import json

class Config():
    def __init__(self):
        with open('config.json', 'r') as in_file:
            config = json.load(in_file)
            for key, value in config.items():
                setattr(self, key, value)