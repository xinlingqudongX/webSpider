from fastapi import APIRouter, HTTPException
from util.export_type import ExtraStrWordsPayload
import jieba
import jieba.posseg as psg
from pathlib import Path
import os

router = APIRouter(tags=['spider'])

@router.get('/start_spider')
async def start_spider():

    return 1

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
    children = os.listdir(Path(baseDir).joinpath('spider'))
    return children