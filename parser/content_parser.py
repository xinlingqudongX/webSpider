import jieba
import os
from pathlib import Path
from requests import Response
from lxml import etree



class SpiderParser(object):
    isSync: bool = False

    def __init__(self) -> None:
        self.init()
    
    def init(self):
        pass

    def checkValid(self, res: Response) -> bool:
        return False
    
    def callback(self, response: Response, content: str):
        pass



class JiweiParser(SpiderParser):

    def __init__(self) -> None:
        super().__init__()
        self.isSync = False
    
    def init(self):
        self.load_words()
    
    def load_words(self):
        words_model = './model'
        wordsPath = Path(words_model)
        if not wordsPath.exists():
            print('词性目录不存在')
            return
        
        for wordsPathStr in os.listdir(words_model):
            if 'words' not in wordsPathStr:
                continue
            userdictPath = wordsPath.joinpath(wordsPathStr).absolute()
            jieba.load_userdict(str(userdictPath))
    
    def addData(self):
        pass
    
    def checkValid(self, res: Response) -> bool:
        if 'ccdi.gov.cn' in res.url:
            return True
        return False

    def callback(self, response: Response, content: str):
        html = etree.parse(content, None)

        put_time = html.xpath('//div[@class="daty_con"]/em[2]/text()')
        title = html.xpath('//h2[@class="tit"]/text()')
        data_content = html.xpath('//div[@class="content"]//*/text()')

        print(put_time, title)


if __name__ == '__main__':
    jiwei = JiweiParser({})
    