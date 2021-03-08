import asyncpg
import logging
from typing import Awaitable, Generator, TypedDict, List, AsyncGenerator
from contextlib import asynccontextmanager, AbstractAsyncContextManager

LOGGER = logging.getLogger(__name__)

class ConnectionParams(TypedDict):
    database: str
    user: str
    password: str
    host: str
    port: int

class Query:
    def __init__(self, query_str: str, *args) -> None:
        self._query_str: str = query_str
        self._args: List = args

    @property
    def query_str(self):
        return self._query_str

    @query_str.setter
    def query_str(self, val):
        self._query_str = val
    
    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, val):
        self._args = val


class Transaction:
    def __init__(self) -> None:
        self.queries: List[Query] = []

    def append_query(self, q: Query):
        self.queries.append(q)

    def get_queries(self) -> Generator[Query, None, None]:
        for q in self.queries:
            yield q


class AsyncDb(AbstractAsyncContextManager):
    def __init__(self, 
                 min_connections: int, 
                 max_connections: int,
                 params: ConnectionParams) -> None:
        self._min_connections: int = min_connections
        self._max_connections: int = max_connections
        self._params: ConnectionParams = params
    
    async def __aenter__(self):
        self._pool = await asyncpg.create_pool(**self._params, 
                                               min_size=self._min_connections, 
                                               max_size=self._max_connections)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._pool:
            await self._pool.close()
        return await super().__aexit__(exc_type, exc_value, traceback)

    @asynccontextmanager
    async def __connection(self) -> asyncpg.Connection:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def run_transaction(self, tr: Transaction) -> Awaitable[bool]:
        try:
            async with self.__connection() as conn:
                for q in tr.get_queries():
                    await conn.execute(q.query_str, *(q.args))
            return True
        except:
            LOGGER.error(f'Transaction Failed')
            return False

    async def get_records(self, q: Query) -> AsyncGenerator:
        async with self.__connection() as conn:
            async for record in conn.cursor(q.query_str, *(q.args)):
                yield record
        
