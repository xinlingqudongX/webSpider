from enum import Enum, IntEnum
from pydantic import BaseModel
from typing import Union, List, Tuple

class WordsTag(str, Enum):
    '''词性标注'''
    普通名词 = "n"
    方位名词 = "f"
    处所名词 = "s"
    时间 = "t"
    人名 = "nr"
    地名 = "ns"
    机构名 = "nt"
    作品名 = "nw"
    其他专名 = "nz"
    普通动词 = "v"
    动副词 = "vd"
    名动词 = "vn"
    形容词 = "a"
    副形词 = "ad"
    名形词 = "an"
    副词 = "d"
    数量词 = "m"
    量词 = "q"
    代词 = "r"
    介词 = "p"
    连词 = "c"
    助词 = "u"
    其他虚词 = "xc"
    标点符号 = "w"

class ExtraStrWordsPayload(BaseModel):
    content: str
    words_tag: List[WordsTag]

class AddWordsTag(BaseModel):
    word: str
    tag: str

class AllException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)