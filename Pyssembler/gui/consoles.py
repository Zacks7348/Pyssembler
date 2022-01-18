from PyQt5.QtWidgets import QLineEdit, QPlainTextEdit, QTabWidget, QTextEdit, QVBoxLayout, QWidget

class Consoles(QTabWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        # This is just a output for Pyssembler messages
        self._pyssembler_cmd = BaseConsole(input_=False)
        self.addTab(self._pyssembler_cmd, 'Pyssembler CMD')

        # This console handles input and output for MIPS programs
        self._mips_output = BaseConsole()
        self.addTab(self._mips_output, 'MIPS I/O')
    
    def p_message(self, message: str):
        self._pyssembler_cmd.message(message)
    
    def m_message(self, message: str):
        self._mips_output.message(message)


class BaseConsole(QWidget):
    """
    Base class for console objects
    """

    def __init__(self, input_=True):
        super().__init__()

        self._output = QTextEdit()
        self._output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self._output)
        if input_:
            self._input = QLineEdit()
            layout.addWidget(self._input)
        self.setLayout(layout)
    
    def message(self, message: str) -> None:
        self._output.insertPlainText(message+'\n')
    
    
