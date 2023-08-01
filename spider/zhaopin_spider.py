try:
    from spider.base_spider import BaseParser, BaseSpider, CustomRequestTask
except ModuleNotFoundError as err:
    from base_spider import BaseParser, BaseSpider, CustomRequestTask

from prisma import Prisma
from requests import Response
from typing import Dict, TypedDict, Any
import time

class ZhaopinParser(BaseParser):
    db: Prisma

    def __init__(self, spider: BaseSpider, debug: bool = False) -> None:
        super().__init__(spider, debug)

    
    async def prismaDB(self):
        if not hasattr(self, 'db'):
            self.db = Prisma(auto_register=True, log_queries=True)
        if not self.db.is_connected():
            await self.db.connect()
        return self.db

    def checkValid(self, res: Response, content: str) -> bool:
        if res.status_code != 200:
            self.logger('错误',content)
            return False
        return True
    
    def parserHotjob(self,res: Response, content: str):
        print('当前链接', res.url)
        data: Dict[str, Any] = res.json()
        page = data.get('page',1)
        pageCount = data.get('pageCount',0)
        total = data.get('rowCount')
        postList = data.get('postList', [])

        if page >= pageCount:
            return
        
        for item in postList:
            postName = item.get('postName','')
            publishDate = item.get('publishDate','')
            serviceCondition = item.get('serviceCondition','')
            workContent = item.get('workContent','')
            workPlace = item.get('workPlace','')
            recruitNum = item.get('recruitNum','')

            self.loop.run_until_complete(self.save_data({
                'company_name': '九州通医药集团股份有限公司',
                'job_title': postName,
                'job_location':workPlace,
                'job_people_number': 1,
                'release_time': publishDate,
                'job_condition': serviceCondition,
                'job_desc': workContent
            }))

        print('当前页数', page)
        url = f'https://www.hotjob.cn/wt/JZT/web/json/position/list?operational=2b67171fce1a9a30df45dd5835483933134592595f42c138fbf3624f9e557908c015b9e645b2665eedc940fa1db7de951d9514c966c898d7&positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page={page + 1}'
        self.spider.download_links.add(url)
        
    def parser36kr(self, res: Response, content: str):
        print('当前链接', res.url)
        resj = res.json()
        code = resj.get('code', 0)
        data = resj.get('data', {})
        pageObj = data.get('page', {})
        projectList = data.get('projectList', [])
        nextPage = pageObj.get('nextPage', 0)
        totalCount = pageObj.get('totalCount', 0)
        pageNo = pageObj.get('pageNo', 0)

        print('下一页数:', nextPage)
        for companyItem in projectList:
            # logoUrl = companyItem.get('logoUrl','')
            self.loop.run_until_complete(self.save_company({
                'company_name': companyItem.get('name', ''),
                'company_website': '',
            }))

        if pageNo != nextPage:
            self.spider.download_links.add(CustomRequestTask(url='https://gateway.36kr.com/api/pms/project/list', method='POST', json={
                'param': {
                    'financingRoundIdList':['8','9','10','11','12','13'],
                    'ifOverseas':'0',
                    'keyword':'',
                    'pageNo':f'{nextPage}',
                    'pageSize':'20',
                    'platformId':2,
                    'siteId':1,
                    'sort':'3',
                    'provinceIdList':['175']
                },
                'partner_id':'web',
                'partner_version': '1.0.0',
                'timestamp': int(time.time() * 1000)
            }))


    def start_parser(self, res: Response, content: str):
        if res.url.find('hotjob.cn') >= 0:
            self.parserHotjob(res, content)
        
        if res.url.find('36kr.com') >= 0:
            self.parser36kr(res, content)

    async def save_data(self, data):
        db = await self.prismaDB()
        
        task = await db.recruitmentjob.upsert(
            where={
                'company_name_job_title':{
                    'company_name': data['company_name'],
                    'job_title': data['job_title']
                }
            }, data={
                'create': data,
                'update': data
            }
        )
        print(task)
    
    async def save_company(self, data):
        db = await self.prismaDB()

        task = await db.recruitment.upsert(
            where={
                'company_name': data['company_name']
            }, data={
                'create': data,
                'update': data
            }
        )

class ZhaopinSpider(BaseSpider):

    def __init__(self) -> None:
        super().__init__()

        self.register_parser(ZhaopinParser(self))

if __name__ == '__main__':
    zhaopin = ZhaopinSpider()

    # zhaopin.download_links.add('https://www.hotjob.cn/wt/JZT/web/json/position/list?operational=2b67171fce1a9a30df45dd5835483933134592595f42c138fbf3624f9e557908c015b9e645b2665eedc940fa1db7de951d9514c966c898d7&positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=1')
    zhaopin.download_links.add(CustomRequestTask(url='https://gateway.36kr.com/api/pms/project/list', method='POST', json={
        'param': {
            'financingRoundIdList':['8','9','10','11','12','13'],
            'ifOverseas':'0',
            'keyword':'',
            'pageNo':'1',
            'pageSize':'20',
            'platformId':2,
            'siteId':1,
            'sort':'3',
            'provinceIdList':['175']
        },
        'partner_id':'web',
        'partner_version': '1.0.0',
        'timestamp': int(time.time() * 1000)
    }))
    zhaopin.start()