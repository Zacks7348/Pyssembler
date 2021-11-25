import tkinter as tk

class SimulatorPage(tk.Frame):
    """
    Container for Widgets to be displayed during simulation
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager

class RegisterBlock(tk.Frame):
    """
    Container for displaying registers and their values
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager

class MemoryBlock(tk.Frame):
    """
    Container for displaying memory contents
    """
    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager