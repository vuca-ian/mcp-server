from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from dotenv import load_dotenv
from datasource import createDatasource,Datasource
import logging
import uvicorn
import argparse
import os

MCP_SERVER_NAME = "postgres-mcp-sse"
    
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)


def pg_config():
    load_dotenv()
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    username = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DATABASE")
    schema = os.getenv("POSTGRES_SCHEMA")
    type = os.getenv("POSTGRES_TYPE")
    showSql = os.getenv("POSTGRES_SHOW_SQL", False)
    return {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'database': database,
        'schema': schema,
        'showSql':showSql,
        'type': type
    }
    
async def startup_event():
    pg:Datasource = createDatasource(pg_config())
    await pg.initialize()
    logger.info("PostgreSQL connection pool initialized")
async def get_tables(request:Request):
    """异步查询示例"""
    try:
        pg = getPool(request)
        results = await pg.query(
            "SELECT * FROM pg_tables WHERE schemaname = $1",
            ('ipaas',)
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
    app.state.pg_client = createDatasource(pg_config()) 
    return app
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    args = parser.parse_args()
    logger.info("MCP PostgreSQL server started")
    uvicorn.run("server:create_starlette_app", host=args.host, port=args.port,reload=True)