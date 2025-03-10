from .PgDatasource import PostgresDatasource
from .Datasource import Datasource
def createDatasource(properties:dict):
    if(properties.get("type") == "postgresql"):
        return PostgresDatasource(properties)