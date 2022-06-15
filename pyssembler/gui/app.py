import logging

from PyQt5 import QtCore, QtGui, QtWidgets

import globals
from pyssembler.gui.ide import PyssemblerIDE
from pyssembler.gui.consoles import Consoles
from pyssembler.gui.controller import Controller


class PyssemblerWindow(QtWidgets.QMainWindow):
    """
    The root GUI class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Pyssembler')
        self.settings = QtCore.QSettings(str(globals.SETTINGS_FILE), QtCore.QSettings.IniFormat)
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.__init_ui()
        self.setMinimumSize(1000, 500)

    def __init_ui(self):
        """
        Initialize widgets
        """
        self._log.info('Setting up window...')
        self._log.debug('Creating IDE widget...')
        self.ide = PyssemblerIDE()
        self._log.debug('Creating Console widgets...')
        self.consoles = Consoles()

        self._log.debug('Building window...')
        self.main_splitter = QtWidgets.QSplitter()
        self.main_splitter.setOrientation(QtCore.Qt.Vertical)
        self.main_splitter.addWidget(self.ide)
        self.main_splitter.addWidget(self.consoles)
        self.main_splitter.setSizes([500, 100])

        self.__init_actions()
        self.__init_menu()
        self.__init_shortcuts()

        self.setCentralWidget(self.main_splitter)

        self._restore_state()

        self._log.debug('Creating Controller...')
        self._controller = Controller()
        self._controller.link_main_window(self)
        self._controller.link_ide(self.ide)

        # Connect actions to widget slots
        self._controller.bind()

    def __init_actions(self):
        """
        Initialize actions
        """
        self._log.debug('Creating Actions...')
        # File actions
        self.new_file_action = QtWidgets.QAction('New File', self)
        self.open_file_action = QtWidgets.QAction('Open File', self)
        self.close_file_action = QtWidgets.QAction('Close File', self)
        self.close_all_files_action = QtWidgets.QAction('Close All', self)
        self.save_file_action = QtWidgets.QAction('Save', self)
        self.save_file_as_action = QtWidgets.QAction('Save As', self)

        # Workspace actions
        self.new_workspace_action = QtWidgets.QAction('New Workspace', self)
        self.open_workspace_action = QtWidgets.QAction('Open Workspace', self)
        self.close_workspace_action = QtWidgets.QAction('Close Workspace', self)

        # Pyssembler actions
        self.exit_action = QtWidgets.QAction('Exit', self)
        self.exit_action.triggered.connect(self.close)
        self.settings_action = QtWidgets.QAction('Settings', self)

        # Editor actions
        self.cut_action = QtWidgets.QAction('Cut', self)
        self.copy_action = QtWidgets.QAction('Copy', self)
        self.paste_action = QtWidgets.QAction('Paste', self)
        self.find_action = QtWidgets.QAction('Find', self)
        self.replace_action = QtWidgets.QAction('Replace', self)
        self.undo_action = QtWidgets.QAction('Undo', self)
        self.redo_action = QtWidgets.QAction('Redo', self)
        self.select_all_action = QtWidgets.QAction('Select All', self)

        # Help actions
        self.help_action = QtWidgets.QAction('Help', self)
        self.documentation_action = QtWidgets.QAction('Documentation', self)
        self.report_action = QtWidgets.QAction('Report Bug', self)
        self.about_action = QtWidgets.QAction('About', self)

    def __init_menu(self):
        """
        Initialize menu
        """
        self._log.debug('Creating MenuBar...')
        menubar = self.menuBar()

        # File Menu
        self.file_menu = menubar.addMenu('File')
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.close_file_action)
        self.file_menu.addAction(self.close_all_files_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.new_workspace_action)
        self.file_menu.addAction(self.open_workspace_action)
        self.file_menu.addAction(self.close_workspace_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_file_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Edit Menu
        self.edit_menu = menubar.addMenu('Edit')
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.find_action)
        self.edit_menu.addAction(self.select_all_action)

        # Code Menu
        self.code_menu = menubar.addMenu('Code')

        # Help Menu
        self.help_menu = menubar.addMenu('Help')
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.documentation_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.report_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)

    def __init_shortcuts(self):
        self._log.debug('Setting up Action keybinds...')
        self.settings.beginGroup('keybinds')
        self.new_file_action.setShortcut(QtGui.QKeySequence(self.settings.value('new_file', 'Ctrl+N')))
        self.open_file_action.setShortcut(QtGui.QKeySequence(self.settings.value('open_file', 'Ctrl+O')))
        self.close_file_action.setShortcut(QtGui.QKeySequence(self.settings.value('close_file', 'Ctrl+W')))
        self.save_file_action.setShortcut(QtGui.QKeySequence(self.settings.value('save_file', 'Ctrl+S')))
        self.save_file_as_action.setShortcut(QtGui.QKeySequence(self.settings.value('save_file_as', 'Ctrl+Shift+S')))
        self.undo_action.setShortcut(QtGui.QKeySequence(self.settings.value('undo', 'Ctrl+Z')))
        self.redo_action.setShortcut(QtGui.QKeySequence(self.settings.value('redo', 'Ctrl+Y')))
        self.cut_action.setShortcut(QtGui.QKeySequence(self.settings.value('cut', 'Ctrl+X')))
        self.copy_action.setShortcut(QtGui.QKeySequence(self.settings.value('copy', 'Ctrl+C')))
        self.paste_action.setShortcut(QtGui.QKeySequence(self.settings.value('paste', 'Ctrl+V')))
        self.find_action.setShortcut(QtGui.QKeySequence(self.settings.value('find', 'Ctrl+F')))
        self.select_all_action.setShortcut(QtGui.QKeySequence(self.settings.value('select_all', 'Ctrl+A')))
        self.settings.endGroup()

    def _restore_state(self):
        self._log.debug('Restoring previous state...')
        # Main window size
        self.settings.beginGroup('state/main_window')
        self.resize(self.settings.value('size', QtCore.QSize(400, 400)))
        self.move(self.settings.value('pos', QtCore.QPoint(200, 200)))
        self.settings.endGroup()

        # Main splitter sizes
        sizes = [int(i) for i in self.settings.value('state/main_splitter/sizes', [500, 100])]
        self.main_splitter.setSizes(sizes)

    def _write_state(self):
        self._log.debug('Saving current state...')
        # Main window size
        self.settings.beginGroup('state/main_window')
        self.settings.setValue('size', self.size())
        self.settings.setValue('pos', self.pos())
        self.settings.endGroup()

        # Main splitter sizes
        self.settings.setValue('state/main_splitter/sizes', self.main_splitter.sizes())

        # Keybinds
        self.settings.beginGroup('keybinds')
        self.settings.setValue('new_file', self.new_file_action.shortcut())
        self.settings.setValue('open_file', self.open_file_action.shortcut())
        self.settings.setValue('close_file', self.close_file_action.shortcut())
        self.settings.setValue('save_file', self.save_file_action.shortcut())
        self.settings.setValue('save_file_as', self.save_file_as_action.shortcut())
        self.settings.setValue('undo', self.undo_action.shortcut())
        self.settings.setValue('redo', self.redo_action.shortcut())
        self.settings.setValue('cut', self.cut_action.shortcut())
        self.settings.setValue('copy', self.copy_action.shortcut())
        self.settings.setValue('paste', self.paste_action.shortcut())
        self.settings.setValue('find', self.find_action.shortcut())
        self.settings.setValue('select_all', self.select_all_action.shortcut())
        self.settings.endGroup()

    # --------------------------------------------------------------------
    # Action Slots
    # --------------------------------------------------------------------

    # --------------------------------------------------------------------
    # Events
    # --------------------------------------------------------------------
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._log.debug('User clicked exit! Starting close sequence...')

        # Close any open Editors
        if not self.ide.request_close_all_editors():
            # User cancelled, abort closing
            self._log.debug('User cancelled, aborting close sequence...')
            event.ignore()
            return

        # Save current state
        self._write_state()

        self._log.debug('Goodbye World')
        # Accept event
        event.accept()


def run():
    QtCore.QCoreApplication.setOrganizationName('zschreiner')
    QtCore.QCoreApplication.setOrganizationDomain('zschreiner.dev')
    QtCore.QCoreApplication.setApplicationName('Pyssembler')

    app = QtWidgets.QApplication([])
    app.setApplicationName('Pyssembler')
    window = PyssemblerWindow()
    window.show()
    app.exec()
