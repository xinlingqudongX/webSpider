from multiprocessing.context import BaseContext
from requests import Session, Response
import re
from json import loads, dumps
import multiprocessing
from multiprocessing import Process, Manager, Value, Array
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.managers import BaseManager
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Tuple, TypedDict, Set, Any
from bs4 import BeautifulSoup
import time
import socket
import asyncio
from websockets.sync.client import connect
from peewee import DateTimeField, CharField, BooleanField, TextField, Model, SqliteDatabase
from spider_web.parser.content_parser import SpiderParser, JiweiParser
from threading import Thread

# 当前目录
nowDir = Path(__file__).parent
print('当前目录',nowDir)

# localWs = connect('ws://localhost:8000/ws')

db = SqliteDatabase(nowDir.joinpath('..','time_spectrum.db'))

class Task(Model): 
    created_at = DateTimeField() 
    updated_at = DateTimeField() 
    link = CharField() 
    domain = CharField() 
    is_completed = BooleanField() 
    page_data = TextField() 
    
    class Meta: 
        database = db


class SharedData(object):
    '''共享数据类'''

    download_links_obj:Dict[str,Set[str]] = {}
    '''下载对象'''
    downloaded_domain:Set[str] = set()
    '''已下载域名'''
    downloaded_links: Set[str] = set()
    '''已下载链接'''
    # links_domain:Set[str] = set()
    # '''要下载的域名'''
    download_links:Set[str] = set()

    parser_list = []

    def setDownload_links_obj(self,key:str,val):
        self.download_links_obj.setdefault(key,val)
    
    def getDownload_links_obj(self,key:str):
        return self.download_links_obj.get(key)
    
    def keysDownload_links_obj(self):
        return self.download_links_obj.keys()

    def InDownloaded_links(self,key:str):
        return key in self.downloaded_links
    
    def InDownloaded_domain(self,domain:str):
        return domain in self.downloaded_domain

    def LenDownload_links_obj(self) -> int:
        return len(self.download_links_obj)

    def AddDownload_domain(self,domain:str):
        self.downloaded_domain.add(domain)
    
    def AddDownloaded_links(self,link:str):
        self.downloaded_links.add(link)
    
    def GetDownloadLinks(self):
        return self.download_links
    
    def GetParserList(self):
        return self.parser_list
    
    def RegisterParser(self, parser: SpiderParser):
        self.parser_list.append(parser)

class SharedDataManage(BaseManager):pass

class SpiderDataset(object):

    @staticmethod
    def getNextTask():
        task = Task.get({
            "is_completed": False
        })
        return task
    
    @staticmethod
    def addTask(taskInfo):
        createRes = Task.create(**taskInfo)
    

class SpiderConfig(TypedDict):
    threads: int
    '''线程数量'''
    process: int
    '''进程数量'''
    parser_list: List[SpiderParser]




class DbDataSet(object):

    def __init__(self) -> None:
        pass

