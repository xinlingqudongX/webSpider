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
    
    packagePath = site.getsitepackages()[1]
    jiebaDictPath = Path(packagePath).joinpath('jieba','vdict.txt')
    with open(jiebaDictPath, 'a', encoding='utf-8') as f:
        for wordsPathStr in os.listdir(dirPaths):
            if 'words' not in wordsPathStr:
                continue

            userdictPath = dirPaths.joinpath(wordsPathStr).absolute()
            # jieba.load_userdict(str(userdictPath))
            try:
                with open(userdictPath, encoding='utf-8') as userfile:
                    userlines = userfile.readlines()

                for line in userlines:
                    splitline = line.split(' ')
                    splitline.insert(1, '3')
                    newline = ' '.join(splitline)
                    print(newline)
                    f.write(newline)
            except Exception as err:
                pass

    
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