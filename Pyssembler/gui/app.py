import tkinter as tk
import logging

from .menus import MenuRibbon
from .manager import Manager, State
from .frames.home import HomePage

LOGGER = logging.getLogger('Pyssembler')

class PyssemblerApp:
    """
    Represents the Pyssembler GUI
    """

    def __init__(self) -> None:
        # Configure root
        self.root = tk.Tk()
        self.root.title('Pyssembler')
        self.root.minsize(1000, 500)
        self.root.state('zoomed')
        self.manager = Manager(self.root, self)

        self.__init_ui()
    
    def __init_ui(self):
        self.menu = MenuRibbon(self.root, self.manager)
        self.manager.menu = self.menu
        self.home = HomePage(self.root, self.manager)
        self.home.pack()
    
    def run(self):
        LOGGER.debug('Starting GUI Application...')
        self.manager.change_state(State.HOME)
        self.root.mainloop()
        LOGGER.debug('Exited GUI loop')
