from typing import Any, List, Tuple, Dict

from requests import Response
from http import HTTPStatus
from lxml import etree
from lxml.etree import Element
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit
import time
import jieba
import jieba.posseg as psg
from pathlib import Path
import os
import re
from prisma import Prisma
from prisma.models import Peopoe, SpiderTask, SpiderTaskContent
import asyncio
import sys

try:
    from spider.base_spider import BaseParser, BaseSpider
except ModuleNotFoundError as err:
    from .base_spider import BaseParser, BaseSpider


class JianChaParser(BaseParser):
    db: Prisma

    def __init__(self, spider: BaseSpider) -> None:
        super().__init__(spider)
        print(os.getcwd(),'当前目录')
        print(os.getenv('DEBUG'),'变量配置')
    
    async def prismaDB(self):
        if not hasattr(self, 'db'):
            self.db = Prisma(auto_register=True, log_queries=True)
        if not self.db.is_connected():
            await self.db.connect()
        return self.db
        
    
    async def initConfig(self):
        words_model_path = './data/words'
        wordsPath = Path(words_model_path)
        # for wordsPathStr in os.listdir(wordsPath):
        #     if 'words' not in wordsPathStr:
        #         continue
        #     userdictPath = wordsPath.joinpath(wordsPathStr).absolute()
        #     jieba.load_userdict(str(userdictPath))
        
        db = await self.prismaDB()
        print('连接数据库成功')
    
    def checkValid(self, res: Response, content: str) -> bool:
        if res.status_code != HTTPStatus.OK:
            return False

        if 'ccdi.gov.cn' not in res.url:
            return False

        # html = etree.HTML(content, None)
        # put_time = html.xpath('//div[@class="daty_con"]/em[2]/text()')
        # title = html.xpath('//h2[@class="tit"]/text()')
        # data_content = html.xpath('//div[@class="content"]//*/text()')

        # if not put_time or not title or not data_content:
        #     return False

        return True
    
    async def save_data(self, data):
        users = await Peopoe.prisma().create(data=data)
        print(users)
    
    async def create_task(self,data):
        task = await SpiderTaskContent.prisma().upsert(where={
            'link':data['link'],
        }, data={
            'create': data,
            'update': data
        })
        
        print(task)
    
    def extra_data(self, res: Response, content: str):
        html = etree.HTML(content, None)

        put_time: List[str] = html.xpath('//div[@class="daty_con"]/em[2]/text()')
        title:List[str] = html.xpath('//h2[@class="tit"]/text()')
        data_content: List[str] = html.xpath('//div[@class="content"][last()]')

        
        
        self.loop.run_until_complete(self.create_task({
            'title': title[0].strip() if len(title) > 0 else '',
            'content': content,
            'link': res.url,
            'content_suffix':'html',
        }))

        if put_time and put_time[0].strip() and title and title[0].strip() and data_content:
            print('有数据')
            puttime = put_time[0].strip()
            tit = title[0].strip()
            data = ''.join(map(lambda item: etree.tostring(item, encoding='unicode'), data_content))
            data = self.chineseReg.findall(data)
            print(put_time, tit, data)
            # words: Dict[str, int] = {}
            # for cut_data in data:
            #     for item in psg.cut(cut_data):
            #         if item.flag not in ['nr', 'PER']:
            #             continue

            #         print(item.flag, item.word)
            #         if words.get(item.word):
            #             words[item.word] += 1
            #         else:
            #             words.setdefault(item.word, 0)
            
            # sortedWords = sorted(words.items(), key=lambda item: item[1])
            # print(sortedWords)

        pass
    
    def extra_url(self, res: Response, content: str):
        html = etree.HTML(content, None)

        hrefAndsrc = html.xpath('//*[@src or @href]')
        title = html.xpath('//title/text()')

        if len(title) > 0:
            print('网页内容标题:', title[0])
        else:
            pass
        urlObj = urlsplit(res.url)

        ignore_tags = ['img','script','css','link']
        links = set()
        urlPath = '/scdcn/zggb/djcf/'
        for linkTag in hrefAndsrc:
            if linkTag.tag in ignore_tags:
                continue
            
            link = ''
            if linkTag.get('href'):
                link = linkTag.get('href')
            
            if linkTag.get('src'):
                link = linkTag.get('src')
            
            print(link)
            reg = re.compile(r'javascript|#')
            if link.startswith('https://') or link.startswith('http://'):
                links.add(link)
            elif not reg.findall(link):
                link = urljoin(res.url, link)
            else:
                print(link,'未匹配的链接')
                link = ''
            
            if link and urlPath in link:
                self.spider.download_links.add(link)


    def start_parser(self, res: Response, content: str):
        # print(res.url,'解析器打印')
        print('当前链接:', res.url)
        self.extra_data(res, content)
        self.extra_url(res, content)


class JianChaSpider(BaseSpider):

    def __init__(self) -> None:
        super().__init__(custom_header={
            'Host':'www.ccdi.gov.cn',
            'Accept-Encoding': 'identity'
        }, cookies={
            'HBB_HC':'560bfb1edbdfaf2e341276f25ac0047dbd9d2abe04b3c7356ad68e240ce09913e6acb6f19a4e6079def3e96f3240c3d14a',
            'HMF_CI':'14b1da7ff0d7caa9e79b0deacc59d8c8ee03ad875ab37808c4d7b98688964f39bc60bd52af69c1f7e64fc41c244f9dab5f00945fcb5c95ef1bad0e0d72264d470f',
            'HMY_JC':'79debc0b5070854381106771b94a2965c0a682318010560b8ce31e787805f9151b,',
        })
        
        self.register_parser(JianChaParser(self))
    

if __name__ == '__main__':
    jiancha = JianChaSpider()
    # jiancha.start('https://www.ccdi.gov.cn')
    links = []
    for i in range(15):
        if i:
            links.append(f'https://www.ccdi.gov.cn/scdcn/zggb/zjsc/index_{i}.html')
        else:
            links.append(f'https://www.ccdi.gov.cn/scdcn/zggb/zjsc/index.html')
    jiancha.download_links.update(links)
    jiancha.start()