import os
import sys
import pymysql

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
