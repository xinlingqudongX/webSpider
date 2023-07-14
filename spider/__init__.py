import os
from pathlib import Path
from importlib import import_module

from .base_spider import SpiderManager
from util.model_util import extract_spider

spiderDir = Path(os.getcwd()).joinpath('spider')

def initSpider():
    children = os.listdir(spiderDir)
    filter_children = [item.replace('.py','') for item in children if item.endswith('spider.py')]
    for spider_name in filter_children:
        spider_module = import_module(f"spider.{spider_name}", package=None)
        file_name = spider_name if spider_name.endswith('.py') else spider_name + '.py'
        spider_path = spiderDir.joinpath(file_name)
        classname = extract_spider(str(spider_path))
        if not classname:
            continue

        spiderClass = getattr(spider_module, classname)
        setattr(SpiderManager,classname, spiderClass())