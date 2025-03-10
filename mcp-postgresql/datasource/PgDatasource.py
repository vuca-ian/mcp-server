from .Datasource import Datasource, log
import asyncpg

class PostgresDatasource(Datasource):

    async def initialize(self):
        if not hasattr(self, '_pool'):
            self._pool = await asyncpg.create_pool(
                host=self._properties['host'],
                port=self._properties['port'],
                database=self._properties['database'],
                user=self._properties['username'],
                password=self._properties['password'],
                min_size=3,
                max_size=10
            )

    @log
    async def query(self, query, params=None):
        try:
            async with self._pool.acquire() as conn:
                if query.strip().lower().startswith("select"):
                    return await conn.fetch(query, *params or ())
                else:
                    await conn.execute(query, *params or ())
                    return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

