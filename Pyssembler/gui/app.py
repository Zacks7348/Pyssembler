from enum import Enum
from json import tool
import logging

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QShortcut, QSplitter,
    QTabWidget, QAction, QFileDialog
)

# Imports custom resources for PyQt5
import resources
import globals

from .ide import IDE
from .consoles import Consoles
from .settings import SettingsWindow
from .simulator import SimulatorWindow, SimulationWorker
from .help import show_about
from .find_replace import FindReplaceDialog

__LOGGER__ = logging.getLogger('Pyssembler.GUI')


class PyssemblerWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Pyssembler')
        self.__init_ui()
        self.setMinimumSize(1000, 500)
        self.showMaximized()

    def __init_ui(self):
        """
        Initialize widgets
        """

        __LOGGER__.debug('Initializing GUI...')
        self.consoles = Consoles()
        self.ide = IDE(self.consoles)
        self.sim = SimulatorWindow(self.consoles)
        self.sim.simulation_finished.connect(self.__on_sim_finish)

        self.main_tabs = QTabWidget(self)
        self.main_tabs.addTab(self.ide, 'Editor')
        self.main_tabs.addTab(self.sim, 'Simulator')
        splitter = QSplitter()
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self.main_tabs)
        splitter.addWidget(self.consoles)
        splitter.setSizes([500, 100])
        self.__init_actions()
        self.__init_menu()
        self.__init_toolbar()
        self.__init_shortcuts()

        self.ide.editor_manager.tabCloseRequested.connect(self.on_close_file)

        self.setCentralWidget(splitter)

    def __init_actions(self):
        """
        Creates all of the main actions
        """

        __LOGGER__.debug('Creating actions...')
        self.new_file_action = QAction(
            QIcon(':/icons/New.png'), 'New File', self)
        self.new_file_action.triggered.connect(self.on_new_file)

        self.open_file_action = QAction(
            QIcon(':/icons/Open.png'), 'Open File', self)
        self.open_file_action.triggered.connect(self.on_open_file)

        self.close_file_action = QAction('Close', self)
        self.close_file_action.triggered.connect(self.on_close_file)

        self.close_all_files_action = QAction('Close All', self)
        self.close_all_files_action.triggered.connect(
            self.on_close_all_files)

        self.save_file_action = QAction(
            QIcon(':/icons/Save.png'), 'Save', self)
        self.save_file_action.triggered.connect(
            self.ide.editor_manager.save_editor)

        self.save_file_as_action = QAction(
            QIcon(':/icons/SaveAs.png'), 'Save As', self)
        self.save_file_as_action.triggered.connect(
            self.ide.save_as)

        self.exit_action = QAction('Exit', self)
        self.exit_action.triggered.connect(self.close)

        self.settings_action = QAction('Settings', self)
        self.settings_action.triggered.connect(self.on_settings)

        self.cut_action = QAction(QIcon(':/icons/Cut.gif'), 'Cut', self)
        self.cut_action.triggered.connect(
            lambda: self.ide.current_editor.cut())

        self.copy_action = QAction(QIcon(':/icons/Copy.png'), 'Copy', self)
        self.copy_action.triggered.connect(
            lambda: self.ide.current_editor.copy())

        self.paste_action = QAction(QIcon(':/icons/Paste.png'), 'Paste', self)
        self.paste_action.triggered.connect(
            lambda: self.ide.current_editor.paste())

        self.find_action = QAction(
            QIcon(':/icons/Find.png'), 'Find/Replace', self)
        self.find_action.triggered.connect(self.on_find_replace)

        self.select_all_action = QAction('Select All', self)
        self.select_all_action.triggered.connect(
            lambda: self.ide.current_editor.selectAll())

        self.assemble_action = QAction(
            QIcon(':/icons/Assemble.png'), 'Assemble', self)
        self.assemble_action.triggered.connect(self.on_single_file_assemble)

        self.play_sim_action = QAction(
            QIcon(':/icons/Play.png'), 'Play Simulation', self
        )
        self.play_sim_action.triggered.connect(self.__play_sim)

        self.step_sim_forward_action = QAction(
            QIcon(':/icons/Next.png'), 'Step Forward', self
        )
        self.step_sim_forward_action.triggered.connect(self.sim.step_simulation_forward)

        self.step_sim_backwards_action = QAction(
            QIcon(':/icons/Previous.png'), 'Step Back', self
        )

        self.pause_sim_action = QAction(
            QIcon(':/icons/Pause.png'), 'Pause Simulation', self
        )
        self.pause_sim_action.triggered.connect(self.__pause_sim)

        self.stop_sim_action = QAction(
            QIcon(':/icons/Stop.png'), 'Stop Simulation', self
        )
        self.stop_sim_action.triggered.connect(self.__stop_sim)

        self.reset_sim_action = QAction(
            QIcon(':/icons/Reset.png'), 'Reset Simulation', self
        )

        self.help_action = QAction(QIcon(':/icons/Help.png'), 'Help', self)

        self.report_action = QAction('Report Issue', self)

        self.about_action = QAction('About', self)
        self.about_action.triggered.connect(lambda: show_about(self))

        self.undo_action = QAction(QIcon(':/icons/Undo.png'), 'Undo', self)
        self.undo_action.triggered.connect(self.ide.editor_manager.undo_editor)
        self.undo_action.setEnabled(False)

        self.redo_action = QAction(QIcon(':/icons/Redo.png'), 'Redo', self)
        self.redo_action.triggered.connect(self.ide.editor_manager.redo_editor)
        self.redo_action.setEnabled(False)

        self.__set_editor_actions(False)
        self.__set_sim_actions(False)

    def __init_menu(self):
        """
        Initialize the menu bar 
        """

        __LOGGER__.debug('Initializing menu...')
        menubar = self.menuBar()

        # File Menu
        self.file_menu = menubar.addMenu('File')
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.close_file_action)
        self.file_menu.addAction(self.close_all_files_action)
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

        # Simulation
        self.menu_sim_action = menubar.addAction('Simulate')
        self.menu_sim_action.triggered.connect(self.on_single_file_assemble)

        # Help Menu
        self.help_menu = menubar.addMenu('Help')
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.report_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)

    def __init_toolbar(self):
        tool_bar = self.addToolBar('Toolbar')
        tool_bar.addAction(self.new_file_action)
        tool_bar.addAction(self.open_file_action)
        tool_bar.addAction(self.save_file_action)
        tool_bar.addAction(self.save_file_as_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.undo_action)
        tool_bar.addAction(self.redo_action)
        tool_bar.addAction(self.cut_action)
        tool_bar.addAction(self.copy_action)
        tool_bar.addAction(self.paste_action)
        tool_bar.addAction(self.find_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.assemble_action)
        tool_bar.addAction(self.play_sim_action)
        tool_bar.addAction(self.step_sim_forward_action)
        tool_bar.addAction(self.step_sim_backwards_action)
        tool_bar.addAction(self.pause_sim_action)
        tool_bar.addAction(self.stop_sim_action)
        tool_bar.addAction(self.reset_sim_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.help_action)

    def __init_shortcuts(self):
        __LOGGER__.debug('Creating shortcuts...')
        self.new_file_action.setShortcut(QKeySequence('Ctrl+N'))
        self.open_file_action.setShortcut(QKeySequence('Ctrl+O'))
        self.close_file_action.setShortcut(QKeySequence('Ctrl+W'))
        self.save_file_action.setShortcut(QKeySequence('Ctrl+S'))
        self.save_file_as_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        self.undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        self.redo_action.setShortcut(QKeySequence('Ctrl+Y'))
        self.cut_action.setShortcut(QKeySequence('Ctrl+X'))
        self.copy_action.setShortcut(QKeySequence('Ctrl+C'))
        self.paste_action.setShortcut(QKeySequence('Ctrl+V'))
        self.find_action.setShortcut(QKeySequence('Ctrl+F'))
        self.select_all_action.setShortcut(QKeySequence('Ctrl+A'))

    def closeEvent(self, event=None):
        # Perform exit sequence
        __LOGGER__.info('Starting exit sequence...')
        if not self.ide.editor_manager.close_editors():
            # User clicked cancel, stop exit sequence
            __LOGGER__.info('Exit sequence aborted!')
            event.ignore()

        # Exit
        # If SIM thread is running, stop it
        if self.sim.is_thread_running:
            self.sim.stop_simulation()
        __LOGGER__.info('Goodbye world')
        event.accept

    def on_open_file(self):
        """
        Opens an editor in the IDE on a file chosen by the user. 
        """

        if self.ide.open_file():
            self.__set_editor_actions(True)

    def on_new_file(self):
        self.ide.editor_manager.open_editor()
        self.__set_editor_actions(True)

    def on_close_file(self, index=None):
        self.ide.editor_manager.close_editor(index)
        if len(self.ide.editor_manager.editors) == 0:
            self.__set_editor_actions(False)

    def on_close_all_files(self):
        if self.ide.editor_manager.close_editors():
            self.__set_editor_actions(False)

    def on_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.exec()

    def on_single_file_assemble(self):
        main = self.ide.editor_manager.get_current_path()
        if not main:
            return
        res = self.sim.init_sim_env(main)
        if res:
            __LOGGER__.debug('Switching to Simulation window...')
            self.main_tabs.setCurrentIndex(1)  # Switch to sim window
            self.play_sim_action.setEnabled(True)
            self.step_sim_forward_action.setEnabled(True)
            self.reset_sim_action.setEnabled(True)

    def __play_sim(self):
        self.sim.play_simulation()
        self.assemble_action.setEnabled(False)
        self.play_sim_action.setEnabled(False)
        self.step_sim_forward_action.setEnabled(False)
        self.step_sim_backwards_action.setEnabled(False)
        self.reset_sim_action.setEnabled(False)
        self.pause_sim_action.setEnabled(True)
        self.stop_sim_action.setEnabled(True)

    def __stop_sim(self):
        self.sim.stop_simulation()
        self.assemble_action.setEnabled(True)
        self.play_sim_action.setEnabled(False)
        self.step_sim_forward_action.setEnabled(False)
        self.step_sim_backwards_action.setEnabled(False)
        self.reset_sim_action.setEnabled(True)
        self.pause_sim_action.setEnabled(False)
        self.stop_sim_action.setEnabled(False)

    def __pause_sim(self):
        self.sim.pause_simulation()
        self.assemble_action.setEnabled(False)
        self.play_sim_action.setEnabled(True)
        self.step_sim_forward_action.setEnabled(True)
        self.step_sim_backwards_action.setEnabled(True)
        self.reset_sim_action.setEnabled(True)
        self.pause_sim_action.setEnabled(False)
        self.stop_sim_action.setEnabled(True)

    def __reset_sim(self):
        pass

    def __on_sim_finish(self):
        self.assemble_action.setEnabled(True)
        self.play_sim_action.setEnabled(False)
        self.step_sim_forward_action.setEnabled(False)
        self.step_sim_backwards_action.setEnabled(False)
        self.reset_sim_action.setEnabled(False)
        self.pause_sim_action.setEnabled(False)
        self.stop_sim_action.setEnabled(False)

    def on_find_replace(self):
        if self.main_tabs.currentIndex == 1:
            self.main_tabs.setCurrentIndex(0)  # Switch to IDE window
        self.find_replace_window = FindReplaceDialog(self.ide.editor_manager)
        self.find_replace_window.exec()

    def __set_editor_actions(self, b: bool):
        self.close_file_action.setEnabled(b)
        self.close_all_files_action.setEnabled(b)
        self.save_file_action.setEnabled(b)
        self.save_file_as_action.setEnabled(b)
        self.cut_action.setEnabled(b)
        self.copy_action.setEnabled(b)
        self.paste_action.setEnabled(b)
        self.find_action.setEnabled(b)
        self.select_all_action.setEnabled(b)
        self.assemble_action.setEnabled(b)
        self.undo_action.setEnabled(b)
        self.redo_action.setEnabled(b)

    def __set_sim_actions(self, b: bool):
        self.play_sim_action.setEnabled(b)
        self.step_sim_forward_action.setEnabled(b)
        self.step_sim_backwards_action.setEnabled(b)
        self.pause_sim_action.setEnabled(b)
        self.stop_sim_action.setEnabled(b)
        self.reset_sim_action.setEnabled(b)


def run_application():
    __LOGGER__.info('Starting Pyssembler GUI app...')
    QCoreApplication.setOrganizationName('zschreiner')
    QCoreApplication.setOrganizationDomain('zschreiner.dev')
    QCoreApplication.setApplicationName('Pyssembler')
    app = QApplication([])
    __LOGGER__.info('Creating GUI...')
    app.setApplicationName('Pyssembler')
    window = PyssemblerWindow()
    window.show()
    __LOGGER__.info('Running GUI app...')
    app.exec()
