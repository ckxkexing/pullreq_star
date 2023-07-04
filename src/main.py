import json
import yaml
import argparse
import importlib
from dbs.tables.prs import list_pr
from dbs.tables.projects import get_project_by_full_name
from config.configs import repos

def run_with_pr_id(feature_func, repo_id, pr_id):
    return feature_func(repo_id, pr_id)

def register_hooks(config):
    hook_functions = []
    for feature in config['features']:
        if feature['enabled']:
            module_name, function_name = feature['name'].rsplit('.', 1)
            module = importlib.import_module(module_name)
            hook_functions.append((getattr(module, function_name), function_name))
    return hook_functions

if __name__ == "__main__":
    # feature config
    with open('config/feature_configs.yaml', 'r') as f:
        config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', dest='output_file')
    args = parser.parse_args()

    # load hook function
    hook_functions = register_hooks(config)

    for owner, repo, lang in repos:
        print(f"{owner} / {repo}")

        repo_id = get_project_by_full_name(f"{owner}/{repo}")

        prs = list_pr(repo_id)

        for i, pr in enumerate(prs):
            for feature_func, function_name in hook_functions:
                # exec feature_func
                pr_id = pr['id']
                prs[i].update(run_with_pr_id(feature_func, repo_id, pr_id))

            with open(args.output_file, "a") as f:
                f.write(json.dumps(prs[i]) + "\n")
            