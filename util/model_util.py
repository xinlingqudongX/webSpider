from pathlib import Path
import os
import jieba

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
    