import tkinter as tk
from tkinter import ttk

from Pyssembler.mips.instructions import get_basic_instructions, get_pseudo_instructions
from Pyssembler.mips.directives import Directives


class HelpWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.resizable(False, False)
        self.title('Help')
        self.__init_ui()

    def __init_ui(self):
        self.nb = ttk.Notebook(self)
        self.cols = ('Format', 'Description')
        self.instr_table = BasicInstructionTable(self)
        self.nb.add(self.instr_table, text='Basic Instructions')
        self.psuedo_table = PseudoInstructionTable(self)
        self.nb.add(self.psuedo_table, text='Pseudo Instructions')
        self.dir_table = DirectivesTable(self)
        self.nb.add(self.dir_table, text='Directives')

        self.close = tk.Button(self, text='Close', command=self.destroy)

        self.nb.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.close.pack(side=tk.TOP)


class HelpDataTable(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.table = tk.Text(self, wrap=tk.NONE)
        self.vsb = tk.Scrollbar(self, orient='vertical',
                                command=self.table.yview)
        self.table.config(yscrollcommand=self.vsb.set)
        self.hsb = tk.Scrollbar(
            self, orient='horizontal', command=self.table.xview)
        self.table.config(xscrollcommand=self.hsb.set)

        self.table.tag_config('graybg', background='gainsboro')
        self.add_with_gray = False

    def setup(self):
        self.table.config(state='disabled')
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.table.pack(side=tk.LEFT)

    def insert(self, keys, descs):
        max_len_format = max(len(f) for f in keys)
        max_len_desc = max(len(d) for d in descs) 
        # need to make sure descriptions are same length

        for f, d in zip(keys, descs):
            self.table.insert(tk.INSERT, '{f:<{ml}}\t{d}\n'.format(
                f=f, d=d.ljust(max_len_desc), ml=max_len_format))
        end = self.table.index(tk.END)
        for i in range(1, int(float(end))+1):
            if self.add_with_gray:
                linestart = self.table.index(f'{i}.0')
                self.table.mark_set('grayStart', linestart)
                lineend = self.table.index(f'{linestart} lineend')
                self.table.mark_set('grayEnd', lineend)
                self.table.tag_add('graybg', 'grayStart', 'grayEnd')
            self.add_with_gray = not self.add_with_gray


class BasicInstructionTable(HelpDataTable):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        formats = []
        descs = []
        for instr in get_basic_instructions():
            formats.append(instr.format)
            descs.append(instr.description)
        self.insert(formats, descs)
        self.setup()

class PseudoInstructionTable(HelpDataTable):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        formats = []
        descs = []
        for instr in get_pseudo_instructions():
            formats.append(instr.format)
            descs.append(instr.description)
        self.insert(formats, descs)
        self.setup()

class DirectivesTable(HelpDataTable):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        dirs = []
        descs = []
        for directive in Directives.get_directives():
            dirs.append(directive)
            descs.append(Directives.get_description(directive))
        self.insert(dirs, descs)
        self.setup()