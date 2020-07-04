import tkinter as tk
from tkinter.scrolledtext import ScrolledText

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
        self.text.tag_config('instr', background='dark orange')
        self.text.tag_config('reg', background='dodger blue')
        self.text.tag_config('comment', foreground='gray47')
        self.text.tag_config('error', background='red')

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
        return "break"

    def highlight_syntax(self, start='1.0', end='end'):
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        count = tk.IntVar()
        while True:
            index = self.search('#', "matchEnd","searchLimit",
                                count=count, regexp=True)
            if index == "": break
            if count.get() == 0: break
            self.mark_set("matchStart", index)
            #self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
            self.mark_set('matchEnd', 'matchStart lineend')
            self.tag_add('comment', 'matchStart', 'matchEnd')

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
        self.text = ScrolledText(self, text_wrap=None)

        self.text.pack(anchor='nw', fill='both', expand=True)