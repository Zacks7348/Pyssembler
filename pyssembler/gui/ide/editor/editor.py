import logging
import math
from pathlib import Path
import re
import string
from typing import List

from PyQt5 import Qsci, QtCore, QtGui

import globals
from pyssembler.mips import BASIC_INSTRUCTIONS, DIRECTIVES, REGISTERS
from pyssembler.mips.tokenizer import TokenType, Token, VALID_SYMBOL_CHARS, tokenize_text
from pyssembler.mips.assembler import clean_lines, validate_statement
from pyssembler.mips.errors import MIPSSyntaxError, MIPSSyntaxWarning


class Styles:
    DEFAULT_STYLE = 0
    MNEMONIC_STYLE = 1
    REGISTER_STYLE = 2
    DIRECTIVE_STYLE = 3
    STRING_STYLE = 4
    CHAR_STYLE = 5
    COMMENT_STYLE = 6


class Indicators:
    ERROR_INDICATOR = 0


class Editor(Qsci.QsciScintilla):

    def __init__(self, path, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path: Path = path
        self._manager = manager
        self._settings = QtCore.QSettings(str(globals.SETTINGS_FILE), QtCore.QSettings.IniFormat)
        self._saved: bool = True if self.path else False
        self._line_nums_width: int = 2
        self._notify_manager: bool = False

        self.setUtf8(True)
        self.standardCommands()

        self.__init_indicators()
        self.__init_ui()
        self.load_file()

        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def __init_ui(self):

        # Line numbers margin
        self.setMarginType(0, Qsci.QsciScintilla.NumberMargin)
        self.setMarginWidth(0, '0' * self._line_nums_width)

        # Symbols margin
        # self.setMarginType(1, Qsci.QsciScintilla.SymbolMargin)
        # self.setMarginWidth(1, '00000')
        # self.breakpoint_img = QtGui.QImage("red_dot.png").scaled(QtGui.QSize(16, 16))
        # self.markerDefine(self.breakpoint_img, 1)

        # Signals
        self.textChanged.connect(self._on_text_change)

        # EOL
        self.setEolMode(Qsci.QsciScintilla.EolUnix)
        self.setEolVisibility(False)

        # Text Wrapping
        self.setWrapMode(Qsci.QsciScintilla.WrapWord)
        self.setWrapVisualFlags(Qsci.QsciScintilla.WrapFlagByText)
        self.setWrapIndentMode(Qsci.QsciScintilla.WrapIndentIndented)

        # Indentation
        self.setIndentationsUseTabs(True)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)

        # Caret
        self.setCaretForegroundColor(QtGui.QColor('#ff0000ff'))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor('#1f0000ff'))
        self.setCaretWidth(2)

        # Autocompletion
        self.setAutoCompletionSource(Qsci.QsciScintilla.AcsAPIs)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(False)
        self.setAutoCompletionUseSingle(Qsci.QsciScintilla.AcusNever)

        # Call tips
        self.setCallTipsStyle(Qsci.QsciScintilla.CallTipsNone)

        # Lexer
        self._lexer = MIPSLexer(self, self.path)
        self.setLexer(self._lexer)
        self._lexer.setEnabled(False)

    @property
    def saved(self):
        return self._saved

    def save(self, path=None):
        """
        Save this editor
        """
        path = path or self.path
        with path.open('w') as f:
            f.write(self.text())
        self._saved = True

    def load_file(self):
        if not self.path:
            return
        with self.path.open('r') as f:
            text = f.read()
            if len(text) < 10000:
                self._lexer.setEnabled(True)
            self.setText(text)
        self._saved = True
        self._notify_manager = True

    def _on_text_change(self):
        # Update line numbers width
        n = int(math.log10(self.lines())) + 2
        if n != self._line_nums_width:
            self._line_nums_width = n
            self.setMarginWidth(0, '0' * self._line_nums_width)
        if self._notify_manager:
            self._manager.on_editor_update(self)
            self._saved = False

    def __init_indicators(self):
        # Error Indicator
        self.indicatorDefine(Qsci.QsciScintilla.SquiggleIndicator, Indicators.ERROR_INDICATOR)
        self.setIndicatorForegroundColor(QtGui.QColor(255, 0, 0), Indicators.ERROR_INDICATOR)
        self.setIndicatorDrawUnder(True, Indicators.ERROR_INDICATOR)
        self.setIndicatorHoverStyle(Qsci.QsciScintilla.StraightBoxIndicator, Indicators.ERROR_INDICATOR)
        self.setIndicatorHoverForegroundColor(QtGui.QColor(255, 0, 0, 10), Indicators.ERROR_INDICATOR)


