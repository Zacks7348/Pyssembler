from pathlib import Path

from PyQt5.QtWidgets import (
        QAction,
        QApplication, 
        QHBoxLayout, 
        QMainWindow, 
        QVBoxLayout, 
        QWidget,
        QFileDialog
    )

from .editor import EditorManager
from .explorer import Explorer

class PyssemblerWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Pyssembler')
        self.__init_ui()
        self.setMinimumSize(1000, 500)
        self.showMaximized()
    
    def __init_ui(self):
        self.__init_menu()
        self.ide = IDE()
        self.open_action.triggered.connect(self.ide.open_file)
        self.setCentralWidget(self.ide)



    def __init_menu(self):
        # Create MenuBar
        menubar = self.menuBar()

        # File Menu
        self.file_menu = menubar.addMenu('File')
        self.new_action = self.file_menu.addAction('New File')
        self.open_action = self.file_menu.addAction('Open File')
        self.close_action = self.file_menu.addAction('Close File')
        self.file_menu.addSeparator()
        self.save_action = self.file_menu.addAction('Save')
        self.save_as_action = self.file_menu.addAction('Save As')
        self.save_all_action = self.file_menu.addAction('Save All')
        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction('Exit')
        self.file_menu.addSeparator()
        self.settings_action = self.file_menu.addAction('Settings')

        # Edit Menu
        self.edit_menu = menubar.addMenu('Edit')
        self.cut_action = self.edit_menu.addAction('Cut')
        self.copy_action = self.edit_menu.addAction('Copy')
        self.paste_action = self.edit_menu.addAction('Paste')
        self.edit_menu.addSeparator()
        self.find_action = self.edit_menu.addAction('Find')
        self.replace = self.edit_menu.addAction('Replace')
        self.select_all_action = self.edit_menu.addAction('Select All')

        # Simulation
        self.sim_action = menubar.addAction('Simulate')

        # Help Menu
        self.help_menu = menubar.addMenu('Help')
        self.help_action = self.help_menu.addAction('Help')
        self.help_menu.addSeparator()
        self.report_issue_action = self.help_menu.addAction('Report Issue')
        self.help_menu.addSeparator()
        self.about_action = self.help_menu.addAction('About')

class IDE(QWidget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__root_path = str(Path('Pyssembler/work').resolve())
        layout = QHBoxLayout()
        self.explorer = Explorer()
        self.editor_manager = EditorManager()
        layout.addWidget(self.explorer, stretch=0)
        layout.addWidget(self.editor_manager, stretch=1)
        self.setLayout(layout)
    
    def new_file(self):
        pass

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            'Open File', 
            self.__root_path, 
            'All Files (*);;ASM Files (*.asm)',
            options=options)
        if filename:
            self.editor_manager.open_editor(filename)

    def close_file(self):
        pass


def run_application():
    app = QApplication([])
    app.setApplicationName('Pyssembler')
    window = PyssemblerWindow()
    window.show()
    app.exec()


