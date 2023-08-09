try:
    from spider.base_spider import BaseParser, BaseSpider, CustomRequestTask
except ModuleNotFoundError as err:
    from base_spider import BaseParser, BaseSpider, CustomRequestTask

from datetime import datetime
from prisma import Prisma
from requests import Response
from typing import Dict, TypedDict, Any
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from pathlib import Path
import re

class MechanismParser(BaseParser):
    db: Prisma

    def __init__(self, spider: BaseSpider, debug: bool = False) -> None:
        super().__init__(spider, debug)

        self.exclude_suffix = ['jpg','png','web','js','css']
        '''不下载的后缀'''
        self.extraTags = ['a','iframe']
        '''要提取的元素名'''

    
    async def prismaDB(self):
        if not hasattr(self, 'db'):
            self.db = Prisma(auto_register=True, log_queries=True)
        if not self.db.is_connected():
            await self.db.connect()
        return self.db
    
    def checkValid(self, res: Response, content: str) -> bool:
        if res.status_code != 200:
            self.logger('错误',content)
            return False
        urlData = urlparse(res.url)
        if urlData.hostname and ('gov.cn' not in urlData.hostname):
            return False
        return True
    
    def start_parser(self, res: Response, content: str):
        self.extraUrls(res, content)
        self.save_data(res, content)

    def extraUrls(self, res: Response, content: str):
        '''提取网络链接'''
        urlData = urlparse(res.url)
        domain = f'{urlData.scheme}://{urlData.hostname}'
        protocol = urlData.scheme

        links = set()
        html = BeautifulSoup(content, 'html.parser')
        linkTags = html.findAll(self.extraTags)
        for link in linkTags:
            extraUrl: str = ''
            if link.has_attr('href'):
                extraUrl = link.get('href').strip()

            if link.has_attr('src'):
                extraUrl = link.get('src').strip()
            
            if not extraUrl:
                continue

            if extraUrl.startswith('/'):
                extraUrl = urljoin(domain,extraUrl)
            elif extraUrl.startswith('//'):
                extraUrl = f'{protocol}:{extraUrl}'
            elif extraUrl.startswith('.') or extraUrl.startswith('..'):
                extraUrl = urljoin(res.url, extraUrl)
            elif extraUrl.startswith('http://') or extraUrl.startswith('https'):
                pass
            else:
                # print('未知格式',extraUrl)
                continue
            if Path(extraUrl).suffix.strip('.') in self.exclude_suffix:
                continue

            links.add(extraUrl)
        
        self.spider.download_links.update(links)

    def save_data(self,res: Response, content: str):
        urlData = urlparse(res.url)
        if urlData.path.strip('/'):
            return
        
        print('当前网址:', res.url)
        titles = re.findall(r'<title>(.*?)</title>', content, re.S | re.I)
        print('标题:',titles)
        print('请求时间:',datetime.now())

class MechanismSpider(BaseSpider):

    def __init__(self) -> None:
        super().__init__()

        self.register_parser(MechanismParser(self))
    
if __name__ == '__main__':
    mechanism = MechanismSpider()
    mechanism.download_links.add('https://www.gov.cn/')
    mechanism.start()