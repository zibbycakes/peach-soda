from flask import Flask
import psycopg2
from config import config

app = Flask(__name__)

def connect():
    """connect to the PostgresSQL database server"""
    conn = None
    try:
        params = config()
        print('connecting to the postgres db...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        print('postgres db version')
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('connection closed')

@app.route('/')
def hello_world():
    connect()
    return 'hello world'