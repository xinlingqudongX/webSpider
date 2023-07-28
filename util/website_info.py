import requests
from requests import Session
from time import time
import random
import re
from paddleocr import PaddleOCR

class WebsiteUtil(Session):
    token: str

    def __init__(self) -> None:
        super().__init__()
        self.token = ''
        self.ocr = PaddleOCR(use_angle_cls=True)
        if not self.token:
            self.token = self.extraToken()
    
    def extraToken(self):
        url = 'https://www.beian.gov.cn/portal/registerSystemInfo'
        payload = {
            'method':'GET',
            'url': url,
            'data':{},
        }

        res = self.request(**payload)
        txt = res.text
        token = re.findall(r"taken_for_user\s?=\s?'(.*?)'", txt)
        if len(token) < 1:
            raise Exception('未获取到token')
        return token[0]

    def queryWebsiteName(self,website_name: str):
        url = 'https://www.beian.gov.cn/portal/registerSystemInfo'
        payload = {
            'method':'POST',
            'url': url,
            'data': {
                'token': self.token,
                'sdcx': 1,
                'flag': 3,
                'websitesname': website_name,
                'inputPassword': self.identifyCode(),
            }
        }
        res = self.request(**payload)
        print(res)

    def queryWebsite(self, website: str):
        url = 'https://www.beian.gov.cn/portal/registerSystemInfo'
        payload = {
            'method':'POST',
            'url': url,
            'data': {
                'token': self.token,
                'sdcx': 1,
                'flag': 3,
                'domainname': website,
                'inputPassword': self.identifyCode(),
            }
        }
        res = self.request(**payload)
        print(res)

    def queryWebsiteInfo(self,info: str):
        url = 'https://www.beian.gov.cn/portal/registerSystemInfo'
        payload = {
            'method':'POST',
            'url': url,
            'data': {
                'token': self.token,
                'sdcx': 1,
                'flag': 3,
                'recordcode': info,
                'inputPassword': self.identifyCode(),
            }
        }
        res = self.request(**payload)
        print(res)

    def checkValidCode(self,code: str):
        url = 'https://www.beian.gov.cn/portal/verCode?t=3&code=1432'
        payload = {
            'method': 'POST',
            'url': url,
            'params': {
                't': random.randint(1,5),
                'code': code
            }
        }
        res = self.request(**payload)
    
    def identifyCode(self) -> str:
        url = 'https://www.beian.gov.cn/common/image.jsp?t=3&tim=1690530357377'
        payload = {
            'method': 'GET',
            'url': url,
            'params': {
                't': 3,
                'tim': int(time() * 1000)
            }
        }
        res = self.request(**payload)
        #   识别
        data = self.ocr.ocr(res.content)
        print(data)
        return ''

    def queryICP(self,website_name: str):
        url = ''

if __name__ == '__main__':
    util = WebsiteUtil()
    util.identifyCode()

