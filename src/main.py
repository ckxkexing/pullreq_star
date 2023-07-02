import yaml
import importlib
from dbs.tables.prs import list_pr
from dbs.tables.projects import get_project_by_full_name

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

    # load hook function
    hook_functions = register_hooks(config)

    owner = "atom"
    repo  = "atom"
    repo_id = get_project_by_full_name(f"{owner}/{repo}")

    prs = list_pr(repo_id)
    featured_prs = []
    for pr in prs[:10]:
        # exec feature_func
        pr_id = pr['id']
        for feature_func, function_name in hook_functions:
            pr[function_name] = run_with_pr_id(feature_func, repo_id, pr_id)
            featured_prs.append(pr)
