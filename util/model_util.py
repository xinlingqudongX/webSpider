from pathlib import Path
import os
import jieba
import re
import site

def jieba_load_words(dirPath: str) -> bool:
    dirPaths = Path(dirPath)
    if not dirPaths.exists():
        print('文件目录不存在')
        return False
    
    dict_set = set()
    for wordsPathStr in os.listdir(dirPaths):
        if 'words' not in wordsPathStr:
            continue

        userdictPath = dirPaths.joinpath(wordsPathStr).absolute()
        # jieba.load_userdict(str(userdictPath))
        with open(userdictPath, encoding='utf-8') as f:
            data = f.read()
            dict_set.update(data.split('\n'))
        
        print(len(dict_set))
    # with open('udict.txt','w', encoding='utf-8') as f:
    #     f.write('\n'.join(dict_set))
    
    return True

def extract_spider(filepath: str) -> str | None:
    path = Path(filepath)
    if not path.exists():
        return
    
    with open(path, encoding='utf8') as f:
        data = f.read()
    
    names = re.findall(r' (.*?)\(BaseSpider\):', data)
    spider_name = names[0] if len(names) > 0 else None
    return spider_name