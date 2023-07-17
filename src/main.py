import sys
import yaml
import time
import random
import pymongo
import argparse
import importlib
from dbs.mongo_base import mongo_db
from dbs.tables.prs import list_pr
from dbs.tables.projects import get_project_by_full_name
from config.configs import repos

import threading
import queue

THREADNUM = 8

# the thread for processing each project
class handleThread(threading.Thread):
    def __init__(self, q, out_q):
        threading.Thread.__init__(self)
        self.q = q
        self.out_q = out_q
        self.hook_functions = self.register_hooks(config)
        random.shuffle(self.hook_functions)

    def run_with_pr_id(self, feature_func, repo_id, pr_id):
        return feature_func(repo_id, pr_id)

    def register_hooks(self, config):
        hook_functions = []
        for feature in config['features']:
            if feature['enabled']:
                module_name, function_name = feature['name'].rsplit('.', 1)
                module = importlib.import_module(module_name)
                hook_functions.append((getattr(module, function_name), function_name))
        return hook_functions

    def run(self):
        # load hook function
        while True:
            try:
                pr = self.q.get(timeout=0)
            except queue.Empty:
                break
            try:
                for feature_func, function_name in self.hook_functions:
                    # exec feature_func
                    pr_id = pr['id']
                    pr.update(self.run_with_pr_id(feature_func, repo_id, pr_id))
            finally:
                self.out_q.put(pr)
                self.q.task_done()
        self.out_q.put(None)

# logger 
def output_logger(queue):
    cnt = 0
    finished = 0
    col = mongo_db['features']

    while True:
        time.sleep(5)

        items = [queue.get() for _ in range(queue.qsize())]

        ops = []
        for item in items:
            if item is None:
                cnt += 1
            else:
                finished += 1
                key = {"id" : item['id']}
                ops.append((pymongo.UpdateOne(key, {"$set":item}, upsert=True)))
        if(len(ops) > 0) :
            col.bulk_write(ops, ordered=False)
            ops = []
        print("finished count = ", finished)
        if cnt >= THREADNUM:
            break
    print('output logger: Done')


if __name__ == "__main__":
    # feature config
    with open('config/feature_configs.yaml', 'r') as f:
        config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', dest='output_file')
    args = parser.parse_args()

    for owner, repo, lang in repos:

        print(f"{owner} / {repo}")

        repo_id = get_project_by_full_name(f"{owner}/{repo}")

        prs = list_pr(repo_id)

        tasks = queue.Queue()
        out_q = queue.Queue()

        for pr in prs:
            tasks.put(pr)

        output = threading.Thread(target=output_logger, args=(out_q,))
        output.daemon = True
        output.start() 

        for _ in range(THREADNUM):
            t = handleThread(tasks, out_q)
            t.daemon = True
            t.start()

        output.join()
        tasks.join()

        print("finish")
