from fastapi import APIRouter
from spider.jiancha_spider import JianChaSpider
import jieba

router = APIRouter(tags=['spider'])

@router.get('/start_spider')
async def start_spider():
    jiancha = JianChaSpider()
    jiancha.start('https://www.ccdi.gov.cn/toutiaon/202306/t20230625_271439.html')

    return 1

@router.get('/stop_spider')
async def stop_spider():
    return 1

@router.get('/pause_spider')
async def pause_spider():
    return 1

@router.get('/resume_spider')
async def resume_spider():
    return 1

@router.get('/create_spider')
async def create_spider():
    pass

@router.get('/delete_spider')
async def delete_spider():
    return 1

@router.post('/extra_words')
async def extra_words():
    return 1