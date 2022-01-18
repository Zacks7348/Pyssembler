from PyQt5.QtWidgets import QMessageBox, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget

import Pyssembler as P
__ABOUT__ = """
Pyssembler {version}\tCopyright {copyright}
{author}
Pyssembler is a MIPS32 IDE, Assembler, and Simulator built with python.

This project was inspired by the MARS application by Pete Sanderson and Kenneth Vollmar.
"""


def show_about(parent):
    QMessageBox.about(parent, 'About', __ABOUT__.format(
        version=P.__version__, copyright=P.__copyright__, author=P.__author__))
