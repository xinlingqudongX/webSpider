from fastapi import APIRouter, HTTPException, Request
from util.export_type import ExtraStrWordsPayload
import jieba
import jieba.posseg as psg
from pathlib import Path
import os
from importlib import import_module
from threading import Thread
import logging

from spider.base_spider import SpiderManager
from util.model_util import extract_spider

router = APIRouter(tags=['spider'])
spiderDir = Path(os.getcwd()).joinpath('spider')

@router.get('/start_spider/{spider_name}')
async def start_spider(spider_name: str, start_url: str):
    spider = getattr(SpiderManager,spider_name, None)
    if not spider:
        return '不存在'
    
    spider.download_links.add(start_url)
    thread = Thread(target=spider.start)
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
    spider_names = [item for item in dir(SpiderManager) if not item.startswith('_')]
    spider_items = []
    for name in spider_names:
        spider = getattr(SpiderManager, name)
        if not spider:
            continue
        spider.name = name
        spiderDict = {key:val for key,val in vars(spider).items() if not key.startswith('_')}
        spider_items.append(spiderDict)

    return spider_items

@router.get('/list_module')
async def list_module():
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
    setattr(SpiderManager,classname, spiderClass())
    # spiderClass().start('https://www.ccdi.gov.cn/scdcn/zggb/zjsc/index.html')
    return '加载成功'