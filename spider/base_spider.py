from requests import Session, Response, Request
from bs4 import BeautifulSoup
from typing import Any, List, OrderedDict, Tuple, Set, TypedDict, Dict
from requests.adapters import HTTPAdapter
import requests.packages
import re
import asyncio
from asyncio import AbstractEventLoop
from websockets.sync.client import connect
from urllib3.util import Retry
import uuid
import json
from websockets.exceptions import ConnectionClosedError
import logging
try:
    from .spider_type import WsNotifyType
except ImportError as err:
    from spider_type import WsNotifyType

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

class CustomJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, set):
            return list(o)

        return super().default(o)


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

class CustomRequestTask(object):
    '''自定义请求对象类'''

    def __init__(self, **kwargs: Any) -> None:
        self.data = kwargs
    
    def to_json(self):
        return json.dumps(self.data, sort_keys=True)
    
    def __hash__(self) -> int:
        return hash(self.to_json())
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, CustomRequestTask):
            return self.to_json() == __value.to_json()
        
        return False

class BaseSpider(object):

    def __init__(self, custom_header = {}, cookies = {}, ws_config = {}) -> None:
        self.stop_flag: bool = False
        self.pause_flag: bool = False
        self.spider_id = str(uuid.uuid4())
        self.debug = False
        self.__req = Session()
        self.custom_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        self.custom_header.update(custom_header)

        self.loaded_domain = set()
        self.loaded_url = set()
        self.download_links: Set[str] = set()
        self.__retries = Retry(
            total=3,
            status_forcelist=[502,503,504]
        )

        self.__req.mount('https://',HTTPAdapter(max_retries=self.__retries))
        self.__req.mount('http://',HTTPAdapter(max_retries=self.__retries))
        self.__req.headers.update(self.custom_header)
        self.__req.proxies.update({
            'http':'',
            'https': ''
        })
        self.__ws_config:Dict[str, Any] = {
            'uri': 'ws://localhost:8000/v1/ws',
        }
        self.__ws_config.update(ws_config)

        self.__req.verify = False

        try:
            self.__loop = asyncio.get_event_loop()
        except Exception as err:
            self.__loop = asyncio.get_running_loop()

        self.__initConfig()
        for key in cookies:
            self.__req.cookies.set(key, cookies[key])

    def __initConfig(self):
        if hasattr(requests, 'packages'):
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        
        self.__req.hooks['response'].append(self.__ws_hook_res)
    
    def download(self, url: str):
        req = Request("GET", url)
        prepped = req.prepare()

        # res = self.__req.send(prepped)
        res = self.__req.get(url)
        return res
    
    def register_parser(self, parser: BaseParser):
        self.__req.hooks['response'].append(parser)
    
    def __ws_init(self):
        try:
            self.__ws = connect(**self.__ws_config)
            self.__ws.debug = True
        except ConnectionClosedError as err:
            print('ws连接失败')

    def __ws_hook_res(self, *args: Response, **kwargs: ParserKwargs):
        res = args[0]

        spider_data = {key:val for key,val in self.__dict__.items() if not key.startswith('_')}

        notify = {
            'spider_id': self.spider_id,
            'response_url': res.url,
            'notify_type': WsNotifyType.爬虫通知,
            **spider_data
        }

        try:
            logging.debug('爬虫数据:%s', json.dumps(spider_data, cls=CustomJsonEncoder))
            self.__ws.send(json.dumps(notify, cls=CustomJsonEncoder))
        except Exception as err:
            print('发送失败')
            logging.error(err)
    
    def __exit(self):
        print('完成')
        notify = {
            'spider_id': self.spider_id,
            'spider_status': 1,
            'notify_type': WsNotifyType.爬虫状态
        }

        try:
            self.__ws.send(json.dumps(notify, cls=CustomJsonEncoder))
            self.__ws.close()
        except Exception as err:
            print('发送失败')
        # sys.exit()
    
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