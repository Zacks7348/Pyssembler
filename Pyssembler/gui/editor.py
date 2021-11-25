import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os

from .cmd import CommandLine

class IDEPage(tk.Frame):
    """
    Home Page of the application
    """

    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.__init_ui()
        
    def __init_ui(self):
        self.explorer = Explorer(self, self.manager, show='tree')
        self.exp_ybar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.explorer.yview)
        self.explorer.configure(yscroll=self.exp_ybar.set)
        self.editor = EditorManager(self, self.manager)

        self.explorer.place(relwidth=0.09)
        self.exp_ybar.place(relwidth=0.01)
        self.editor.place(relwidth=0.9)

class Explorer(ttk.Treeview):
    """
    A File Explorer
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.heading('#0', text='Dir', anchor='w')


class EditorManager(ttk.Notebook):
    """
    A Tabbed Editor organizer
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager

class Editor(ScrolledText):
    """
    Represents an open editor for a specific file
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager