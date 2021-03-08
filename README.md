## Set up env  
```
python3 -m venv env
. env/bin/activate
pip3 install asyncpg
```

## Example
Insert
```
query_str = 'INSERT INTO player (name, age) VALUES ($1, $2)' 
name = 'Tom'
age = 3

tr = Transaction()
q = Query(query_str, name, age)
tr.append_query(q)

async with AsyncDb(1, 2, conn_params) as db:
    await db.run_transaction(tr)
```

Select
```
query_str = 'SELECT * from player'
async with AsyncDb(5, 10, conn_params) as db:
    q = Query(query_str)
    records_generator = db.get_records(q)
    async for r in records_generator:
        print(r)
```