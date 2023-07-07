import sys
import json
import yaml
import random
import argparse
import importlib
from dbs.tables.prs import list_pr
from dbs.tables.projects import get_project_by_full_name
from config.configs import repos

import threading
import queue

THREADNUM = 2

# the thread for processing each project
class handleThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
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
                print(self.q.qsize())

                for i, pr in enumerate(prs):
                    for feature_func, function_name in self.hook_functions:
                        # exec feature_func
                        pr_id = pr['id']
                        prs[i].update(self.run_with_pr_id(feature_func, repo_id, pr_id))

                    # with open(args.output_file, "a") as f:
                    #     f.write(json.dumps(prs[i]) + "\n")
                    print(prs[i])

            except queue.Empty:
                return
            self.q.task_done()

if __name__ == "__main__":
    # feature config
    with open('config/feature_configs.yaml', 'r') as f:
        config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', dest='output_file')
    args = parser.parse_args()


    for owner, repo, lang in repos:

        if owner != "flutter":
            continue

        print(f"{owner} / {repo}")

        repo_id = get_project_by_full_name(f"{owner}/{repo}")

        prs = list_pr(repo_id)

        tasks = queue.Queue()

        for pr in prs:
            tasks.put(pr)

        for _ in range(THREADNUM):
            t = handleThread(tasks)
            t.daemon = True
            t.start()
        tasks.join()

        print("finish")