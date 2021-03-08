import asyncio

from asyncdb import Query, AsyncDb, ConnectionParams, Transaction
from random import randint
import uuid
import time

conn_params = ConnectionParams(database='postgres', user='cuiy0006', password='', host='localhost', port='5432')

async def test_insertions_async():
   query_str = 'INSERT INTO player (name, age) VALUES ($1, $2)' 
   trs = []
   for j in range(100):
      tr = Transaction()
      for i in range(500):
         name = str(uuid.uuid4())
         age = randint(1, 100)
         tr.append_query(Query(query_str, name, age))

         if j == 50 and i == 250:
            tr.append_query(Query('INSERT INTO play (name, age) VALUES ($1, $2)', name, age))

      trs.append(tr)
   
   async with AsyncDb(5, 10, conn_params) as db:
      coros = [db.run_transaction(tr) for tr in trs]
      coro = asyncio.gather(*coros)
      await coro


async def test_insertion_sync():
   query_str = 'INSERT INTO player (name, age) VALUES ($1, $2)' 
   trs = []
   for _ in range(50000):
      name = str(uuid.uuid4())
      age = randint(1, 100)
      tr = Transaction()
      tr.append_query(Query(query_str, name, age))
      trs.append(tr)

   async with AsyncDb(5, 10, conn_params) as db:
      for tr in trs:
         await db.run_transaction(tr)


async def test_select():
   query_str = 'SELECT * from player'
   async with AsyncDb(5, 10, conn_params) as db:
      records_generator = db.get_records(Query(query_str))
      cnt = 0
      async for r in records_generator:
         cnt += 1
         if cnt <= 10:
            print(r)
      print(cnt)


if __name__ == '__main__':
   start = time.perf_counter()
   asyncio.run(test_insertions_async())
   end = time.perf_counter()
   print(f'async {end - start:0.2f} seconds')

   start = time.perf_counter()
   asyncio.run(test_insertion_sync())
   end = time.perf_counter()
   print(f'sync {end - start:0.2f} seconds')

   asyncio.run(test_select())