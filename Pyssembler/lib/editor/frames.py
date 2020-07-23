import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json

LANG = 'Pyssembler/lib/language/'
MIPS_INSTR = LANG+'mips/instructions.json'
MIPS_REG = LANG+'mips/registers.json'

class Editor(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.text = CustomText(self, font=('Courier', 14, 'normal'), wrap=tk.NONE)
        self.vsb = tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.hsb = tk.Scrollbar(self, orient='horizontal', command=self.text.xview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.configure(xscrollcommand=self.hsb.set)
        self.linenumbers = TextLineNumbers(self, width=30, bg='grey97')
        self.linenumbers.attach(self.text)

        #Binding events
        self.text.bind('<<Change>>', self._on_change)
        self.text.bind('<Configure>', self._on_change)

        #Setup highlighting/syntax
        self.text.tag_config('instr', foreground='dark orange')
        self.text.tag_config('reg', foreground='dodger blue')
        self.text.tag_config('comment', foreground='gray47')
        self.text.tag_config('error', foreground='red')

        #Packing widgets
        self.vsb.pack(side='right', fill='y')
        self.linenumbers.pack(side='left', fill='y')
        self.hsb.pack(side='bottom', fill='x')
        self.text.pack(side='right', fill='both', expand='true')
    
    def _on_change(self, event):
        self.linenumbers.redraw()

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind("<<Paste>>", self.paste)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result
    
    def paste(self, event):
        tagranges = self.tag_ranges("sel")
        if tagranges:
            selectionstart = self.index(tk.SEL_FIRST)
            selectionend = self.index(tk.SEL_LAST)
            self.delete(selectionstart, selectionend)
            self.mark_set(tk.INSERT, selectionstart)
        self.insert(tk.INSERT, self.master.clipboard_get())
        self.see(tk.INSERT)
        self.highlight_syntax()
        return "break"

    def highlight_syntax(self, start='1.0', end='end'):
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        #Comments syntax
        while True:
            index = self.search('#', "matchEnd","searchLimit", regexp=True)
            if index == "": break
            self.mark_set("matchStart", index)
            #self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
            self.mark_set('matchEnd', 'matchStart lineend')
            self.tag_add('comment', 'matchStart', 'matchEnd')
        
        #Instr syntax
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        count = tk.IntVar()
        instr = []
        with open(MIPS_INSTR) as in_file:
            instr = json.load(in_file)
        while True:
            index = self.search('|'.join(instr), 'matchEnd', 'searchLimit', count=count, regexp=True)
            if index == '': break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
            self.tag_add('instr', 'matchStart', 'matchEnd')
        
        #Reg syntax
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        count = tk.IntVar()
        reg = []
        with open(MIPS_REG) as in_file:
            reg = json.load(in_file).values()
        while True:
            index = self.search('|'.join(reg).replace('$', '\$'), 'matchEnd', 'searchLimit', count=count, regexp=True)
            if index == '': break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
            self.tag_add('reg', 'matchStart', 'matchEnd')
    
    def highlight_syntax_line(self):
        self.mark_set('searchStart', self.index('insert linestart'))
        self.mark_set('searchEnd', self.index('insert lineend'))

        #Comments syntax
        index = self.search('#', 'searchStart', 'searchEnd', regexp=True)
        if index == '':
            self.tag_remove('comment', 'searchStart', 'searchEnd')
        else:
            self.mark_set("matchStart", index)
            self.tag_add('comment', 'matchStart', 'searchEnd')
        
        #Instructions syntax
        count = tk.IntVar()
        instr = []
        with open(MIPS_INSTR) as in_file:
            instr = json.load(in_file)
        index = self.search('|'.join(instr), 'searchStart', 'searchEnd', count=count, regexp=True)
        if index == '': 
            self.tag_remove('instr', 'searchStart', 'searchEnd')
        else:
            self.mark_set('matchStart', index)
            self.mark_set('matchEnd', '{}+{}c'.format(index, count.get()))
            self.tag_add('instr', 'matchStart', 'matchEnd')
        
        #Registers syntax
        reg = []
        with open(MIPS_REG) as in_file:
            reg = list(json.load(in_file).values())
        while True:
            index = self.search('|'.join(reg).replace('$', '\$'), 'searchStart', 'searchEnd', count=count, regexp=True)
            if index == '': 
                self.tag_remove('reg', 'searchStart', 'searchEnd')
                break
            else:
                self.mark_set('matchStart', index)
                self.mark_set('matchEnd', '{}+{}c'.format(index, count.get()))
                self.mark_set('searchStart', 'matchEnd+1c')
                self.tag_add('reg', 'matchStart', 'matchEnd')
            
        

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

class Console(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.text = ScrolledText(self, 
                                text_wrap=None, 
                                font=('Courier New', 10, 'normal'),
                                wrap=tk.WORD
                                )
        self.text.pack(anchor='nw', fill='both', expand=True)
        self.text.tag_config('info', foreground='lime green')
        self.text.tag_config('warning', foreground='orange')
        self.text.tag_config('error', foreground='red2')

        self.commands = {}
        self.commands['help '] = 'get help with all commands. help -command for help with a specfic command'
        self.commands['translate'] = '(-b/-m) translate code in current file. -b for binary conversion and -m for mips conversion'
        self.commands['clear'] = 'clears the text editor'
        self.commands['exit'] = 'exits program'
    
    def newline(self):
        self.text.insert(tk.INSERT, '\n')

    def get_command(self):
        return self.text.get('end-1c linestart', 'end-1c')

    def info(self, message):
        self.text.insert(tk.INSERT, message+'\n', 'info')
        
    def warning(self, message):
        self.text.insert(tk.INSERT, message+'\n', 'warning')
    
    def error(self, message):
        self.text.insert(tk.INSERT, message+'\n', 'error')
    
        
