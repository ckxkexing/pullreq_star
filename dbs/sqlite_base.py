import os
import sys
import sqlite3

sys.path.append(os.path.dirname(sys.path[0]))
from config.configs import config

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect(config['sqlite3']['path'])
conn.row_factory = dict_factory     # query res as dict
cursor = conn.cursor()
