
from dynaconf import Dynaconf
from pydantic import BaseSettings

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
    pass