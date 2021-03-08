## Set up env  
```
python3 -m venv env
. env/bin/activate
pip3 install asyncpg
```
<br/><br/>

## Example
Insert
```
query_str = 'INSERT INTO player (name, age) VALUES ($1, $2)' 
name = 'Tom'
age = 3

tr = Transaction()
tr.append_query(Query(query_str, name1, age1))

async with AsyncDb(1, 2, conn_params) as db:
    await db.run_transaction(tr)
```

Select
```
query_str = 'SELECT * from player'
async with AsyncDb(5, 10, conn_params) as db:
    records_generator = db.get_records(Query(query_str))
    async for r in records_generator:
        print(r)
```