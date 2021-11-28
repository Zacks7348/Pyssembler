from posixpath import abspath, expanduser
import tkinter as tk
from tkinter import ttk
from tkinter.constants import ANCHOR
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import os

from .cmd import CommandLine

from Pyssembler.mips.instructions import get_mnemonics
import Pyssembler.mips.hardware.registers as regs


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
        self.explorer = Explorer(self, self.manager, show='tree', selectmode=tk.BROWSE)
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
        path = self.explorer.paths.get(self.explorer.selection()[0], None)
        if path:
            self.editor.open_editor(path)
    
    def save(self):
        """
        Saves the selected editor 
        """
        self.editor.nametowidget(self.editor.select()).save()
    
    def save_as(self, path):
        """
        Saves the selected editor as a new file
        """
        self.editor.nametowidget(self.editor.select()).save_as(path)
        self.editor.open_editor(path)

class Explorer(ttk.Treeview):
    """
    A File Explorer
    """

    def __init__(self, master, manager, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.paths = {} # Used to save abs paths while displaying filenames
        self.heading('#0', text='Explorer', anchor='w')
        # FOR TESTING
        self.add_path(os.path.abspath('Pyssembler/work'))

    def add_path(self, path):
        """
        Adds a directory to the explorer. 
        """
        abspath = os.path.abspath(path)
        root = self.insert('', tk.END, text=path, open=True)
        self.__add_paths(root, abspath)
    
    def update(self):
        """
        Updates the tree view to reflect changes made 
        (creating/deleting files and folders) after initialization
        """
        for item in self.get_children():
            self.delete(item)
        self.paths.clear()
        self.add_path(os.path.abspath('Pyssembler/work'))

    def __add_paths(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            old = self.insert(parent, tk.END, text=p, open=False)
            if os.path.isdir(abspath):
                self.__add_paths(old, abspath)
            else:
                # Is file
                self.paths[old] = abspath


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

    def close_editor_by_path(self, path):
        if path in self.open_editors:
            self.close_editor(self.open_editors[path])

    def close_editor(self, editor):
        if editor.saved:
            self.forget(editor)
            return True
        s = messagebox.askyesnocancel(
            title='Save', message=f'Do you want to save {os.path.basename(editor.path)}?')
        if s is None:
            return False
        if s:
            editor.save()
        self.forget(editor)
        return True
    
    def close_editors(self):
        """
        Close all open editors
        """
        removed = []
        for editor in self.open_editors.values():
            if not self.close_editor(editor):
                # User clicked Cancel, don't exit
                return False
            removed.append(editor.path)
        for p in removed:
            self.open_editors.pop(p)
        return True

    def save_all_editors(self):
        for editor in self.open_editors.values():
            editor.save()

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
            editor = self.nametowidget(self.tabs()[index])
            self.close_editor(editor)
            self.open_editors.pop(editor.path)
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

        self.text.bind('<<Change>>', self._on_change)
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.text.bind('<Configure>', self._on_change)

    def save(self):
        """
        Save the current state of the editor to file at self.path
        """
        with open(self.path, 'w') as f:
            f.write(self.text.get('1.0', tk.END))
        self.saved = True
    
    def save_as(self, path):
        """
        Save the current state of the editor into a new file
        """
        with open(path, 'w') as f:
            f.write(self.text.get('1.0', tk.END))

    def _on_change(self, event=None):
        self.linenums.redraw()
    
    def on_key_release(self, event=None):
        """
        When the user releases a key, perform syntax highlighting
        on that line and set saved status to False
        """
        self.text.highlight_syntax_line()
        self.saved = False

    def __read_file(self):
        with open(self.path) as f:
            self.text.insert(tk.INSERT, f.read())
        self.text.highlight_syntax()
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

        # Set up syntax highlighting tags
        self.tag_config('instr', foreground='dark orange')
        self.tag_config('reg', foreground='dodger blue')
        self.tag_config('comment', foreground='gray47')
        self.tag_config('error', foreground='red')

        # Save regex expressions for syntax highlighting
        self.mnemonic_regex = '|'.join(get_mnemonics())
        self.reg_regex = '|'.join([r.replace("$", "\$") for r in regs.get_names()])

    def remove_highlight_syntax(self):
        start = "1.0"
        end = "end"
        self.tag_remove("comment", start, end)
        self.tag_remove("instr", start, end)
        self.tag_remove("reg", start, end)

    def highlight_syntax(self):
        start = '1.0'
        end = self.index('end')
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        for i in range(1, int(float(end))+1):
            searchStart = self.index('{}.0'.format(i))
            searchEnd = self.index('{} lineend'.format(searchStart))
            self.highlight_syntax_line(searchStart, searchEnd)
    
    def highlight_syntax_line(self, start=None, stop=None):
        if start is None:
            self.mark_set("searchStart", self.index("insert linestart"))
        else:
            self.mark_set('searchStart', start)
        if stop is None:
            self.mark_set("searchEnd", self.index("insert lineend"))
        else:
            self.mark_set('searchEnd', stop)

        # If comment exists, mark everything right of # as comment
        index = self.search('#', 'searchStart', 'searchEnd', regexp=True)
        if index == '':
            self.tag_remove('comment', 'searchStart', 'searchEnd')
        else:
            self.mark_set('matchStart', index)
            self.tag_add('comment', 'matchStart', 'searchEnd')
            self.mark_set('searchEnd', self.index('matchStart'))
        
        # Search for and highlight instruction mnemonics
        # There should only be a max of 1 mnemonic per line,
        # so only highlight first found

        # TODO: Mnemonics surrounded by other chars are getting colored
        # ie .word, or would be found and colored. Need to find solution
        count = tk.IntVar()
        index = self.search(
            self.mnemonic_regex, "searchStart", "searchEnd", count=count, regexp=True
        )
        if index == "":
            self.tag_remove("instr", "searchStart", "searchEnd")
        else:
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
            self.tag_add("instr", "matchStart", "matchEnd")
        
        # Search for and highlight all reg names
        # TODO: Register names surrounded by other chars are getting colored
        # ie abcd$s1abc, $s1 would be found and colored. Need to find solution
        self.tag_remove("reg", "searchStart", "searchEnd")
        while True:
            index = self.search(
                self.reg_regex,
                "searchStart",
                "searchEnd",
                count=count,
                regexp=True,
            )
            if index == "":
                self.tag_remove("reg", "searchStart", "searchEnd")
                break
            else:
                self.mark_set("matchStart", index)
                self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
                self.mark_set("searchStart", "matchEnd+1c")
                self.tag_add("reg", "matchStart", "matchEnd")

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        try:
            # BAND-AID FIX!!!!!!!!!!!!!!!1
            # Copy-Pasting crashes program, most likely due to
            # those events firing first then the selection being
            # removed. Other events could also crash
            # For now just catch and move on with my life
            result = self.tk.call(cmd)
        except:
            return None

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

