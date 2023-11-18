"""
    load my exist local features file
    into mongo
"""
import json

from dbs.mongo_base import mongo_db

col = mongo_db["features"]
resp = col.create_index("id")
resp = col.create_index("html_url")

with open("/data1/kexingchen/new_pullreq_new_0.jsonl", "r") as f:
    for line in f:
        lin = line.strip()
        if not lin:
            continue
        data = json.loads(lin)
        key = {"id": data["id"]}
        col.update_one(key, {"$set": data}, upsert=True)

with open("/data1/kexingchen/new_pullreq_new_diff.jsonl", "r") as f:
    for line in f:
        lin = line.strip()
        if not lin:
            continue
        data = json.loads(lin)
        key = {"id": data["id"]}
        col.update_one(key, {"$set": data}, upsert=True)
