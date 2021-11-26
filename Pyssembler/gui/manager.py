from enum import Enum
import logging
import os



LOGGER = logging.getLogger('Pyssembler')

class State(Enum):
    HOME = 0
    SAVED_PROJECT = 1
    UNSAVED_PROJECT = 2


class Manager:
    """
    The under-the-hood logic of the Pyssembler GUI.

    This class provides logic for widget-to-widget communication, 
    implements a state machine, and deals with IO.
    """
    def __init__(self, root, app):
        self.root = root
        self.app = app
        # Widgets that are set by app
        self.menu = None
        self.ide = None

        # State Info
        self.current_state = None
        self.prev_state = None

    def exit(self):
        if not self.ide.editor.close_editors():
            return
        self.root.destroy()

#-------------------------------------------------------------------------
# IO FUNCTIONS
#-------------------------------------------------------------------------

    def open_file(self, path):
        """
        Opens the file located at path, reads the contents
        """
        if not path:
            return
        LOGGER.debug(f'Opening file {path}...')
        self.ide.editor.open_editor(path)
        LOGGER.debug('Opened file!')
    
    def new_file(self, path):
        if not path:
            return
        LOGGER.debug(f'Creating new file {path}...')
        f = open(path, 'w')
        f.close()
        LOGGER.debug('Created file!')
        self.open_file(path)
        

#-------------------------------------------------------------------------
# State Machine
#-------------------------------------------------------------------------
    def change_state(self, state: State):
        """
        Perform a state change to state
        """
        self.prev_state = self.current_state
        if state == State.HOME:
            self.__home_state()
        self.current_state = state
    
    def revert_state(self):
        """
        Revert back to prev state
        """
        self.change_state(self.prev_state)
            
    def __home_state(self):
        # Menus
        pass

    