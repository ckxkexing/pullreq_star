"""
    export pr features from mongodb
"""

from tqdm import tqdm

from dbs.mongo_base import mongo_db
from tools.file_util import write_csv_data


col = mongo_db["features"]

cursor = col.find({}, {"_id": 0})

headers = []

for feature in tqdm(cursor):
    headers = list(set(headers + list(feature.keys())))

headers.remove("id")
headers.remove("number")
headers.remove("html_url")
headers.remove("merge_decision")
headers = ["id", "number", "html_url", "merge_decision"] + headers

headers.remove("description")
headers.remove("code_add")
headers.remove("code_del")
headers = headers + ["description", "code_add", "code_del"]

res = []
cursor = col.find({}, {"_id": 0})

for feature in tqdm(cursor):
    cur = []
    for k in headers:
        if k not in feature:
            cur.append(None)
        else:
            if k in ["description", "code_add", "code_del"]:
                feature[k] = "<nl>".join(feature[k].splitlines())
            cur.append(feature[k])
    res.append(cur)

write_csv_data("/data1/kexingchen/new_pullreq.csv", headers, res)
