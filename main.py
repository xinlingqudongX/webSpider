from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from base import netRequest
from http import HTTPStatus
from router import all
from config import config
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('启动服务')
    nowDir = os.getcwd()
    print('当前工作目录:', nowDir)
    config.initConfig()
    yield
    print('结束参数')

app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(all.router, prefix='/v1')

origins = [
    "http://localhost:8080",
    "http://localhost:7071",
    "http://localhost:8000",
    # "http://localhost:8000",
]

app.add_middleware(CORSMiddleware,allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0',port=8000)