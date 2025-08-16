from envyaml import EnvYAML
from pydantic import AnyUrl, BaseModel, ConfigDict
from . import constants


class BaseConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class DbConfig(BaseConfig):
    echo: bool = False
    url: AnyUrl


class Config(BaseConfig):
    db: DbConfig


class ConfigProxy:
    
    def __init__(self):
        self._config = None
    
    def __getattr__(self, name):
        if self._config is None:
            raise Exception('Configuration must be loaded')
        return getattr(self._config, name)
    
    def load(self):
        env = EnvYAML(constants.CONFIG_PATH, flatten=False)
        self._config = Config.model_validate(env.export())


config = ConfigProxy()