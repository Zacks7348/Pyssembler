from posixpath import abspath, expanduser
import tkinter as tk
from tkinter import ttk
from tkinter.constants import ANCHOR
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import os

from .cmd import CommandLine


class IDEPage(tk.Frame):
    """
    Home Page of the application
    """

    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.manager.ide = self
        self.__init_ui()

    def __init_ui(self):
        self.explorer = Explorer(self, self.manager, show='tree')
        self.exp_ybar = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.explorer.yview)
        self.exp_xbar = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.explorer.xview)
        self.explorer.configure(yscroll=self.exp_ybar.set)
        self.explorer.configure(xscroll=self.exp_xbar.set)
        self.editor = EditorManager(self, self.manager)

        # Bind Events
        self.explorer.bind('<<TreeviewSelect>>', self.on_explorer_select)

        # Display widgets
        self.explorer.place(relwidth=0.09, relheight=0.98)
        self.exp_ybar.place(relwidth=0.01, relheight=1, relx=0.09)
        self.exp_xbar.place(relwidth=0.09, relheight=0.02, rely=0.98)
        self.editor.place(relwidth=0.9, relheight=1, relx=0.1)

    def on_explorer_select(self, event):
        print(self.explorer.selection())


class Explorer(ttk.Treeview):
    """
    A File Explorer
    """

    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.heading('#0', text='Explorer', anchor='w')
        # FOR TESTING
        self.add_path('Pyssembler/work')

    def add_path(self, path):
        """
        Adds a directory to the explorer. 
        """
        abspath = os.path.abspath(path)
        root = self.insert('', tk.END, text=path, open=True)
        self.__add_paths(root, abspath)

    def __add_paths(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            old = self.insert(parent, tk.END, text=p, open=False)
            if os.path.isdir(abspath):
                self.__add_paths(old, abspath)


class EditorManager(ttk.Notebook):
    """
    A Tabbed Editor organizer
    """

    __initialized = False

    def __init__(self, master, manager, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            EditorManager.__initialized = True
        kwargs["style"] = "CustomNotebook"
        super().__init__(master, **kwargs)
        self.manager = manager
        self.open_editors = {}
        self._active = None
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def open_editor(self, path):
        """
        Creates a new editor tab 
        """
        if path in self.open_editors:
            self.select(self.open_editors[path])
            return
        self.open_editors[path] = Editor(self, self.manager, path)
        self.add(self.open_editors[path], text=os.path.basename(path))
        self.select(self.open_editors[path])

    def close_editor(self, editor):
        if editor.saved:
            self.forget(editor)
            return
        s = messagebox.askyesnocancel(
            title='Save', message=f'Do you want to save {os.path.basename(editor.path)}?')
        if s: 
            editor.save()
            self.forget(editor)
            return
        if s == False:
            self.forget(editor)
        if s is None:
            return False
        if s:
            editor.save()
        self.forget(editor)
        self.open_editors.pop(editor.path)
        return True
    
    def close_editors(self):
        """
        Close all open editors
        """
        for editor in self.open_editors.values():
            if not self.close_editor(editor):
                return False
            self.open_editors.pop(editor.path)
        return True
        

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""
        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return "break"

    def on_close_release(self, event):
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))
        if self._active == index:
            self.close_editor(self.nametowidget(self.tabs()[index]))
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        """
        Thanks to Bryan Oakley who wrote an answer to this stack overflow question
        https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook
        """
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [
                     ("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {
                                     "side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {
                                     "side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])


class Editor(tk.Frame):
    """
    Container for both the text editor and line numbers
    """

    def __init__(self, master, manager, path, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.path = path
        self.saved = True
        self.__init_ui()
        self.__read_file()

    def __init_ui(self):
        self.text = EditorText(self)
        self.vsb = tk.Scrollbar(self, orient="vertical",
                                command=self.text.yview)
        self.text.config(yscrollcommand=self.vsb.set)
        self.linenums = LineNumbers(self, self.text, width=30)

        self.linenums.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.vsb.pack(side=tk.LEFT, fil=tk.Y)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

    def save(self):
        """
        Save the current state of the editor to file at self.path
        """
        with open(self.path, 'w') as f:
            f.write(self.text.get('1.0', tk.END))
        self.saved = True

    def _on_change(self, event=None):
        self.linenums.redraw()
        self.saved = False

    def __read_file(self):
        with open(self.path) as f:
            self.text.insert(tk.INSERT, f.read())
        self.saved = True


class LineNumbers(tk.Canvas):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, **kwargs)
        self.text = text
        self.breakpoints = []

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum)
            i = self.text.index("%s+1line" % i)


class EditorText(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

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