class DownloadSpider(object):
    '''下载器'''
    spider_config: SpiderConfig = {
        'threads': 1,
        'process': 2,
        'parser_list': [],
    }

    download_threads = 4
    '''下载线程'''
    '''要下载的链接'''
    exclude_suffix = ['jpg','png','web','js','css']
    '''不下载的后缀'''
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept-Encoding': 'identity'
    }
    proxy = {
        'http':'',
        'https':'',
    }
    threads_list:List[Process] = []
    white_domain = ['ccdi.gov.cn']
    '''域名白名单'''
    sharedData: SharedData

    parser_list = []


    def __init__(self, startUrl:str, threads=None) -> None:
        self.download_threads = multiprocessing.cpu_count()
        if threads:
            self.download_threads = threads
        self.req = Session()
        self.urlReg = re.compile(r'(https?://\S+)')
        self.nowUrl = ''
        self.nowDomain = ''
        self.verifyUrl = False
        self.timeout = 10
        self.err_status = [500,403]
        self.extraTags = ['a','iframe']
        self.startUrl = startUrl
        self.chineseReg = re.compile(r'([\u4e00-\u9fa5]+)')
    
    def initSocket(self):
        pass
    
    def registerParser(self, parser: SpiderParser):
        self.parser_list.append(parser)

    def checkValidUrl(self,url:str) -> bool:
        '''检查是否是网络链接'''
        result = self.urlReg.findall(url)
        if not result:
            return False
        return True
    
    def checkCharset(self, content:bytes):
        '''检查编码格式'''
        charsets = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
        charset = None
        for c in charsets:
            try:
                content.decode(c)
                charset = c
                break
            except:
                continue
        return charset
    
    def generateHeader(self,params:Dict):
        return {**self.header, **params}
    
    def download(self, downloadUrl: str):
        '''下载'''
        if not self.checkValidUrl(downloadUrl):
            print('不符合格式的链接', downloadUrl)
            return
        
        urlData = urlparse(downloadUrl)
        if not urlData.hostname:
            print('不符合格式的链接', downloadUrl)
            return

        if self.sharedData.InDownloaded_links(downloadUrl):
            return
        

        self.nowUrl = downloadUrl
        self.nowDomain = urlData.hostname

        self.sharedData.AddDownload_domain(urlData.hostname)
        self.sharedData.AddDownloaded_links(downloadUrl)

        try:
            header = self.generateHeader({
                'Host':self.nowDomain,
            })
            res: Response = self.req.get(downloadUrl, verify=self.verifyUrl,timeout=self.timeout, headers=header, proxies=self.proxy)
        except Exception as err:
            print(downloadUrl,err)
            return

        if res.status_code in self.err_status:
            print(downloadUrl, res.status_code, '请求状态错误')

            return
        print('正在请求：',downloadUrl)

        charset = self.checkCharset(res.content)
        if not charset:
            print('未识别的编码',downloadUrl)
            return
        
        try:
            htmlContent = res.content.decode(charset)
        except Exception as err:
            print('解码失败',err)
            return
        
        # self.links_domain.add(urlData.hostname)
        linkUrls = self.extraUrl(downloadUrl, htmlContent)

        for link in linkUrls:
            subUrlData = urlparse(link)
            if not subUrlData.hostname:
                continue
            
            if not self.sharedData.InDownloaded_domain(subUrlData.hostname):
                downloadSet = self.sharedData.getDownload_links_obj(subUrlData.hostname)
                if downloadSet:
                    downloadSet.add(link)
                else:
                    self.sharedData.setDownload_links_obj(subUrlData.hostname,set([link]))
            else:
                downloadSet = self.sharedData.getDownload_links_obj(subUrlData.hostname)
                if not downloadSet is None:
                    downloadSet.add(link)
        parser_list = self.sharedData.GetParserList()
        for parseTask in parser_list:
            self.runParserTask(parseTask,res, htmlContent)

    
    def extraUrl(self,downloadUrl: str, content:str) -> List[str]:
        '''提取网络链接'''
        urlData = urlparse(downloadUrl)
        domain = f'{urlData.scheme}://{urlData.hostname}'
        protocol = urlData.scheme

        links = set()
        if not urlData.hostname:
            return list(links)

        html = BeautifulSoup(content, 'html.parser')
        titleTag = html.find('title')
        htmlTitle = ''
        if titleTag and titleTag.text:
            print(titleTag.text)
            title = re.findall(self.chineseReg,titleTag.text.strip())
            if title:
                htmlTitle = title[0]
            else:
                htmlTitle = titleTag.text.strip()
        if not urlData.path:
            self.upload(urlData.hostname, htmlTitle)


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
                extraUrl = urljoin(downloadUrl, extraUrl)
            elif extraUrl.startswith('http://') or extraUrl.startswith('https://'):
                urlData = urlparse(extraUrl)
                if not any(map(lambda domain:urlData.hostname and urlData.hostname.endswith(domain), self.white_domain)):
                    continue
            else:
                print('未知格式',extraUrl)
                continue
            if Path(extraUrl).suffix.strip('.') in self.exclude_suffix:
                continue

            links.add(extraUrl)
        
        return list(links)

    def startDownload(self,startUrl:str,sharedData:SharedData):
        self.sharedData = sharedData

        print(self.sharedData.GetDownloadLinks())

        urlData = urlparse(startUrl)
        if not self.checkValidUrl(startUrl) or not urlData.hostname:
            raise Exception('不符合格式的链接')
        
        if self.sharedData.LenDownload_links_obj() <= 0:
            self.sharedData.setDownload_links_obj(urlData.hostname,set([startUrl]))
            # self.download_links.add(startUrl)
        
        while self.sharedData.LenDownload_links_obj() > 0:
            domains = list(self.sharedData.keysDownload_links_obj())
            nextDownloadDomain = ''

            for downloadDomain in domains:
                if not self.sharedData.InDownloaded_domain(downloadDomain):
                    nextDownloadDomain = downloadDomain
                    break
            if not nextDownloadDomain:
                print('没有要下载的域名了')
                break

            downloadSet = self.sharedData.getDownload_links_obj(nextDownloadDomain)
            if downloadSet is None:
                downloadSet = set()
            # self.download_links = downloadSet

            while len(downloadSet) > 0:
                downloadUrl = downloadSet.pop()
                self.download(downloadUrl)
                # localWs.send(downloadUrl)
                time.sleep(0.4)

        print('下载结束')
    
    def startThread(self, wait:bool = True):
        SharedDataManage.register('SharedData', SharedData)
        manager = SharedDataManage()
        manager.start()
        shardData = manager.SharedData()

        while len(self.threads_list) < self.download_threads:
            for cpu in range(self.download_threads - len(self.threads_list)):
                threads = multiprocessing.Process(target=self.startDownload, args=[self.startUrl, shardData])
                self.threads_list.append(threads)
                threads.daemon = True
                threads.start()
                # threads.join()
                time.sleep(10)
                print(f'启动{cpu}进程')
            
            if wait:
                for threads in self.threads_list:
                    threads.join()
            
            for index, threads in enumerate(self.threads_list):
                if not threads.is_alive():
                    self.threads_list.pop(index)
    
    def loadBackup(self):
        pass

    def saveBackup(self):
        # with open(check_file,'w',encoding='utf8') as f:
        # f.write('\n'.join(list(check_set)))
        # with open(download_file,'w',encoding='utf8') as f:
        #     f.write('\n'.join(list(download_set)))
        # with open(domain_file,'w',encoding='utf8') as f:
        #     f.write('\n'.join(list(domain_set)))
        # with open(domain_json,'w',encoding='utf8') as f:
        #     f.write(dumps(domain_obj))
        pass

    def upload(self,domain:str, title = ''):
        # self.req.post('http://localhost:7001/web/add_department',json={'department_name':title,'department_website':domain})
        pass

    def runParserTask(self, parserTask: SpiderParser, res: Response, content: str):
        if not parserTask.checkValid(res):
            return
        if parserTask.isSync:
            task = Thread(target=parserTask.callback, args=[res, content])
            task.start()
        else:
            parserTask.callback(res, content)

if __name__ == '__main__':
    # spider = DownloadSpider('https://www.gov.cn')
    spider = DownloadSpider('https://www.ccdi.gov.cn/')
    # spider.download_threads = 30
    spider.download_threads = 2
    # spider.download_threads = 10
    jiParse = JiweiParser()
    spider.registerParser(jiParse)
    spider.startThread()
