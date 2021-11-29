import configparser
from pathlib import Path
import os

__CONFIG_FILE__ = Path('./config.ini').absolute()

def generate_default_config():
    config = configparser.ConfigParser()
    config['editor'] = {}
    config['editor']['font'] = 'Courier'
    config['editor']['font-size'] = '14'
    config['editor']['syntax-highlighting'] = 'True'
    with open(__CONFIG_FILE__, 'w') as f:
        config.write(f)

def get_config():
    config = configparser.ConfigParser()
    if not os.path.exists(__CONFIG_FILE__):
        generate_default_config()
    config.read(__CONFIG_FILE__)
    return config

def update_config(config: configparser.ConfigParser):
    with open(__CONFIG_FILE__, 'w') as f:
        config.write(f)
