import yaml
f = open("config/configs.yaml", "r")
config = yaml.load(f.read(), Loader=yaml.BaseLoader)

repos = []
with open("project_list.txt", "r") as f:
    for line in f:
        lin = line.strip()
        if not lin :
            continue
        owner, repo, lang = lin.split()
        repos.append((owner, repo, lang))
