import requests
import re
from time import time
from urllib.parse import urlencode
from typing import TypedDict

class QrcodeRes(TypedDict):
    loginUrl: str
    qr: str
    lp: str
    code: int
    result: str
    desc: str
    description: str


class Mi(object):

    def __init__(self) -> None:
        self.qr_url = 'https://account.xiaomi.com/longPolling/loginUrl'
        self.headers = {
            'Cookie':'deviceId=wb_6b023837-1c01-4774-9be2-1569d8650538; pass_ua=web; uLocale=zh_CN; passInfo=login-end',
            'Host':'account.xiaomi.com',
        }
        self.req = requests.Session()

    def qrcode_login(self):
        '''二维码登录'''
        data = {
            '_group':'DEFAULT',
            '_qrsize': 240,
            'qs':'',
            'bizDeviceType':'',
            'callback':'',
            'sid':'i.mi.com',
            '_snsNone':'true',
            'needTheme':'false',
            'showActiveX':'false',
            'serviceParam':'{"checkSafePhone":false,"checkSafeAddress":false,"lsrp_score":0.0}',
            '_locale':'zh_CN',
            '_sign':'',
            '_dc': int(time() * 1000)
        }

        res = self.req.get(self.qr_url, params=data)
        print(res)
    
    def qrcode_check(self, link:str):
        '''二维码检查'''
        res = self.req.options(link)
        print(res)

if __name__ == '__name__':
    mi = Mi()
    mi.qrcode_login()
