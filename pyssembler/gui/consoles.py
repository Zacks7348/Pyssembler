from PyQt5 import QtCore, QtGui, QtWidgets


class Consoles(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Problems console
        # Displays warnings and errors
        self._problems = BaseConsole()
        self.addTab(self._problems, 'Problems')

        # Output console
        # Displays assembler output
        self._output = BaseConsole()
        self.addTab(self._output, 'Output')

        # Terminal console
        # Displays runtime output and captures user input
        self._terminal = BaseConsole()
        self.addTab(self._terminal, 'Terminal')

    def write_problems(self, text):
        self._problems.write(text)

    def write_output(self, text):
        self._output.write(text)

    def write_terminal(self, text):
        self._terminal.write(text)


class BaseConsole(QtWidgets.QWidget):
    """
    Base class for console widgets
    """

    # output signals
    input_recieved = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._text = QtWidgets.QTextEdit()
        self._text.setReadOnly(True)

    def write(self, text):
        self._text.insertPlainText(text)
