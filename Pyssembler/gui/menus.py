import tkinter as tk

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
        self.add_command(label='New Project')
        self.add_command(label='Open Project')
        self.add_command(label='Close Project')
        self.add_separator()
        self.add_command(label='New File')
        self.add_command(label='Open File')
        self.add_command(label='Close File')
        self.add_separator()
        self.add_command(label='Save')
        self.add_command(label='Save As')
        self.add_command(label='Save All')
        self.add_separator()
        self.add_command(label='Exit')
        self.add_separator()
        self.add_command(label='Settings')
    

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
