import tkinter as tk
from tkinter import filedialog
import logging
import os

from .menus import MenuRibbon
from .editor import IDEPage
from .cmd import CommandLine
import config

LOGGER = logging.getLogger('Pyssembler')

class PyssemblerApp:
    """
    Represents the Pyssembler GUI. 
    """

    def __init__(self) -> None:
        # Configure root
        self.root = tk.Tk()
        self.root.title('Pyssembler')
        self.root.minsize(1000, 500)
        self.root.state('zoomed')

        self.__init_virt_events()
        self.__init_ui()
    
    def __init_ui(self):
        self.menu = MenuRibbon(self.root)
        self.ide = IDEPage(self.root)
        self.cmds = CommandLine(self.root)

        self.ide.place(relheight=0.8, relwidth=1)
        self.cmds.place(relheight=0.2, rely=0.8, relwidth=1)

        self.root.protocol('WM_DELETE_WINDOW', self.__exit)

        # Bind Virtual Events
        self.root.bind('<<Pyssembler_NewFile>>', self.__new_file)
        self.root.bind('<<Pyssembler_OpenFile>>', self.__open_file)
        self.root.bind('<<Pyssembler_Save>>', self.__save)
        self.root.bind('<<Pyssembler_SaveAs>>', self.__save_as)
        self.root.bind('<<Pyssembler_SaveAll>>', self.__save_all)
        self.root.bind('<<Pyssembler_Exit>>', self.__exit)
        self.root.bind('<<Pyssembler_SettingsUpdate>>', self.__config_update)

    def __init_virt_events(self):
        """
        Add Pyssembler virtual events to root
        """
        self.virt_events = (
            '<<Pyssembler_NewFile>>', 
            '<<Pyssembler_OpenFile>>', 
            '<<Pyssembler_CloseFile>>', 
            '<<Pyssembler_Save>>', 
            '<<Pyssembler_SaveAs>>', 
            '<<Pyssembler_SaveAll>>',
            '<<Pyssembler_Exit>>',
            '<<Pyssembler_SettingsUpdate>>')
        for e in self.virt_events:
            self.root.event_add(e, 'None')
    
    def __new_file(self, event=None):
        """
        Prompts user to create a new file. If a file was created, 
        open an editor on it
        """
        path = filedialog.asksaveasfilename(
                initialdir=os.getcwd()+'/Pyssembler/work',
                title='New File',
                filetypes=(("asm files", "*.asm"),("all files", "*.*")),
                defaultextension="*.asm"
        )
        if not path: return
        LOGGER.debug(f'Creating new file {path}...')
        open(path, 'w').close()
        LOGGER.debug('Created file!')
        LOGGER.debug(f'Opening editor on {path}...')
        self.ide.editor.open_editor(path)
        LOGGER.debug('Opened editor!')
        self.ide.explorer.update()
    
    def __open_file(self, event=None):
        """
        Prompts user to choose a file to open. If a file is selected,
        open an editor on it
        """
        path = filedialog.askopenfilename(
            initialdir=os.getcwd()+'/Pyssembler/work',
            title='Open File',
            filetypes=(('asm files', '*.asm'), ('all files', '*.*')),
            defaultextension='*.asm'
        )
        if not path: return
        LOGGER.debug(f'Opening editor on {path}...')
        self.ide.editor.open_editor(path)
        LOGGER.debug('Opened editor!')
    
    def __save(self, event=None):
        """
        Tell the IDE to save the selected editor
        """
        LOGGER.debug('Saving...')
        self.ide.save()
        LOGGER.debug('Saved!')
    
    def __save_as(self, event=None):
        """
        Tell the IDE to save the selected editor as a new file and
        open a editor on the new file
        """
        path = filedialog.asksaveasfilename(
            initialdir=os.getcwd()+'/Pyssembler/work',
            title='New File',
            filetypes=(("asm files", "*.asm"),("all files", "*.*")),
            defaultextension="*.asm"
        )
        if not path: return
        LOGGER.debug(f'Saving to {path}...')
        self.ide.save_as()
        LOGGER.debug('Saved!')
        self.ide.explorer.update()
    
    def __save_all(self, event=None):
        LOGGER.debug('Saving...')
        self.ide.editor.save_all_editors()
        LOGGER.debug('Saved!')

    def __exit(self, event=None):
        LOGGER.debug('Exiting application...')
        if not self.ide.editor.close_editors():
            LOGGER.debug('Aborted exit')
            return
        LOGGER.debug('Commiting suicide')
        self.root.destroy()

    def __config_update(self, event=None):
        self.ide.editor.update_config()


    def run(self):
        LOGGER.debug('Starting GUI Application...')
        self.root.mainloop()
        LOGGER.debug('Exited GUI loop')
