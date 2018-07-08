"""Get settings YAML file and load to object."""
import os
from collections import namedtuple
from yaml import load

FULL_PATH = "/Users/timbledum/Documents/Python/tmhouse/"

try:
    with open("settings.yaml") as file:
        settings_yaml = load(file)
except FileNotFoundError: # If launched by automatic scheduler
    with open(os.path.join(FULL_PATH, "settings.yaml")) as file:
        settings_yaml = load(file)

settings = namedtuple("Settings", settings_yaml.keys())(*settings_yaml.values())
