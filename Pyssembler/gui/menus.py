import tkinter as tk
from tkinter import filedialog
import os

class MenuRibbon(tk.Menu):
    """
    Menu Ribbon
    """

    def __init__(self, master, manager):
        super().__init__(master, tearoff=False)
        self.manager = manager
        self.manager.menu = self
        self.master.config(menu=self)

        self.file_menu = FileMenu(master, manager)
        self.edit_menu = EditMenu(master, manager)

        self.add_cascade(label='File', menu=self.file_menu)
        self.add_cascade(label='Edit', menu=self.edit_menu)

class FileMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master, tearoff=False)
        self.manager = manager
        self.add_command(label='New File', command=self.on_new_file)
        self.add_command(label='Open File', command=self.on_open_file)
        self.add_command(label='Close File')
        self.add_separator()
        self.add_command(label='Save')
        self.add_command(label='Save As')
        self.add_command(label='Save All')
        self.add_separator()
        self.add_command(label='Exit', command=self.manager.exit)
        self.add_separator()
        self.add_command(label='Settings')
    
    def on_new_file(self):
        path = filedialog.asksaveasfilename(
                initialdir=os.getcwd()+'/Pyssembler/work',
                title='New File',
                filetypes=(("asm files", "*.asm"),("all files", "*.*")),
                defaultextension="*.asm"
                )
        self.manager.new_file(path)

    def on_open_file(self):
        path = filedialog.askopenfilename(
            initialdir=os.getcwd()+'/Pyssembler/work',
            title='Open File',
            filetypes=(('asm files', '*.asm'), ('all files', '*.*')),
            defaultextension='*.asm'
        )
        self.manager.open_file(path)
    
    

class EditMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master, tearoff=False)
        self.manager = manager
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
