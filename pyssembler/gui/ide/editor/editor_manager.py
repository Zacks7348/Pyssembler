import logging
import math
from pathlib import Path

from PyQt5 import QtCore, QtWidgets, Qsci, QtGui

import globals
from pyssembler.gui import utils
from pyssembler.gui.ide.editor.editor import Editor


class EditorManager(QtWidgets.QTabWidget):
    """
    Manages a set of open editors.
    """

    def __init__(self, ide, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._ide = ide
        self.setTabsClosable(True)
        self._new_name = 'Untitled{}*'
        self._new_cnt = 1
        self._open_editors = []
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self.tabCloseRequested.connect(self._ide.request_close_editor)

    def on_editor_update(self, editor):
        index = self.indexOf(editor)
        name = self.tabText(index)
        if not name.endswith('*'):
            self.setTabText(index, name+'*')

    def open_editor(self, path: Path = None) -> None:
        """
        Open an editor on the file located at path or a new editor if path is None

        :param path: The location of the file to open an editor on (optional)
        :return: None
        """
        if path is None:
            # Open an empty editor
            name = self._new_name.format(self._new_cnt)
            self._log.debug(f'Opening New Editor: {name}...')
            self._new_cnt += 1
        else:
            self._log.debug(f'Opening Editor: {path}...')
            editor = self._get_editor_by_path(path)
            if editor:
                self._log.debug(f'Editor already open on {path}! Setting to current...')
                self.setCurrentWidget(editor)
                return
            name = path.name
        editor = Editor(path, self)
        self.addTab(editor, name)
        self._open_editors.append(editor)
        self.setCurrentWidget(editor)

    def close_editor(self, index=None) -> None:
        """
        Close the editor located at index or currently selected editor if index is None

        :param index: The index of the editor to close (optional)
        :return: None
        """
        if index is None:
            index = self.currentIndex()
        editor = self.widget(index)
        self._open_editors.remove(editor)
        self.removeTab(index)

    def save_editor(self, index=None, path=None) -> None:
        """
        Save the editor located at index or currently select editor if index is None

        Optionally save the editor to a different file located at path

        :param index: The index of the editor to save
        :param path: The path of a different file to save the editor to (optional)
        :return:
        """
        if index is None:
            index = self.currentIndex()
        editor = self.widget(index)
        editor.save(path=path)
        if editor.path is None:
            editor.path = path
        name = self.tabText(index)
        if name.endswith('*'):
            self.setTabText(index, name[:-1])

    def has_open_editor(self) -> bool:
        """
        Returns True if there is an editor currently open
        :return: bool
        """
        return self.currentIndex() != -1

    def is_editor_saved(self, index=None) -> bool:
        """
        Returns True if the currently selected editor is saved
        :return: bool
        """
        if not index:
            index = self.currentIndex()
        return self.widget(index).saved

    def is_editor_new(self, index=None) -> bool:
        """
        Returns True if the currently selected editor is still New
        (has not been written to disk)
        :return: bool
        """
        if not index:
            index = self.currentIndex()
        return self.widget(index).path is None

    def _get_editor_by_path(self, path: Path):
        for editor in self._open_editors:
            if editor.path == path:
                return editor
        return None

