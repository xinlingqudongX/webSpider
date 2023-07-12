from pathlib import Path
import os
import jieba
import re

def jieba_load_words(dirPath: str) -> bool:
    dirPaths = Path(dirPath)
    if not dirPaths.exists():
        print('文件目录不存在')
        return False
    
    for wordsPathStr in os.listdir(dirPaths):
        if 'words' not in wordsPathStr:
            continue

        userdictPath = dirPaths.joinpath(wordsPathStr).absolute()
        jieba.load_userdict(str(userdictPath))
    
    return True

def extract_spider(filepath: str):
    path = Path(filepath)
    if not path.exists():
        return
    
    with open(path, encoding='utf8') as f:
        data = f.read()
    
    names = re.findall(r' (.*?)\(BaseSpider\):', data)
    spider_name = names[0]
    return spider_name