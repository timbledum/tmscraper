from collections import namedtuple
from yaml import load

with open("settings.yaml") as file:
    settings_yaml = load(file)

settings = namedtuple("Settings", settings_yaml.keys())(*settings_yaml.values())
