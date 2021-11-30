import tkinter as tk


class AboutWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resizable(False, False)
        self.title('About')
        self.__init_ui()

    def __init_ui(self):
        self.text_contents = """Pyssembler 1.0  Copyright 2020-2021
Zackary Schreiner
Pyssembler is a MIPS IDE & Simulator built in Python

This project was inspired by the MARS project
MARS: http://courses.missouristate.edu/kenvollmar/mars/
        """

        self.text = tk.Text(self)
        self.text.insert('1.0', self.text_contents)
        self.text.config(state='disabled')
        self.ok = tk.Button(self, text='OK', command=self.destroy)

        self.text.pack(side=tk.TOP)
        self.ok.pack(side=tk.TOP)
