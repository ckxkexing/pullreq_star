import os
import sys
import pymysql
import threading

sys.path.append(os.path.dirname(sys.path[0]))
from config.configs import config

config = config['mysql']
host = config['host']
port = int(config['port'])
db = config['db']
user = config['user']
password = config['passwd']

gh_conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
gh_cursor = gh_conn.cursor(pymysql.cursors.DictCursor)

thread_local = threading.local()
def get_mysql_db_connection():
    if not hasattr(thread_local, 'gh_conn') or not hasattr(thread_local, 'gh_cursor'):
        gh_conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
        gh_cursor = gh_conn.cursor(pymysql.cursors.DictCursor)
        thread_local.gh_conn = gh_conn
        thread_local.gh_cursor = gh_cursor
    return thread_local.gh_conn, thread_local.gh_cursor
