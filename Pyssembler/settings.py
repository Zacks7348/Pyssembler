import json

class Settings():
    def __init__(self):
        with open('settings.json', 'r') as in_file:
            self.settings = json.load(in_file)
        self.editor = self.settings['editor-settings']
        self.translator = self.settings['translator-settings']
    
    def rewrite(self, new):
        self.config = new
        self.__write()
    
    def __write(self):
        with open('settings.json', 'w') as out_file:
            json.dump(self.config, out_file, indent=4)
            