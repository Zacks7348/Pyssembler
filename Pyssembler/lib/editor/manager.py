from enum import Enum
import logging
import os

from Pyssembler.environment.mips_translator import mips_to_binary

log = logging.getLogger(__name__)

class State(Enum):
    HOME = 0
    SAVED = 1
    UNSAVED = 2

class Manager():
    def __init__(self, root, app):
        self.root = root
        self.menu = None
        self.app = app
        self.file_dir = None
        self.file_name = None
        self.state = None
        self.TITLE = '{} - Pyssembler'
    
    def link_menu(self, menu):
        self.menu = menu
    
    def exit(self):
        self.root.destroy()
    
    def highlight_syntax(self, line=True):
        self.app.syntax_editor(line)

    def change_title(self, title):
        self.root.title(title)
    
    def on_editor_update(self, sv):
        if self.state is State.SAVED:
            self.change_state(State.UNSAVED)
        self.app.syntax_editor()
    
    def clear_editor(self, unsave=False):
        self.app.clear_editor()
        if unsave:
            self.change_state(State.UNSAVED)
    
    def set_state_home(self):
        self.change_state(State.HOME)

    def change_state(self, state):
        log.debug('State change: {} to {}'.format(self.state, state))
        if state == State.HOME:
            self.menu.entryconfig('Edit', state='disabled')
            self.menu.entryconfig("Translate", state='disabled')
            self.menu.entryconfig('Simulate', state='disabled')
            self.menu.file_menu.entryconfig('Close File', state='disabled')
            self.menu.file_menu.entryconfig('Save', state='disabled')
            self.menu.file_menu.entryconfig('Save As', state='disabled')
            self.app.clear_editor()
            self.app.configure_editor('disabled')
            self.file_dir = None
            self.file_name = None
            self.change_title("Pyssembler")
        
        else:
            self.menu.entryconfig('Edit', state='normal')
            self.menu.entryconfig("Translate", state='normal')
            self.menu.entryconfig('Simulate', state='normal')
            self.menu.file_menu.entryconfig('Close File', state='normal')
            self.menu.file_menu.entryconfig('Save', state='normal')
            self.menu.file_menu.entryconfig('Save As', state='normal')
            self.app.configure_editor('normal')
        self.state = state
    
    def save(self):
        try:
            log.info('Saving file...')
            with open(self.file_dir, 'w') as out:
                out.write(self.app.get_text_editor())
            log.info('Saved file: '+self.file_dir)
            self.change_state(State.SAVED)
            self.highlight_syntax(line=False)
            return True
        except:
            log.info('Could not save file')
            return False

    def create_file(self, file_dir):
        try:
            log.info('Creating new file...')
            open(file_dir, 'w').close()
            self.file_dir = file_dir
            self.file_name = os.path.basename(self.file_dir)
            self.change_title(self.TITLE.format(self.file_dir))
            self.change_state(State.SAVED)
            log.debug('Created new file: '+self.file_dir)
            self.app.clear_editor()
            return True
        except:
            return False
    
    def open_file(self, file_dir):
        if file_dir == "":
            return False
        log.info("Opening file...")
        try:
            with open(file_dir, "r") as in_file:
                self.change_state(State.SAVED)
                self.app.clear_editor()
                self.app.insert_text_editor(in_file.read())
                self.file_dir = file_dir
                self.file_name = os.path.basename(self.file_dir)
                self.change_title(self.TITLE.format(self.file_dir))
                log.info('Opened file!')
                self.highlight_syntax(line=False)
        except:
            return False
    
    def close_file(self):
        log.info('Closing file...')
        self.file_dir = None
        self.file_name = None
        self.change_title('Pyssembler')
        self.app.clear_editor()
        self.change_state(State.HOME)
        log.info('Closed file!')

    def mips_to_binary(self):
        self.app.console.info('Translating mips...')
        code = self.app.get_text_editor().splitlines()
        code = mips_to_binary(code)
        if code[1]:
            self.app.console.info('Successfully translated mips to binary!')
            return code[0]
        else:
            self.app.console.error(str(code[0]))
            return None
          
    @property
    def saved(self):
        return self.state == State.SAVED or self.state == State.HOME
    
    @property
    def is_home(self):
        return self.state == State.HOME
    