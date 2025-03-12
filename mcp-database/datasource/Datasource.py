from abc import ABCMeta, abstractmethod
from .SqlLogger import sql_print



def log(func):
    def wrapper(self, *args, **kwargs):
        sql_print(args[0],*args[1:],**kwargs)
        result = func(self, *args, **kwargs)
        return result
    return wrapper

class Datasource(metaclass=ABCMeta):
    _instance = None
    _properties = None
    def __init__(self, properties):
        self._properties = properties

    def __new__(cls, data):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._data = data
        return cls._instance
    
    @abstractmethod
    async def initialize(self):
        pass


    def getSchema(self):
        return self._properties.get("schema")

    def getType(self):
        return self._properties.get("type")
    @log
    @abstractmethod
    def query(self, query, *params):
        print("query---->")
        pass


