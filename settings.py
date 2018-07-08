from collections import namedtuple
from yaml import load

full_path = "/Users/timbledum/Documents/Python/tmhouse/"

try:
    with open("settings.yaml") as file:
        settings_yaml = load(file)
except FileNotFoundError:
    with open(full_path + "settings.yaml") as file:
        settings_yaml = load(file)

settings = namedtuple("Settings", settings_yaml.keys())(*settings_yaml.values())
