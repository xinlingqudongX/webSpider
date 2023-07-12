from fastapi import APIRouter, HTTPException, Request
from util.export_type import ExtraStrWordsPayload
import jieba
import jieba.posseg as psg
from pathlib import Path
import os
from importlib import import_module
from threading import Thread

from spider.base_spider import SpiderManager
from util.model_util import extract_spider

router = APIRouter(tags=['spider'])
spiderDir = Path(os.getcwd()).joinpath('spider')

@router.get('/start_spider/{spider_name}')
async def start_spider(spider_name: str):
    spider = getattr(SpiderManager,spider_name, None)
    if not spider:
        return '不存在'
    thread = Thread(target=spider().start)
    thread.start()
    return '成功'

@router.get('/stop_spider/{spider_id}')
async def stop_spider(spider_id: int):
    return 1

@router.get('/pause_spider/{spider_id}')
async def pause_spider(spider_id: int):
    return 1

@router.get('/resume_spider/{spider_id}')
async def resume_spider(spider_id: int):
    return 1

@router.get('/create_spider')
async def create_spider():
    pass

@router.get('/delete_spider/{spider_id}')
async def delete_spider(spider_id: int):
    return 1

@router.post('/create_script')
async def create_script():
    return 1

@router.get('/list_spider')
async def list_spider():
    baseDir = os.getcwd()
    # spiderDir = 'spider'
    # print(os.getcwd())
    spider_names = [item for item in dir(SpiderManager) if not item.startswith('_')]
    return spider_names

@router.get('/list_module')
async def list_module():
    baseDir = os.getcwd()
    # spiderDir = 'spider'
    # print(os.getcwd())
    children = os.listdir(spiderDir)
    filter_children = [item.replace('.py','') for item in children if item.endswith('spider.py')]
    return filter_children

@router.get('/load_spider/{spider_name}')
async def load_spider(req: Request, spider_name: str):
    spider_module = import_module(f"spider.{spider_name}", package=None)
    file_name = spider_name if spider_name.endswith('.py') else spider_name + '.py'
    spider_path = spiderDir.joinpath(file_name)
    classname = extract_spider(str(spider_path))
    if not classname:
        return '加载失败'
    
    spiderClass = getattr(spider_module, classname)
    setattr(SpiderManager,classname, spiderClass)
    # spiderClass().start('https://www.ccdi.gov.cn/scdcn/zggb/zjsc/index.html')
    return '加载成功'