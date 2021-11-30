import tkinter as tk
from tkinter import filedialog
import os

from .frames import AboutWindow, SettingsWindow, HelpWindow


class MenuRibbon(tk.Menu):
    """
    Menu Ribbon
    """

    def __init__(self, master):
        super().__init__(master, tearoff=False)
        #self.manager.menu = self
        self.master.config(menu=self)

        self.file_menu = FileMenu(master)
        self.edit_menu = EditMenu(master)
        self.help_menu = HelpMenu(master)

        self.add_cascade(label='File', menu=self.file_menu)
        self.add_cascade(label='Edit', menu=self.edit_menu)
        self.add_command(label='Simulate')
        self.add_cascade(label='Help', menu=self.help_menu)


class FileMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=False)
        self.add_command(label='New File', command=lambda:
                         self.master.event_generate('<<Pyssembler_NewFile>>'))
        self.add_command(label='Open File', command=lambda:
                         self.master.event_generate('<<Pyssembler_OpenFile>>'))
        self.add_command(label='Close File')
        self.add_separator()
        self.add_command(label='Save', command=lambda:
                         self.master.event_generate('<<Pyssembler_Save>>'))
        self.add_command(label='Save As', command=lambda:
                         self.master.event_generate('<<Pyssembler_SaveAs>>'))
        self.add_command(label='Save All', command=lambda:
                         self.master.event_generate('<<Pyssembler_SaveAll>>'))
        self.add_separator()
        self.add_command(label='Exit', command=lambda:
                         self.master.event_generate('<<Pyssembler_Exit>>'))
        self.add_separator()
        self.add_command(label='Settings',
                         command=lambda: SettingsWindow(self.master))


class EditMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=False)
        self.add_command(label='Undo')
        self.add_command(label='Redo')
        self.add_separator()
        self.add_command(label='Cut')
        self.add_command(label='Copy')
        self.add_command(label='Paste')
        self.add_separator()
        self.add_command(label='Find')
        self.add_command(label='Replace')
        self.add_command(label='Select All')


class HelpMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=False)
        self.add_command(label='Help', command=lambda: HelpWindow())
        self.add_separator()
        self.add_command(label='Report Issue')
        self.add_separator()
        self.add_command(label='About', command=lambda: AboutWindow())

    def on_about(self):
        AboutWindow()
