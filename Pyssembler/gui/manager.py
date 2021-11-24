from enum import Enum
import logging



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
        self.current_state = None
        self.prev_state = None
    
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
        self.menu.file_menu.entryconfig('Close Project', state='disabled')
        self.menu.file_menu.entryconfig('Close File', state='disabled')

    