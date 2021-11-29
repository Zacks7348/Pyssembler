import tkinter as tk
from tkinter import ttk, font
from typing import Collection

import config


class SettingsWindow(tk.Toplevel):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resizable(False, False)
        self.title('Settings')
        self.root = root
        self.__init_ui()

    def __init_ui(self):
        settings = config.get_config()
        self.editor_font_label = tk.Label(self, text='Font:')
        self.editor_font_combo = ttk.Combobox(
            self, values=font.families(), state='readonly')
        self.editor_font_combo.current(
            list(font.families()).index(settings['editor']['font']))

        self.editor_font_size_label = tk.Label(self, text='Font Size:')
        self.editor_font_size_combo = ttk.Combobox(
            self, values=[i for i in range(10, 51)], state='readonly')
        self.editor_font_size_combo.current(
            settings.getint('editor', 'font-size')-10)

        self.editor_highlight_label = tk.Label(
            self, text='Syntax Highlighting')
        self.editor_highlight_combo = ttk.Combobox(
            self, values=[False, True], state="readonly")
        self.editor_highlight_combo.current(
            int(settings.getboolean('editor', 'syntax-highlighting')))

        self.save_button = tk.Button(self, text='Save', command=self.on_save)
        self.cancel_button = tk.Button(self, text='Cancel', command=lambda: self.destroy)
        self.default_button = tk.Button(self, text='Defaults')

        self.editor_font_label.grid(row=0, column=0)
        self.editor_font_combo.grid(row=0, column=1)
        self.editor_font_size_label.grid(row=1, column=0)
        self.editor_font_size_combo.grid(row=1, column=1)
        self.editor_highlight_label.grid(row=2, column=0)
        self.editor_highlight_combo.grid(row=2, column=1)
        self.save_button.grid(row=3, column=0)
        self.cancel_button.grid(row=3, column=1)
    
    def on_save(self):
        c = config.get_config()
        c['editor']['font'] = self.editor_font_combo.get()
        c['editor']['font-size'] = self.editor_font_size_combo.get()
        c['editor']['syntax-highlighting'] = self.editor_highlight_combo.get()
        config.update_config(c)
        self.root.event_generate('<<Pyssembler_SettingsUpdate>>')
        self.destroy()

        