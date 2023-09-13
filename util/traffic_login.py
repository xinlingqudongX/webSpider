import requests
import re
from time import time, sleep
from urllib.parse import urlencode
from typing import TypedDict, List
import cv2
import base64
import numpy as np

class QrcodeRes(TypedDict):
    loginUrl: str
    qr: str
    lp: str
    code: int
    result: str
    desc: str
    description: str

class QrImgRes(TypedDict):
    img: str
    code: str
    token: str

class QrCheckRes(TypedDict):
    msg: str
    code: str
    url: str


class TrafficManagement(object):

    def __init__(self) -> None:
        self.qr_url = 'https://gab.122.gov.cn/eapp/qrCode/queryQRCode?token={token}'
        self.qr_img = 'https://gab.122.gov.cn/eapp/qrCode/loginQrCodeImg'
        self.headers = {
            'Cookie':'deviceId=wb_6b023837-1c01-4774-9be2-1569d8650538; pass_ua=web; uLocale=zh_CN; passInfo=login-end',
            'Host':'account.xiaomi.com',
        }
        self.req = requests.Session()
        self.token = ''
        self.img = ''

        self.check_codes:List[str] = ['400','201']
        self.check_seconds = 2
    
    def decodeBase64Img(self, base64Img: str):
        img_data = base64.b64decode(base64Img)
        np_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img

    def qrcode_login(self):
        '''二维码登录'''

        res = self.req.post(self.qr_img)
        resj: QrImgRes = res.json()
        self.img = resj.get('img')
        self.token = resj.get('token')

        img = self.decodeBase64Img(self.img)
        cv2.imshow('qrcode', img)
        cv2.waitKey(0)


        while True:
            loginUrl = self.qrcode_check(self.token)
            if loginUrl:
                cv2.destroyAllWindows()
                self.req.get(loginUrl)
                break
            sleep(self.check_seconds)
        
    
    def qrcode_check(self, token: str) -> str | None:
        '''二维码检查'''
        res = self.req.post(self.qr_url.format(token=token))
        resj: QrCheckRes = res.json()
        print(resj)

        if resj.get('code') != '200':
            return
        return resj.get('url')

if __name__ == '__main__':
    trffic = TrafficManagement()
    trffic.qrcode_login()
