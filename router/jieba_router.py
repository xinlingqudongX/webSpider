from fastapi import APIRouter, HTTPException, Request
from util.export_type import AddWordsTag, ExtraStrWordsPayload
import jieba
import jieba.posseg as psg
from typing import List, Dict
from pathlib import Path

router = APIRouter(prefix='/jieba', tags=['jieba'])

@router.post('/extra_words')
async def extra_words(params: ExtraStrWordsPayload):
    items = []
    for item in psg.cut(params.content):
        print(item.flag, item.word)
        if item.flag in params.words_tag:
            items.append(item)

    return items

@router.post('/add_words')
async def add_words(req: Request, params: Dict[str, List[AddWordsTag]]):
    words = params.get('words',[])
    
    dataDir = Path('../data/words')
    filePath = dataDir.joinpath('custom_words.txt')
    with open(filePath, 'a+') as f:
        words_str = map(lambda item:f'{item.word} {item.tag}', words)
        f.writelines(words_str)

    return 1