class MIPSLexer(Qsci.QsciLexerCustom):
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
        self.setStyling(len(bytearray(text, 'utf-8')), Styles.DEFAULT_STYLE)

    def styleText(self, start, end):
        if not self._enabled:
            return
        # Clear indicators
        self.clear_indicator(start, end - start, Indicators.ERROR_INDICATOR)

        # Syntax Highlighting
        self.startStyling(start)
        text = self.parent().text()[start:end]
        start_line = 0
        if start > 0:
            start_line = self.parent().lineIndexFromPosition(start)[0]
        styles = {
            TokenType.COMMENT: Styles.COMMENT_STYLE,
            TokenType.ASCII: Styles.STRING_STYLE,
            TokenType.CHAR: Styles.CHAR_STYLE,
            TokenType.MNEMONIC: Styles.MNEMONIC_STYLE,
            TokenType.DIRECTIVE: Styles.DIRECTIVE_STYLE,
            TokenType.REGISTER: Styles.REGISTER_STYLE,
        }

        lines = tokenize_text(text, line_offset=start_line, char_offset=start, filename=self.filename)
        # Apply styles
        for line in lines:
            if not line:
                continue
            for token in line:
                if token.type == TokenType.UNKNOWN:
                    self.set_indicator(token.char, token.length(), 1, Indicators.ERROR_INDICATOR)
                else:
                    self.setStyling(token.raw_length(), styles.get(token.type, Styles.DEFAULT_STYLE))

        # Validate statements
        try:
            statements = clean_lines(lines)
            for statement in statements:
                try:
                    validate_statement(statement)
                except MIPSSyntaxError as e:
                    self.set_indicator(e.token.char, e.token.length(), 1, Indicators.ERROR_INDICATOR)
        except MIPSSyntaxError as e:
            self.set_indicator(e.token.char, e.token.length(), 1, Indicators.ERROR_INDICATOR)

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
        # Font
        self._settings.beginGroup('editor')
        font = QtGui.QFont()
        font.setFamily(self._settings.value('name', 'Courier'))
        font.setPointSize(int(self._settings.value('size', 14)))
        font.setWeight(int(self._settings.value('weight', -1)))
        font.setItalic(bool(self._settings.value('italics', False)))
        self._settings.endGroup()

        self.setDefaultColor(QtGui.QColor('#ff000000'))
        self.setDefaultPaper(QtGui.QColor('#ffffffff'))

        # Default Style
        self.__init_style('#ff000000', '#ffffffff', font, Styles.DEFAULT_STYLE)

        # Mnemonic Style
        self.__init_style('#00ff8c00', '#ffffffff', font, Styles.MNEMONIC_STYLE)

        # Register Style
        self.__init_style('#001e90ff', '#ffffffff', font, Styles.REGISTER_STYLE)

        # Directive Style
        self.__init_style('#00800080', '#ffffffff', font, Styles.DIRECTIVE_STYLE)

        # String Style
        self.__init_style('#006b8e23', '#ffffffff', font, Styles.STRING_STYLE)

        # Char Style
        self.__init_style('#006b8e23', '#ffffffff', font, Styles.CHAR_STYLE)

        # Comment Style
        self.__init_style('#008c8c8c', '#ffffffff', font, Styles.COMMENT_STYLE)

    def __init_style(self, text_color, paper_color, font, style):
        self.setColor(QtGui.QColor(text_color), style)
        self.setPaper(QtGui.QColor(paper_color), style)
        self.setFont(font, style)

