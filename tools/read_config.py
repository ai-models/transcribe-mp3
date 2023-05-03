# read ../config.json file

import json
import os


def read_config():
    with open(os.path.join(os.path.dirname(__file__), "../config.json")) as config_file:
        config = json.load(config_file)
    return config


if __name__ == "__main__":
    read_config()
