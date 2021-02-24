import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import font
from tkinter import ttk
import json

from Pyssembler.settings import Settings
from Pyssembler.environment.cpu import CPU


LANG = "Pyssembler/lib/language/"
MIPS_INSTR = LANG + "instructions.json"
MIPS_REG = LANG + "registers.json"


class Editor(tk.Frame):
    def __init__(self, master=None, manager=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        settings = Settings().editor
        font_settings = (settings["font"], settings["font-size"], "normal")

        self.text = CustomText(self, font=font_settings, wrap=tk.NONE)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.configure(xscrollcommand=self.hsb.set)
        self.linenumbers = TextLineNumbers(self, width=60, bg="grey97")
        self.linenumbers.attach(self.text)

        # Binding events
        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

        # Setup highlighting/syntax
        self.text.tag_config("instr", foreground="dark orange")
        self.text.tag_config("reg", foreground="dodger blue")
        self.text.tag_config("comment", foreground="gray47")
        self.text.tag_config("error", foreground="red")
        self.text.tag_config('warning', foreground='yellow')

        # Packing widgets
        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.text.pack(side="right", fill="both", expand="true")

    def _on_change(self, event):
        self.linenumbers.redraw()

    def update_settings(self, settings):
        editor = settings["editor-settings"]
        font_settings = (editor["font"], editor["font-size"], "normal")
        self.text.configure(font=font_settings)
        self.linenumbers.font = ('Courier', font_settings[1], font_settings[2])
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
        if (
            args[0] in ("insert", "replace", "delete")
            or args[0:3] == ("mark", "set", "insert")
            or args[0:2] == ("xview", "moveto")
            or args[0:2] == ("xview", "scroll")
            or args[0:2] == ("yview", "moveto")
            or args[0:2] == ("yview", "scroll")
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

        #If comment exists, mark it and set searchEnd to start of comment
        index = self.search('#', 'searchStart', 'searchEnd', regexp=True)
        if index == '':
            self.tag_remove('comment', 'searchStart', 'searchEnd')
        else:
            self.mark_set('matchStart', index)
            self.tag_add('comment', 'matchStart', 'searchEnd')
            self.mark_set('searchEnd', self.index('matchStart'))
        
        #Search for and highlight instructions
        count = tk.IntVar()
        instr = []
        with open(MIPS_INSTR) as in_file:
            instr = json.load(in_file)
        index = self.search(
            "|".join(instr), "searchStart", "searchEnd", count=count, regexp=True
        )
        if index == "":
            self.tag_remove("instr", "searchStart", "searchEnd")
        else:
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "{}+{}c".format(index, count.get()))
            self.tag_add("instr", "matchStart", "matchEnd")
        
        # Search for and highlight regs
        reg = []
        with open(MIPS_REG) as in_file:
            reg = list(json.load(in_file).values())
        self.tag_remove("reg", "searchStart", "searchEnd")
        while True:
            index = self.search(
                "|".join(reg).replace("$", "\$"),
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

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        editor = Settings().editor
        self.font = ("Courier", editor["font-size"], "normal")

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(
                1, y, anchor="nw", text=linenum, font=self.font
            )
            i = self.textwidget.index("%s+1line" % i)

    @property
    def offset(self):
        return '{}, 0'.format(self.font_size%14)


class Console(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.text = ScrolledText(
            self,
            text_wrap=None,
            font=("Courier New", 10, "normal"),
            wrap=tk.WORD,
            state="disabled",
        )
        self.text.pack(anchor="nw", fill="both", expand=True)
        self.text.tag_config("info", foreground="lime green")
        self.text.tag_config("warning", foreground="orange")
        self.text.tag_config("error", foreground="red2")

        self.commands = {}
        self.commands[
            "help "
        ] = "get help with all commands. help -command for help with a specfic command"
        self.commands[
            "translate"
        ] = "(-b/-m) translate code in current file. -b for binary conversion and -m for mips conversion"
        self.commands["clear"] = "clears the text editor"
        self.commands["exit"] = "exits program"

    def info(self, message):
        self.__write(message, "info")

    def warning(self, message):
        self.__write(message, "warning")

    def error(self, message):
        self.__write(message, "error")

    def __write(self, message, tag=None):
        self.text.config(state="normal")
        if tag is None:
            self.text.insert(tk.INSERT, message + "\n")
        else:
            self.text.insert(tk.INSERT, message + "\n", tag)
        self.text.config(state="disabled")


class SettingsWindow(tk.Toplevel):
    def __init__(self, manager, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        self.title("Settings")
        self.manager = manager
        current = Settings()
        # Inputs
        self.var = {}
        self.var["editor-settings"] = {
            "font": "Courier",
            "font-size": 14,
            "highlight-syntax": True,
        }
        self.var["simulator-settings"] = {"value-radix": "hex"}

        # Creating Widgets
        # Editor Settings
        editor_font_label = tk.Label(self, text="Font:")
        self.editor_font_combo = ttk.Combobox(
            self, values=font.families(), state="readonly"
        )
        self.editor_font_combo.current(
            list(font.families()).index(current.settings["editor-settings"]["font"])
        )

        editor_font_size_label = tk.Label(self, text="Font size:")
        self.editor_font_size_combo = ttk.Combobox(
            self, values=[i for i in range(10, 51)], state="readonly"
        )
        self.editor_font_size_combo.current(
            current.settings["editor-settings"]["font-size"] - 10
        )

        editor_highlight_label = tk.Label(self, text="Highlight Syntax")
        self.editor_highlight_combo = ttk.Combobox(
            self, values=[False, True], state="readonly"
        )
        self.editor_highlight_combo.current(
            int(current.settings["editor-settings"]["highlight-syntax"])
        )

        # Simulator Settings
        simulator_radix_label = tk.Label(self, text="Value Radix: ")
        self.simulator_radix_combo = ttk.Combobox(
            self, values=['binary', 'decimal', 'hex'], state="readonly"
        )
        index = 0
        if current.simulator["value-radix"] == "decimal":
            index = 1
        elif current.simulator["value-radix"] == 'hex':
            index = 2
        self.simulator_radix_combo.current(index)

        # Action Buttons
        save_button = tk.Button(self, text="Save", command=self._on_save, width=5)
        cancel_button = tk.Button(self, text="Cancel", command=self.on_exit, width=5)
        restore_button = tk.Button(
            self, text="Restore Defaults", command=self.on_restore
        )

        # Grid widgets to self
        tk.Label(self, text="Editor Settings").grid(row=0, column=0, columnspan=2)
        editor_font_label.grid(row=1, column=0)
        self.editor_font_combo.grid(row=1, column=1)
        editor_font_size_label.grid(row=2, column=0)
        self.editor_font_size_combo.grid(row=2, column=1)
        editor_highlight_label.grid(row=3, column=0)
        self.editor_highlight_combo.grid(row=3, column=1)

        tk.Label(self, text="Simulator Settings").grid(row=4, column=0, columnspan=2)
        simulator_radix_label.grid(row=5, column=0)
        self.simulator_radix_combo.grid(row=5, column=1)

        save_button.grid(row=6, column=0, sticky="e")
        cancel_button.grid(row=6, column=1)
        restore_button.grid(row=7, columnspan=2)
        self.grab_set()

    # Button functions
    def _on_save(self):
        self.var["editor-settings"]["font"] = self.editor_font_combo.get()
        self.var["editor-settings"]["font-size"] = int(
            self.editor_font_size_combo.get()
        )
        self.var["editor-settings"]["highlight-syntax"] = (
            self.editor_highlight_combo.get() == "True"
        )
        self.var["simulator-settings"]["value-radix"] = self.simulator_radix_combo.get()
        Settings().rewrite(self.var)
        self.destroy()
        self.manager.update_settings(self.var)

    def on_exit(self):
        self.destroy()

    def on_restore(self):
        Settings().rewrite(self.var)
        self.destroy()
        self.manager.update_settings(self.var)


class Simulation(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        settings = Settings()
        self.title = tk.Label(self, text="Register Values")
        self.CPU = CPU()
        self.registers = {}
        

