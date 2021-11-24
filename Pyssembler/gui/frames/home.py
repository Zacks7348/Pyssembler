import tkinter as tk

class HomePage(tk.Frame):
    """
    Home Page of the application
    """

    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.__init_ui()
        
    def __init_ui(self):
        self.new_project_button = tk.Button(text='New Project')
        self.new_project_button.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        self.open_project_button = tk.Button(text='Open Project')
        self.open_project_button.place(relx=0.5, rely=0.55, anchor=tk.CENTER)