from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from datetime import datetime
from dotenv import load_dotenv
from datasource import createDatasource,Datasource
import mcp.types as types
import logging
import uvicorn
import argparse
import os

MCP_SERVER_NAME = "postgres-mcp-sse"
    
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

pg:Datasource = None
def pg_config():
    load_dotenv()
    return {
        'host': os.getenv("POSTGRES_HOST"),
        'port': os.getenv("POSTGRES_PORT"),
        'username': os.getenv("POSTGRES_USERNAME"),
        'password': os.getenv("POSTGRES_PASSWORD"),
        'database': os.getenv("POSTGRES_DATABASE"),
        'schema': os.getenv("POSTGRES_SCHEMA"),
        'showSql':os.getenv("POSTGRES_SHOW_SQL", False),
        'type': os.getenv("POSTGRES_TYPE")
    }
    
async def startup_event():
    pg:Datasource = createDatasource(pg_config())
    await pg.initialize()
    logger.info("PostgreSQL connection pool initialized")
async def get_tables(request:Request):
    """List all database tables"""
    try:
        pg = getPool(request)
        results = await pg.query(
            "SELECT * FROM pg_tables WHERE schemaname = $1",
            pg.getSchema()
        )
        return JSONResponse({"data": [dict(r) for r in results]})
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)

async def get_table_columns_schema(request: Request):
    """Get table columns"""
    table = request.path_params.get("table")
    results = await pg.query(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = $1 and table_schema = $2",
        table, pg.getSchema()
    )
    return JSONResponse({"data": [dict(r) for r in results]})

async def get_data(request: Request):
    """execute sql """
    sql = request.query_params.get("sql")
    results = await pg.query(sql)
    return JSONResponse({"data": [dict(date_format(r)) for r in results]})

def date_format(obj):
    return {
        key: value.isoformat() if isinstance(value, datetime) else value
        for key, value in obj.items()
    }

def getPool(request):
    return request.app.state.pg_client    

mcp = FastMCP(MCP_SERVER_NAME)
pg = createDatasource(pg_config()) 
@mcp.tool()
async def list_tables():
    """List all database tables"""
    results = await pg.query(
        "SELECT * FROM pg_tables WHERE schemaname = $1",
        pg.getSchema()
    )
    return results

@mcp.tool()
async def get_table_columns(table: str):
    """Get table columns"""
    results = await pg.query(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = $1 and table_schema = $2",
        table, pg.getSchema()
    )
    return [dict(r) for r in results]

@mcp.tool()
async def list_data(table: str):
    """List all table data"""
    results = await pg.query(f"SELECT * FROM {table}")
    return results

@mcp.tool()
async def query_data(query: str, args=None):
    """Query data by sql query and args"""
    results = await pg.query(query, args)
    return [dict(date_format(r)) for r in results]

@mcp.prompt(name="db-prompt")
def db_propmpt():
    return f"""You are a {pg.getType()} database assistant.
You can query the database by sql query and args.
You can list all database tables by calling the `list_tables` tool.
You can list all table columns by calling the `get_table_columns` tool.
You can list all table data by calling the `list_data` tool.    
"""

# @mcp.list_prompts()
# async def handle_list_prompts() -> list[types.Prompt]:
#     return [
#         types.Prompt(
#             name="example-prompt",
#             description="An example prompt template",
#             arguments=[
#                 types.PromptArgument(
#                     name="arg1",
#                     description="Example argument",
#                     required=True
#                 )
#             ]
#         )
#     ]

def create_starlette_app():
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")
    mcp_server:Server = mcp._mcp_server
    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
    app = Starlette(
        debug=True,
        routes=[
            Route("/data", get_data),
            Route("/{table}/schema", get_table_columns_schema),
            Route("/tables/", get_tables),
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        on_startup=[startup_event]
    )
    
    app.state.pg_client = pg
    return app
if __name__ == "__main__":
    # mcp_server = mcp._mcp_server
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    args = parser.parse_args()
    logger.info("MCP server started")
    uvicorn.run("server:create_starlette_app", host=args.host, port=args.port,reload=True)