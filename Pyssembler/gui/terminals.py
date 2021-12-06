from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget

class Terminals(QTabWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)