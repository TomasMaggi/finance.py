import sqlite3
import pathlib
from os.path import exists

# erase the db if alredy exist
if exists("finance.db"):
    file1 = pathlib.Path("finance.db")
    file1.unlink()

connection = sqlite3.connect("finance.db")
cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER, 
        username TEXT NOT NULL, 
        hash TEXT NOT NULL, 
        cash NUMERIC NOT NULL DEFAULT 10000.00, 
        PRIMARY KEY(id))
        ''')

cursor.execute('''CREATE UNIQUE INDEX username ON users (username);''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER,
        user_id INTEGER,
        symbol TEXT,
        share INTEGER,
        operation TEXT,
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        PRIMARY KEY(id))
''')
connection.commit()

connection.close()
