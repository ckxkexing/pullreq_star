import os
import sys
import sqlite3
import threading

sys.path.append(os.path.dirname(sys.path[0]))
from config.configs import config

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

thread_local = threading.local()
def get_sqlite_db_connection():
    if not hasattr(thread_local, 'conn') or not hasattr(thread_local, 'cursor'):
        conn = sqlite3.connect(config['sqlite3']['path'])
        conn.row_factory = dict_factory     # query res as dict
        cursor = conn.cursor()
        thread_local.conn = conn
        thread_local.cursor = cursor
    return thread_local.conn, thread_local.cursor

# for main threads
conn = sqlite3.connect(config['sqlite3']['path'])
conn.row_factory = dict_factory     # query res as dict
cursor = conn.cursor()
