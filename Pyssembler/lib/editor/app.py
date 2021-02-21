import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging

from Pyssembler.lib.editor.manager import Manager
from Pyssembler.lib.editor.menus import MainMenu
from Pyssembler.lib.editor.frames import Editor, Console, Simulation

log = logging.getLogger(__name__)

class App:
    def __init__(self, root, title="Pyssembler"):
        self.root = root
        self.root.geometry("1000x500")
        self.root.minsize(1000, 500)
        self.root.title(title)
        self.manager = Manager(self.root, self)
        self.menu = MainMenu(self.root, self.manager)
        self.editor = Editor(self.root)
        self.console = Console(self.root)
        self.simulation = Simulation(self.root)

        # Set program state to HOME
        self.manager.set_state_home()

        # Bindings
        self.editor.text.bind("<KeyRelease>", self.manager.on_editor_update)
        self.editor.text.bind("<Control-s>", self.menu.file_menu.on_save)
        self.root.protocol("WM_DELETE_WINDOW", self.menu.file_menu.on_exit)

        self.manager.link_update_functions(self.editor.update_settings)

        # Placing Frames in root
        self.editor.place(relheight=0.85, relwidth=0.7)
        self.console.place(relheight=0.15, relwidth=0.7, rely=0.85)
        self.simulation.place(relwidth=0.3, relx=0.7)

    def insert_text_editor(self, data, start=tk.INSERT):
        self.editor.text.insert(start, data)

    def get_text_editor(self):
        return self.editor.text.get("1.0", tk.END)

    def get_text_console(self):
        return self.console.text.get("1.0", tk.END)

    def clear_editor(self):
        self.editor.text.delete("1.0", tk.END)

    def configure_editor(self, state):
        self.editor.text.config(state=state)

    def syntax_editor(self, line=True):
        if line:
            self.editor.text.highlight_syntax_line()
        else:
            self.editor.text.highlight_syntax()


def run():
    log.debug("Creating application...")
    root = tk.Tk()
    App(root)
    log.debug("Application created! Executing app...")
    root.mainloop()
