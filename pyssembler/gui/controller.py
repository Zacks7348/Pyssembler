from __future__ import annotations
from enum import Enum
import logging
from typing import TYPE_CHECKING

from pyssembler.gui.utils import request_open_file

if TYPE_CHECKING:
    from pyssembler.gui.app import PyssemblerWindow
    from pyssembler.gui.ide import PyssemblerIDE

import globals


class State(Enum):
    HOME = 0
    EDITOR_UNSAVED = 1
    EDITOR_SAVED = 2
    SIMULATOR_HOME = 3
    SIMULATOR_PLAYING = 4
    SIMULATOR_PAUSED = 5
    SIMULATOR_STOPPED = 6


class Controller:
    def __init__(self):
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self._main_window: PyssemblerWindow = None
        self._ide: PyssemblerIDE = None

    def link_main_window(self, window: PyssemblerWindow):
        self._log.info('Linked main window!')
        self._main_window = window

    def link_ide(self, ide: PyssemblerIDE):
        self._log.info('Linked IDE!')
        self._ide = ide

    def bind(self):
        self._log.info('Binding...')
        # Connect signals from main window to other widgets
        self._main_window.new_file_action.triggered.connect(self._ide.request_open_new_editor)
        self._main_window.open_file_action.triggered.connect(self._ide.request_open_editor)
        self._main_window.close_file_action.triggered.connect(self._ide.request_close_editor)
        self._main_window.close_all_files_action.triggered.connect(self._ide.request_close_all_editors)

        self._main_window.save_file_action.triggered.connect(self._ide.request_save_editor)
        self._main_window.save_file_as_action.triggered.connect(self._ide.request_save_as_editor)

        self._main_window.open_workspace_action.triggered.connect(self._ide.request_open_workspace)
        self._main_window.close_workspace_action.triggered.connect(self._ide.request_close_workspace)
