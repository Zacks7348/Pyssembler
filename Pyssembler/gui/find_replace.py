from PyQt5 import QtWidgets, QtGui

import re

class FindReplaceDialog(QtWidgets.QDialog):
    def __init__(self, editors) -> None:
        super().__init__()
        self.editors = editors

        self.setWindowTitle('Find/Replace')
        self.__init_ui()
        self.last_match = None
    
    def __init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()
        self.find_input = QtWidgets.QLineEdit()
        form_layout.addRow(QtWidgets.QLabel('Find'), self.find_input)
        self.replace_input = QtWidgets.QLineEdit()
        form_layout.addRow(QtWidgets.QLabel('Replace'), self.replace_input)
        main_layout.addLayout(form_layout)

        button_layout = QtWidgets.QHBoxLayout()
        self.find_button = QtWidgets.QPushButton('Find')
        self.find_button.clicked.connect(self.on_find)
        button_layout.addWidget(self.find_button)
        self.replace_button = QtWidgets.QPushButton('Replace')
        self.replace_button.clicked.connect(self.on_replace)
        button_layout.addWidget(self.replace_button)
        self.replace_all_button = QtWidgets.QPushButton('Replace All')
        self.replace_all_button.clicked.connect(self.on_replace_all)
        button_layout.addWidget(self.replace_all_button)
        main_layout.addLayout(button_layout)

        opt_layout = QtWidgets.QHBoxLayout()
        self.match_case = QtWidgets.QCheckBox('Match Case')
        opt_layout.addWidget(self.match_case)
        self.whole_word = QtWidgets.QCheckBox('Whole Word')
        opt_layout.addWidget(self.whole_word)
        self.reg = QtWidgets.QCheckBox('Regex')
        self.reg.stateChanged.connect(self.on_reg_change)
        opt_layout.addWidget(self.reg)
        main_layout.addLayout(opt_layout)

        self.setLayout(main_layout)
    
    def on_find(self):
        editor = self.editors.current_editor
        text = editor.toPlainText()
        query = self.find_input.text()

        if self.whole_word.isChecked():
            query = r'\W'+query+r'\W'
        flags = 0 if self.match_case.isChecked() else re.I
        pattern = re.compile(query,flags)

        # If last match successful, start at position after
        start = self.last_match.start() + 1 if self.last_match else 0

        self.last_match = pattern.search(text, start)
        if self.last_match:
            start, end = self.last_match.start(), self.last_match.end()
            # If Whole Word Search, need to remove \W chars
            if self.whole_word.isChecked():
                start += 1
                end -= 1
            self.move_cursor(start, end)
    
    def on_replace(self):
        editor = self.editors.current_editor
        cursor = editor.textCursor()
        if self.last_match and cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            editor.setTextCursor(cursor)

    def on_replace_all(self):
        self.last_match = None # Start search at start
        self.on_find() # Get first match in last_match

        while self.last_match:
            self.on_replace()
            self.on_find()
    
    def on_reg_change(self, state):
        state = not state
        if state:
            self.whole_word.setChecked(False)
            self.match_case.setChecked(False)
        self.whole_word.setEnabled(state)
        self.match_case.setEnabled(state)

    
    def move_cursor(self, start, end):
        cursor = self.editors.current_editor.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end-start)
        self.editors.current_editor.setTextCursor(cursor)


        



        