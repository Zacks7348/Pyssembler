import logging
import re
import string
from typing import List

from PyQt5 import Qsci, QtCore, QtGui

import globals
from pyssembler.mips import BASIC_INSTRUCTIONS, DIRECTIVES, REGISTERS
from pyssembler.mips.tokenizer import TokenType, Token, VALID_SYMBOL_CHARS, tokenize_text
from pyssembler.mips.assembler import clean_lines, validate_statement
from pyssembler.mips.errors import MIPSSyntaxError, MIPSSyntaxWarning


class MIPSLexer(Qsci.QsciLexerCustom):
    # Styles
    DEFAULT_STYLE = 0
    MNEMONIC_STYLE = 1
    REGISTER_STYLE = 2
    DIRECTIVE_STYLE = 3
    STRING_STYLE = 4
    CHAR_STYLE = 5
    COMMENT_STYLE = 6

    # Indicators
    ERROR_INDICATOR = 0

    def __init__(self, parent, filename):
        super().__init__(parent)
        self.filename = filename
        self._settings = QtCore.QSettings(str(globals.SETTINGS_FILE), QtCore.QSettings.IniFormat)
        self.__init_styles()
        self._enabled = True
        self._regex = r'#.+|".+"|\'.+\'|\$*\.?\w+:?|\s+|\S'
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.__api = Qsci.QsciAPIs(self)

        # Populate API
        for mnemonic in BASIC_INSTRUCTIONS:
            self.__api.add(mnemonic)
        for directive in DIRECTIVES:
            self.__api.add(directive)
        for register in REGISTERS:
            self.__api.add(register)
        self.__api.prepare()

    def setEnabled(self, b):
        self._enabled = b

    def language(self):
        return 'MIPS'

    def description(self, style):
        if style == 0:
            return 'DefaultStyle'
        if style == 1:
            return 'MnemonicStyle'
        if style == 2:
            return 'RegisterStyle'
        if style == 3:
            return 'DirectiveStyle'
        if style == 4:
            return 'StringStyle'
        if style == 5:
            return 'CharStyle'
        if style == 6:
            return 'CommentStyle'

    def clearStyles(self):
        text = self.parent().text()
        self.startStyling(0)
        self.setStyling(len(bytearray(text, 'utf-8')), self.DEFAULT_STYLE)

    def styleText(self, start, end):
        if not self._enabled:
            return
        self.startStyling(start)
        text = self.parent().text()[start:end]
        start_line = 0
        if start > 0:
            start_line = self.parent().lineIndexFromPosition(start)[0]
        styles = {
            TokenType.COMMENT: self.COMMENT_STYLE,
            TokenType.ASCII: self.STRING_STYLE,
            TokenType.CHAR: self.CHAR_STYLE,
            TokenType.MNEMONIC: self.MNEMONIC_STYLE,
            TokenType.DIRECTIVE: self.DIRECTIVE_STYLE,
            TokenType.REGISTER: self.REGISTER_STYLE,
        }

        lines = tokenize_text(text, line_offset=start_line, char_offset=start, filename=self.filename)
        # Apply styles
        for line in lines:
            if not line:
                continue
            for token in line:
                self.setStyling(token.raw_length(), styles.get(token.type, self.DEFAULT_STYLE))

        # Validate statements
        # First clear all indicators
        self.clear_indicator(start, end, self.ERROR_INDICATOR)
        statements = clean_lines(lines)
        for statement in statements:
            try:
                validate_statement(statement)
            except MIPSSyntaxError as e:
                self.set_indicator(e.token.char, e.token.length(), 1, self.ERROR_INDICATOR)
                # print(e.summary, e.token)

    def set_indicator(self, start_pos, length, value, indicator):
        self.parent().SendScintilla(Qsci.QsciScintilla.SCI_SETINDICATORCURRENT, indicator)
        self.parent().SendScintilla(Qsci.QsciScintilla.SCI_SETINDICATORVALUE, value)
        self.parent().SendScintilla(Qsci.QsciScintilla.SCI_INDICATORFILLRANGE, start_pos, length)

    def clear_indicator(self, start_pos, length, indicator):
        self.parent().SendScintilla(Qsci.QsciScintilla.SCI_SETINDICATORCURRENT, indicator)
        self.parent().SendScintilla(Qsci.QsciScintilla.SCI_INDICATORCLEARRANGE, start_pos, length)

    def wordCharacters(self):
        return VALID_SYMBOL_CHARS

    def __get_font(self):
        self._settings.beginGroup('font')
        font = QtGui.QFont()
        font.setFamily(self._settings.value('name', 'Courier'))
        font.setPointSize(int(self._settings.value('size', 14)))
        font.setWeight(int(self._settings.value('weight', -1)))
        font.setItalic(bool(self._settings.value('italics', False)))
        self._settings.endGroup()
        return font

    def __init_styles(self):
        # Default text settings
        self._settings.beginGroup('editor')
        self.setDefaultFont(self.__get_font())

        self.setDefaultColor(QtGui.QColor(self._settings.value('color', '#ff000000')))
        self.setDefaultPaper(QtGui.QColor(self._settings.value('paper', '#ffffffff')))

        self._settings.beginGroup('styles')
        # Default Style
        self._settings.beginGroup('default')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#ff000000')),
            self.DEFAULT_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.DEFAULT_STYLE
        )
        self.setFont(self.__get_font(), self.DEFAULT_STYLE)
        self._settings.endGroup()  # editor/styles/default/

        # Mnemonic Style
        self._settings.beginGroup('mnemonic')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#00ff8c00')),
            self.MNEMONIC_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.MNEMONIC_STYLE
        )
        self.setFont(self.__get_font(), self.MNEMONIC_STYLE)
        self._settings.endGroup()  # editor/styles/mnemonic/

        # Register Style
        self._settings.beginGroup('register')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#001e90ff')),
            self.REGISTER_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.REGISTER_STYLE
        )
        self.setFont(self.__get_font(), self.REGISTER_STYLE)
        self._settings.endGroup()  # editor/styles/register/

        # Directive Style
        self._settings.beginGroup('directive')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#00800080')),
            self.DIRECTIVE_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.DIRECTIVE_STYLE
        )
        self.setFont(self.__get_font(), self.DIRECTIVE_STYLE)
        self._settings.endGroup()  # editor/styles/directive/

        # String Style
        self._settings.beginGroup('string')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#006b8e23')),
            self.STRING_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.STRING_STYLE
        )
        self.setFont(self.__get_font(), self.STRING_STYLE)
        self._settings.endGroup()  # editor/styles/string/

        # Char Style
        self._settings.beginGroup('char')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#006b8e23')),
            self.CHAR_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.CHAR_STYLE
        )
        self.setFont(self.__get_font(), self.CHAR_STYLE)
        self._settings.endGroup()  # editor/styles/char/

        # Comment Style
        self._settings.beginGroup('comment')
        self.setColor(
            QtGui.QColor(self._settings.value('color', '#008c8c8c')),
            self.COMMENT_STYLE
        )
        self.setPaper(
            QtGui.QColor(self._settings.value('paper', '#ffffffff')),
            self.COMMENT_STYLE
        )
        self.setFont(self.__get_font(), self.COMMENT_STYLE)
        self._settings.endGroup()  # editor/styles/comment/

        self._settings.endGroup()  # editor/styles/
        self._settings.endGroup()  # editor/
