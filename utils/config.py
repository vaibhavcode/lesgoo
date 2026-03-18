import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

def load_config():
    with open(_CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()