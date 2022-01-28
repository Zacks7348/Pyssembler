import logging

from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget
)


class Consoles(QTabWidget):

    input_recieved = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        # This is just a output for Pyssembler messages
        self._pyssembler_cmd = BaseConsole(input_=False)
        self.addTab(self._pyssembler_cmd, 'Pyssembler CMD')

        # This console handles input and output for MIPS programs
        self._mips_io = BaseConsole()
        self.addTab(self._mips_io, 'MIPS I/O')
        self._mips_io.input.returnPressed.connect(self.__on_mips_input)

    def p_message(self, message: str):
        self._pyssembler_cmd.message(message)
        self.setCurrentIndex(0)

    def m_message(self, message: str):
        self._mips_io.message(message)
        self.setCurrentIndex(1)

    def __on_mips_input(self):
        msg = self._mips_io.input.text()
        self._mips_io.input.clear()
        self.input_recieved.emit(msg)

    def allow_mips_input(self):
        self._mips_io.input.setEnabled(True)

    def disallow_mips_input(self):
        self._mips_io.input.setEnabled(False)


class BaseConsole(QWidget):
    """
    Base class for console objects
    """

    def __init__(self, input_=True):
        super().__init__()

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.output)
        if input_:
            self.input = QLineEdit()
            self.input.setEnabled(False)
            layout.addWidget(self.input)
        self.setLayout(layout)

    def message(self, message: str) -> None:
        self.output.insertPlainText(message)
