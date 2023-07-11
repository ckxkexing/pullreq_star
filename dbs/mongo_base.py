import os
import sys
import pymongo

from config.configs import config

host = config['mongodb']['host']
port = config['mongodb']['port']
client = pymongo.MongoClient(host = host, port = port)
mongo_db = client[config['mongodb']['db']]
