from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from base import netRequest
from http import HTTPStatus
import os

from router import all
from pathlib import Path
from config import config
from spider import initSpider

from util.export_type import AllException
from util.model_util import jieba_load_words

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('启动服务')
    nowDir = os.getcwd()
    print('当前工作目录:', nowDir)
    print(f'启动:{app.title} 版本:{app.version}')
    config.initConfig()
    # print('正在导入jieba自定义分词')
    # jieba_load_words(str(Path(nowDir).joinpath('data','words')))
    print(app.docs_url)
    print(app.redoc_url)
    initSpider()
    yield
    print('结束参数')

app = FastAPI(
    title='初始化项目',
    description='初始化项目介绍',
    smmary='介绍',
    version='0.0.1',
    terms_of_service='',
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    debug=True, 
    lifespan=lifespan
)

app.include_router(all.router, prefix='/v1')

origins = [
    "http://localhost:8080",
    "http://localhost:7071",
    "http://localhost:8000",
    # "http://localhost:8000",
]

app.add_middleware(CORSMiddleware,allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.exception_handler(AllException)
async def all_exception_handler(request: Request, exc):
    return 1

app.mount('/public', StaticFiles(directory='public'), name='public')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0',port=8000, workers=2)