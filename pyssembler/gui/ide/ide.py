import logging
from pathlib import Path
from typing import Union

from PyQt5 import QtWidgets, QtCore

import globals
from pyssembler.gui.ide.editor import EditorManager
from pyssembler.gui.ide.explorer import ExplorerView
from pyssembler.gui.utils import request_new_file, request_open_file, request_choice, request_choose_directory


class PyssemblerIDE(QtWidgets.QWidget):
    """
    Manages all widgets that comprise the IDE.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prev_dir = globals.WORK_DIR
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self._log.debug('Creating EditorManager widget...')
        self._editors = EditorManager(self)
        self._explorer = ExplorerView()
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.addWidget(self._explorer)
        splitter.addWidget(self._editors)
        splitter.setSizes([50, 500])
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

        self._explorer.open_file_requested.connect(self.request_open_editor)

    @QtCore.pyqtSlot(Path)
    @QtCore.pyqtSlot()
    def request_open_editor(self, path: Path = None):
        self._log.debug('Requesting Open File...')
        if path is None:
            filename = request_open_file(self, 'Open File', self._prev_dir)
            if filename:
                self._editors.open_editor(path=filename)
                return True
            self._log.debug('User cancelled Open File!')
            return False
        self._editors.open_editor(path=path)
        return True

    @QtCore.pyqtSlot()
    def request_open_new_editor(self):
        self._log.debug('Requesting Open New File...')
        self._editors.open_editor()
        return True

    @QtCore.pyqtSlot()
    def request_save_editor(self, index=None):
        self._log.debug('Requesting Save File...')
        if self._editors.is_editor_new(index=index):
            return self.request_save_as_editor(iindex=index)
        self._editors.save_editor(index=index)
        return True

    @QtCore.pyqtSlot()
    def request_save_as_editor(self, index=None):
        self._log.debug('Requesting Save File As...')
        filename = request_new_file(self, 'Save As', self._prev_dir)
        if filename:
            self._editors.save_editor(index=index, path=filename)
            return True
        return False

    @QtCore.pyqtSlot()
    def request_close_editor(self, index=None):
        self._log.debug('Requesting Close Editor...')
        if not self._editors.is_editor_saved(index=index):
            choice = request_choice(self, 'Close File', 'Do you want to save before closing?')
            if choice == QtWidgets.QMessageBox.Yes:
                res = self.request_save_editor(index=index)
                if res:
                    self._editors.close_editor(index=index)
                    return True
                return False
            if choice == QtWidgets.QMessageBox.Cancel:
                return False
        self._editors.close_editor(index=index)
        return True

    @QtCore.pyqtSlot()
    def request_close_all_editors(self):
        while self._editors.has_open_editor():
            res = self.request_close_editor()
            if not res:
                return False
        return True

    @QtCore.pyqtSlot()
    def request_open_workspace(self):
        self._log.debug('Requesting Open Workspace...')
        path = request_choose_directory(self, 'Open Workspace', self._prev_dir)
        if path:
            self._log.debug(f'Opening workspace: {path}')
            self._explorer.set_workspace(path)
            self._current_workspace = path
            return True
        self._log.debug('User cancelled Open Workspace!')
        return False

    @QtCore.pyqtSlot()
    def request_close_workspace(self):
        self._log.debug('Requesting Close Workspace...')
        self._explorer.clear_workspace()
