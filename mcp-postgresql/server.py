from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from dotenv import load_dotenv
import asyncpg
import logging
import uvicorn
import argparse
import os

MCP_SERVER_NAME = "postgres-mcp-sse"
    
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)
def format_sql_params(query: str,params:dict):
    if not params:
        return 'None'
    
    formatted = []
    for idx, param in enumerate(params, 1):
        try:
            type_name = type(param).__name__
            if isinstance(param, str):
                value_repr = str(param)
            else:    
                value_repr = repr(param)
            
            # 处理特殊类型
            if isinstance(param, bytes):
                value_repr = f"<bytes len={len(param)}>"
            elif param is None:
                type_name = 'NoneType'
            if isinstance(param, str) and 'password' in query.lower():
                value_repr = '******' 
            formatted.append(f"{value_repr}({type_name})")
        except Exception as e:
            formatted.append(f"!!PARAM_ERROR[{e}]!!")
    return ', '.join(formatted)

def pg_config():
    load_dotenv()
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    username = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DATABASE")
    schema = os.getenv("POSTGRES_SCHEMA")
    showSql = os.getenv("POSTGRES_SHOW_SQL", False)
    return {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'database': database,
        'schema': schema,
        'showSql':showSql
    }
class PostgresClient:
    _instance = None
    _showSql = False
    def __new__(cls, config):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._config = config
            cls._instance._showSql =config['showSql']
        return cls._instance
    
    async def initialize(self):
        if not hasattr(self, '_pool'):
            self._pool = await asyncpg.create_pool(
                host=self._config['host'],
                port=self._config['port'],
                database=self._config['database'],
                user=self._config['username'],
                password=self._config['password'],
                min_size=3,
                max_size=10
            )
            logger.info("Connection pool created")
    async def execute_query(self, query, params=None):
        try:
            if self._showSql:
                logger.info("Executing query: \nSQL:\t  %s\nPARAMETES:%s", query, format_sql_params(query, params))
            async with self._pool.acquire() as conn:
                if query.strip().lower().startswith("select"):
                    return await conn.fetch(query, *params or ())
                else:
                    await conn.execute(query, *params or ())
                    return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query failed: {str(e)}")
            return False

    def close(self):
        self.cursor.close()
        self.conn.close()
    
async def startup_event():
    pg = PostgresClient(pg_config())
    await pg.initialize()
    logger.info("PostgreSQL connection pool initialized:%s", pg)
async def get_tables(request:Request):
    """异步查询示例"""
    try:
        pg = getPool(request)
        results = await pg.execute_query(
            "SELECT * FROM pg_tables WHERE schemaname = $1",
            ('coin',)
        )
        return JSONResponse({"tables": [dict(r) for r in results]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

def getPool(request):
    return request.app.state.pg_client    

def create_starlette_app():
    app = Starlette(
        debug=True,
        routes=[
            Route("/messages/", get_tables),
        ],
        on_startup=[startup_event]
    )
    app.state.pg_client = PostgresClient(pg_config()) 
    return app
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    args = parser.parse_args()
    logger.info("MCP PostgreSQL server started")
    uvicorn.run("server:create_starlette_app", host=args.host, port=args.port,reload=True)