from requests import Session, Response
from bs4 import BeautifulSoup
from typing import Any, List, OrderedDict, Tuple, Set, TypedDict
from requests.adapters import HTTPAdapter
import re
import requests

class ParserKwargs(TypedDict):
    timeout: int | None
    proxies: OrderedDict
    stream: bool
    verify: bool
    cert: None

class BaseParser(object):

    def __init__(self, spider: "BaseSpider", debug: bool = False) -> None:
        self.spider = spider
        self.debug = debug
        self.chineseReg = re.compile(r'([\u4e00-\u9fa5、，。’‘“”；《》]+)')
        self.accept_suffix = [
            'html',
        ]
    
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

    def __call__(self, *args: Tuple[Response], **kwargs: ParserKwargs) -> Any:
        self.logger(args,'解析器参数')
        self.logger(kwargs, '解析器参数')

        if len(args) > 0 and isinstance(args[0], Response):
            res = args[0]
            charset, content = self.decode_content(res.content)
            if content and self.checkValid(args[0], content):
                self.start_parser(args[0], content)


class BaseSpider(object):

    def __init__(self, custom_header = {}, cookies = {}) -> None:
        self.req = Session()
        self.custom_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        self.custom_header.update(custom_header)

        self.retry_times = 3
        self.loaded_domain = set()
        self.loaded_url = set()
        self.download_links: Set[str] = set()

        self.req.mount('https://',HTTPAdapter(max_retries=self.retry_times))
        self.req.mount('http://',HTTPAdapter(max_retries=self.retry_times))
        self.req.headers.update(self.custom_header)
        self.req.proxies.update({
            'http':'',
            'https': ''
        })
        self.req.verify = False

        self.__initConfig()
        for key in cookies:
            self.req.cookies.set(key, cookies[key])

    def __initConfig(self):
        if hasattr(requests, 'packages'):
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    
    def download(self, url: str):
        res = self.req.get(url)
        return res
    
    def register_parser(self, parser: BaseParser):
        self.req.hooks['response'].append(parser)
    
    def get_data(self):
        pass
    
    def start(self, start_url: str):
        pass
