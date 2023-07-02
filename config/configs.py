import yaml
f = open("config/configs.yaml", "r")
config = yaml.load(f.read(), Loader=yaml.BaseLoader)
