from requests import Session, Response
from bs4 import BeautifulSoup
from typing import Any, List, OrderedDict, Tuple, Set, TypedDict, Dict
from requests.adapters import HTTPAdapter
import re
import requests
import asyncio
from asyncio import AbstractEventLoop
import websockets
from websockets.sync.client import connect
from urllib3.util import Retry
import uuid
from json import dumps, loads
from websockets.exceptions import ConnectionClosedError
import sys
from .spider_type import WsNotifyType

class ParserKwargs(TypedDict):
    timeout: int | None
    proxies: OrderedDict
    stream: bool
    verify: bool
    cert: None

class SpiderWsConfig(TypedDict):
    pass

class SpiderWsNotify(object):
    spider_id: str
    response_url: str
    notify_type: WsNotifyType




class BaseParser(object):
    loop: AbstractEventLoop

    def __init__(self, spider: "BaseSpider", debug: bool = False) -> None:
        self.spider = spider
        self.debug = debug
        self.chineseReg = re.compile(r'([\u4e00-\u9fa5、，。’‘“”；《》]+)')
        self.accept_suffix = [
            'html',
        ]
        self.limit_domain: Set[str] = set()
        
        try:
            self.loop = asyncio.get_event_loop()
        except Exception as err:
            self.loop = asyncio.get_running_loop()
    
    def logger(self, *args):
        if self.debug:
            print(*args)

    def checkValid(self,res: Response, content: str) -> bool:
        return True
    
    def decode_content(self, content:bytes) -> Tuple[str | None, str | None]:
        '''检查编码格式'''
        charsets = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
        charset = None
        data = None
        for c in charsets:
            try:
                data = content.decode(c)
                charset = c
                break
            except:
                continue
        if charset:
            return charset, data
        return charset, data

    def start_parser(self, res: Response, content: str):
        pass

    def __call__(self, *args: Response, **kwargs: ParserKwargs) -> Any:
        self.logger(args,'解析器参数')
        self.logger(kwargs, '解析器参数')

        res = args[0]
        charset, content = self.decode_content(res.content)
        if content and self.checkValid(args[0], content):
            self.start_parser(args[0], content)


class BaseSpider(object):

    spider_id = str(uuid.uuid4())
    stop_flag: bool = False
    pause_flag: bool = False

    def __init__(self, custom_header = {}, cookies = {}, ws_config = {}) -> None:
        self.req = Session()
        self.custom_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        self.custom_header.update(custom_header)

        self.loaded_domain = set()
        self.loaded_url = set()
        self.download_links: Set[str] = set()
        self.retries = Retry(
            total=3,
            status_forcelist=[502,503,504]
        )

        self.req.mount('https://',HTTPAdapter(max_retries=self.retries))
        self.req.mount('http://',HTTPAdapter(max_retries=self.retries))
        self.req.headers.update(self.custom_header)
        self.req.proxies.update({
            'http':'',
            'https': ''
        })
        self.ws_config:Dict[str, Any] = {
            'uri': 'ws://localhost:8000/v1/ws',
        }
        self.ws_config.update(ws_config)

        self.req.verify = False

        self.loop = asyncio.get_event_loop()

        self.__initConfig()
        for key in cookies:
            self.req.cookies.set(key, cookies[key])

    def __initConfig(self):
        if hasattr(requests, 'packages'):
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        
        self.req.hooks['response'].append(self.__ws_hook_res)
    
    def download(self, url: str):
        res = self.req.get(url)
        return res
    
    def register_parser(self, parser: BaseParser):
        self.req.hooks['response'].append(parser)
    
    def __ws_init(self):
        try:
            self.ws = connect(**self.ws_config)
            self.ws.debug = True
        except ConnectionClosedError as err:
            print('ws连接失败')

    def __ws_hook_res(self, *args: Response, **kwargs: ParserKwargs):
        res = args[0]
        notify = {
            'spider_id': self.spider_id,
            'response_url': res.url,
            'notify_type': WsNotifyType.爬虫通知
        }

        try:
            self.ws.send(dumps(notify))
        except Exception as err:
            print('发送失败')
    
    def __exit(self):
        print('完成')
        notify = {
            'spider_id': self.spider_id,
            'spider_status': 1,
            'notify_type': WsNotifyType.爬虫状态
        }

        try:
            self.ws.send(dumps(notify))
            self.ws.close()
        except Exception as err:
            print('发送失败')
        sys.exit()
    
    def get_data(self):
        pass
    
    def start(self):
        '''启动爬虫'''

        # 开始连接ws
        self.__ws_init()

        while True:
            if self.pause_flag:
                continue
            
            if self.stop_flag:
                break
    
            if len(self.download_links):
                url = self.download_links.pop()
                res = self.download(url)
                # print(res)
            else:
                break
        

        self.__exit()

class SpiderManager(object):
    '''管理对象'''

    def __setattr__(self, __name: str, __value: Any) -> None:
        object.__setattr__(self, __name, __value)