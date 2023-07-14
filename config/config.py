
from dynaconf import Dynaconf
from pydantic import BaseSettings
import logging.config
import json
import os
from datetime import datetime

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

class EnvSettings(BaseSettings):
    pass

    class Config:
        env_file = '.env'


def initConfig():
    '''初始化配置'''
    print('初始化配置', settings)
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    with open(settings['logger']['logger_conf']) as f:
        logging_conf = json.load(f)
        filename = logging_conf['handlers']['file']['filename']
        logging_conf['handlers']['file']['filename'] = f'log/{current_date}_{filename}'
        logging.config.dictConfig(logging_conf)
        
    pass