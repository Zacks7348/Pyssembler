import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from tkinter.scrolledtext import ScrolledText
import os

class MainMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master=None, tearoff=False)
        self.manager = manager
        self.manager.link_menu(self)
        self.master.config(menu=self)
        self.file_menu = FileMenu(master, manager)
        self.edit_menu = EditMenu(master, manager)
        self.translate_menu = TranslateMenu(master, manager)
        self.view_menu = ViewMenu(master, manager)

        self.add_cascade(label='File', menu=self.file_menu)
        self.add_cascade(label='Edit', menu=self.edit_menu)
        self.add_cascade(label='Translate', menu=self.translate_menu)
        self.add_command(label='Simulate')
        self.add_cascade(label='View', menu=self.view_menu)

class FileMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master=None, tearoff=False)
        self.manager = manager
        self.add_command(label="New File", command=self.on_new_file)
        self.add_command(label="Open File", command=self.on_open_file)
        self.add_command(label="Close File", command=self.on_close_file)
        self.add_separator()
        self.add_command(label="Save", command=self.on_save)
        self.add_command(label="Save As", command=self.on_save_as)
        self.add_separator()
        self.add_command(label="Exit", command=self.on_exit)
        self.add_separator()
        self.add_command(label="Settings")

    def prompt_save(self, title='Save', message='Do you want to save?'):
        if self.manager.file_dir is None:
            return False
        option = tk.messagebox.askyesnocancel(
                title=title,
                message=message   
                )
        if option:
            self.on_save()
        return option
    
    def on_save(self, title='Save'):
        if self.manager.is_home:
            return
        if self.manager.file_name is None:
            self.on_save_as()
            return
        if self.manager.save():
            messagebox.showinfo("Save", "Successfully saved "+self.manager.file_name)
        else:
            messagebox.showerror("Save As", "Could not save "+str(self.manager.file_name))

    def on_save_as(self, title='Save As'):
        self.on_new_file(title=title)
        if self.manager.save():
            messagebox.showinfo("Save As", "Successfully saved "+self.manager.file_name)
        else:
            messagebox.showerror("Save As", "Could not save "+str(self.manager.file_name))

    def on_exit(self):
        if not self.manager.saved:
            option = self.prompt_save()
            if option is None:
                return
        self.manager.exit()
    
    def on_new_file(self, title='New File'):
        if not self.manager.saved:
            option = self.prompt_save()
            if option is None:
                return
        file_dir = filedialog.asksaveasfilename(
                initialdir=os.getcwd()+'/work',
                title=title,
                filetypes=(("dat files", "*.dat"),("all files", "*.*")),
                defaultextension="*.dat"
                )
        if file_dir != "":
            self.manager.create_file(file_dir)
            
    
    def on_open_file(self):
        if not self.manager.saved:
            option = self.prompt_save()
            if option is None:
                return
        directory = filedialog.askopenfilename(
                initialdir=os.getcwd()+'/work',
                title="Open File",
                filetypes=(("dat files", "*.dat"),("all files", "*.*")),
                defaultextension="*.dat"
                )
        self.manager.open_file(directory)

    def on_close_file(self):
        if not self.manager.saved:
            option = self.prompt_save(title='Close File')
            if option is None:
                return
        self.manager.close_file()


class EditMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master=None, tearoff=False)
        self.manager = manager
        self.add_command(label='Clear', command=self.on_clear)
    
    def on_clear(self):
        self.manager.clear_editor(unsave=True)

class TranslateMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master=None, tearoff=False)
        self.manager = manager
        self.add_command(label="To Binary", command=self.on_to_binary)
        self.add_command(label="From Binary")
    
    def on_to_binary(self):
        output = self.manager.mips_to_binary()
        if not output is None:
            top = tk.Toplevel()
            top.title('Translation')
            msg = ScrolledText(top)
            msg.insert(tk.INSERT, '\n'.join(output))
            msg.configure(state='disabled')
            msg.pack()
            button = tk.Button(top, text='Ok', command=top.destroy)
            button.pack()

class ViewMenu(tk.Menu):
    def __init__(self, master, manager):
        super().__init__(master=None, tearoff=False)
        self.manager = manager

