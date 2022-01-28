from pathlib import Path

from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QWidget, QSplitter
from PyQt5.QtCore import Qt

from .editor import EditorManager
from .consoles import Consoles


class IDE(QWidget):
    def __init__(self, consoles) -> None:
        super().__init__()
        self.consoles = consoles
        self.__root_path = str(Path('Pyssembler/work').resolve())
        self.editor_manager = EditorManager()

        layout = QVBoxLayout()
        layout.addWidget(self.editor_manager)
        self.setLayout(layout)

    def new_file(self):
        """
        Opens a new editor
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        filename, _ = QFileDialog.getSaveFileName(
            self,
            'New File',
            self.__root_path,
            'ASM Files (*.asm)',
            options=options)
        if filename:
            open(filename, 'w').close()  # Create file
            self.editor_manager.open_editor(filename)
            return True
        return False

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Open File',
            self.__root_path,
            'ASM Files (*.asm)',
            options=options)
        if filename:
            self.editor_manager.open_editor(filename)
            return True
        return False

    def save_as(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Save As',
            self.__root_path,
            'ASM Files (*.asm)',
            options=options)
        if filename:
            open(filename, 'w').close()  # Create file
            self.editor_manager.save_editor_as(filename)

    @property
    def current_editor(self):
        return self.editor_manager.current_editor
