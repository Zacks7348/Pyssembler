from posixpath import abspath
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
        self.manager.ide = self
        self.__init_ui()
        
    def __init_ui(self):
        self.explorer = Explorer(self, self.manager, show='tree')
        self.exp_ybar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.explorer.yview)
        self.exp_xbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.explorer.xview)
        self.explorer.configure(yscroll=self.exp_ybar.set)
        self.explorer.configure(xscroll=self.exp_xbar.set)
        self.editor = EditorManager(self, self.manager)

        self.explorer.place(relwidth=0.09, relheight=0.98)
        self.exp_ybar.place(relwidth=0.01, relheight=1, relx=0.09)
        self.exp_xbar.place(relwidth=0.09, relheight=0.02, rely=0.98)
        self.editor.place(relwidth=0.9, relheight=1, relx=0.1)

class Explorer(ttk.Treeview):
    """
    A File Explorer
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.heading('#0', text='Explorer', anchor='w')
        # FOR TESTING
        self.add_path('Pyssembler/work')
        
    def add_path(self, path):
        """
        Adds a directory to the explorer. 
        """
        abspath = os.path.abspath(path)
        root = self.insert('', tk.END, text=path, open=True)
        self.__add_paths(root, abspath)
    
    def __add_paths(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            old = self.insert(parent, tk.END, text=p, open=False)
            if os.path.isdir(abspath):
                self.__add_paths(old, abspath)


class EditorManager(ttk.Notebook):
    """
    A Tabbed Editor organizer
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.open_editors = []
        self.__init_ui()
    
    def __init_ui(self):
        self.open_editor()

    def open_editor(self, path):
        """
        Creates a new editor tab 
        """

        self.open_editors.append(Editor(self, self.manager, path))
        self.add(self.open_editors[-1], text=os.path.basename(path))
        self.select(self.open_editors[-1])

    def close_editor(self, path):
        for e in self.open_editors:
            if e.path == path:
                self.forget(e)

class Editor(ScrolledText):
    """
    Represents an open editor for a specific file
    """
    def __init__(self, master, manager, path, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.path = path