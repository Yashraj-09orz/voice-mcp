#every part of the database would talk to server very often so these are aliases which would be used again and again instead of manually writing all the stuff
#it activates everything which is required in order to interact with the database

#-- Connect -> connectin to the database
import os
import sqlite3
from braindump import config
#check if the folder and the file exist or not if not then create one and turn on the sqlite foreign key and connect the database
def connect():
    os.makedirs(os.path.dirname(config.DB_PATH),exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row #just to make all of them readable using string all the column can be now read through string
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
#inside the database table copy the schema make all the rows and column and initialize all the table ready to store the data
def init_db():
    with open(config.SCHEMA_PATH) as f:
        schema = f.read()
    conn = connect()
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(schema)
    finally:
        conn.close()
#querying all of them and getting the output for a sql query which is executed 
#rows = query_all("SELECT name FROM folders WHERE parent_id = ?", (1,))
def query_all(sql,params=()):
    conn = connect()
    try:
        return conn.execute(sql,params).fetchall()
    finally:
        conn.close()
#now to fetch only one single thing 
def query_one(sql, params=()):
    conn = connect()
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()
#now executing the query for writing into database , with changing instead of keeping as draft
def execute(sql,params = ()):
    conn = connect()
    try:
        cur = conn.execute(sql,params)
        conn.commit() #save in the table the draft 
        return cur.lastrowid #what was saved at last
    except Exception:
        conn.rollback() #undo the change
        raise #return the query 
    finally:
        conn.close()

        
