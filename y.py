import yaml
print(yaml.__version__)
config='./config/AdvancedWhitelist.yml'
conf=yaml.load(config,Loader=yaml.FullLoader)