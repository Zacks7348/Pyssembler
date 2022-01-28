import logging

from PyQt5.QtCore import QRegExp, QSettings, QSize, QRect, Qt
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QSyntaxHighlighter, QTextCharFormat, QTextFormat
)
from PyQt5.QtWidgets import (
    QPlainTextEdit, QTabWidget, QMessageBox, QWidget, QTextEdit, QFileDialog,
    QFormLayout, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout
)

from PyQt5 import QtWidgets

from pathlib import Path

from Pyssembler.mips.instructions import get_mnemonics
from Pyssembler.mips.hardware.registers import get_names
from Pyssembler.mips.directives import Directives

__LOGGER__ = logging.getLogger('Pyssembler.GUI')

__WORK_FOLDER__ = str(Path('Pyssembler/work').resolve())


class EditorManager(QTabWidget):
    """
    Manages a set of open editors. 

    When an editor is modified, a * will be appended to
    the tab name, alerting the user that the editor in that tab
    has unsaved changes.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setTabsClosable(True)
        self.editors = []
        self.new_name_fmt = 'Untitled{}.asm*'
        self.new_cnt = 1

        # self.tabCloseRequested.connect(self.close_editor)

    def open_editor(self, path=None):
        """
        Open an editor on the file located at path

        If path is none, creates a new editor with no path. 
        """

        __LOGGER__.debug(f'Opening editor on {path}...')
        if path is None:
            # Create empty editor with no path
            filename = self.new_name_fmt.format(self.new_cnt)
            p = None
            self.new_cnt += 1
        else:
            # Open editor on path
            path = Path(path).resolve()
            # if (p := str(path)) in self.__editors:
            p = str(path)
            if self.__select_editor_by_path(p):
                __LOGGER__.debug('Exiting editor already open')
                return
            filename = path.name
        editor = Editor(p, filename, self)
        __LOGGER__.debug('Adding editor to IDE...')
        self.addTab(editor, filename)
        self.editors.append(editor)
        __LOGGER__.debug('Selecting editor...')
        self.setCurrentWidget(editor)

    def close_editor(self, index=None) -> bool:
        """
        Close the editor with index, or close current editor
        if index is None. Returns True if the editor has been closed.
        If the editor has changes and the user clicks cancel, the
        editor will not close and return False.
        """

        if index is None:
            index = self.currentIndex()
        editor = self.widget(index)
        __LOGGER__.debug(f'Closing editor on {editor.path}...')
        if not editor.saved:
            __LOGGER__.debug('Prompting editor save...')
            res = QMessageBox.warning(
                self,
                'Pyssembler',
                f'Do you want to save?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if res == QMessageBox.Cancel:
                __LOGGER__.debug('User canceled, aborting...')
                return False
            if res == QMessageBox.Yes:
                self.save_editor(editor)
        __LOGGER__.debug('Removing editor from IDE...')
        self.removeTab(index)
        if editor in self.editors:
            self.editors.remove(editor)
        return True

    def close_editors(self) -> bool:
        """
        Closes all editors. Returns True if all editors
        were closed. See close_editor() for when editors
        are not closed
        """

        __LOGGER__.debug('Closing all open editors...')
        while self.count() > 0:
            if not self.close_editor():
                __LOGGER__.debug('Closing all open editors cancelled!')
                return False
        return True

    def save_editor(self, editor=None):
        """
        Saves an editor. If no editor is passed, saves the selected editor
        """
        if not editor:
            if not (editor := self.widget(self.currentIndex())):
                return
        __LOGGER__.debug(f'Saving editor on {editor.path}...')
        update = not editor.path
        editor.save()
        index = self.indexOf(editor)
        if update and editor.path:
            self.setTabText(index, Path(editor.path).name)
        # If tab text ends with a *, remove the *
        if (name := self.tabText(index)).endswith('*'):
            self.setTabText(index, name[:-1])

    def save_editor_as(self, path):
        editor = self.widget(self.currentIndex())
        __LOGGER__.debug(f'Saving editor on {editor.path} to {path}...')
        editor.save_as(path)

    def save_all_editors(self):
        __LOGGER__.debug('Saving all open editors...')
        for editor in self.editors.values():
            editor.save()

    def get_current_path(self):
        """
        Returns the path of the selected editor if any
        """
        editor = self.currentWidget()
        if not editor:
            return None
        return editor.path

    def on_editor_change(self, editor):
        index = self.indexOf(editor)
        if not (name := self.tabText(index)).endswith('*'):
            self.setTabText(index, name+'*')

    def undo_editor(self):
        """
        Performs an Undo operation on the current editor
        """
        if not (editor := self.widget(self.currentIndex())):
            return
        editor.undo()

    def redo_editor(self):
        """
        Performs a Redo operation on the current editor
        """
        if not (editor := self.widget(self.currentIndex())):
            return
        editor.redo()

    def __select_editor_by_path(self, path):
        for editor in self.editors:
            if editor.path == path:
                self.setCurrentWidget(editor)
                return True
        return False

    @property
    def current_editor(self) -> 'Editor':
        return self.widget(self.currentIndex())


class LineNumbers(QWidget):
    """
    The Line Numbers displayed in the editor
    """

    def __init__(self, editor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_nums_width(), 0)

    def paintEvent(self, event) -> None:
        self.editor.line_nums_paint_event(event)


class Editor(QPlainTextEdit):
    """
    A Text Editor for a file located at path
    """

    def __init__(self, path, name, manager) -> None:
        super().__init__()
        self.manager = manager
        self.settings = QSettings()
        self.line_nums = LineNumbers(self)
        self.path = path
        self.name = name
        self.saved = True

        # Apply settings
        font = QFont()
        font.setFamily(str(self.settings.value('editor/font', 'Courier')))
        font.setPointSize(int(self.settings.value('editor/fontSize', 14)))
        self.setFont(font)

        self.do_sh = bool(self.settings.value(
            'editor/syntaxHighlighting', True))

        self.blockCountChanged.connect(self.update_line_nums_width)
        self.updateRequest.connect(self.update_line_nums)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.highlighter = MIPSSyntaxHighlighter(self.document())
        self.__read_file()

        self.textChanged.connect(self.__on_text_change)

    def save(self):
        if not self.path:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            filename, _ = QFileDialog.getSaveFileName(
                self,
                'Save File',
                __WORK_FOLDER__,
                'ASM Files (*.asm)',
                options=options)
            if not filename:
                return
            self.path = filename
        with open(self.path, 'w') as f:
            f.write(self.toPlainText())
        self.saved = True

    def save_as(self, path):
        """
        Save contents of editor to new path
        """
        with open(path, 'w') as f:
            f.write(self.toPlainText())

    def __read_file(self):
        if not self.path:
            self.saved = False
            return
        with open(self.path, 'r') as f:
            self.setPlainText(f.read())
        self.saved = True

    def __on_text_change(self):
        self.saved = False
        self.manager.on_editor_change(self)

    def line_nums_width(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 10 + self.fontMetrics().width('9') * digits
        return space

    def update_line_nums_width(self, _):
        self.setViewportMargins(self.line_nums_width(), 0, 0, 0)

    def update_line_nums(self, rect, dy):

        if dy:
            self.line_nums.scroll(0, dy)
        else:
            self.line_nums.update(0, rect.y(), self.line_nums.width(),
                                  rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_nums_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_nums.setGeometry(QRect(cr.left(), cr.top(),
                                         self.line_nums_width(), cr.height()))

    def line_nums_paint_event(self, event):
        mypainter = QPainter(self.line_nums)

        # mypainter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(
            block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                mypainter.setPen(Qt.lightGray)
                mypainter.drawText(0, top, self.line_nums.width() - 10, height,
                                   Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor(220, 220, 200)  # Gainsboro

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)


class MIPSSyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, parent):
        super().__init__(parent)

        # Mnemonics
        mnemonic_format = QTextCharFormat()
        mnemonic_format.setForeground(QColor(255, 140, 0))  # dark orange
        self.rules = [(QRegExp(f'\\b{m}\\b'), mnemonic_format)
                      for m in sorted(get_mnemonics())]

        # Registers
        reg_format = QTextCharFormat()
        reg_format.setForeground(QColor(30, 144, 255))  # dodger blue
        self.rules += [(QRegExp('{}'.format(reg.replace('$', '\$'))),
                        reg_format) for reg in get_names()]

        # Directives
        dir_format = QTextCharFormat()
        dir_format.setForeground(QColor(128, 0, 128))  # purple
        self.rules += [(QRegExp('{}'.format(d.replace('.', '\.'))), dir_format)
                       for d in Directives.get_directives()]

        # Double Quoted String
        str_format = QTextCharFormat()
        str_format.setForeground(QColor(107, 142, 35))  # olive drab
        self.rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), str_format))

        # Single Quoted Characters
        # TODO

        # Integers
        # TODO

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(Qt.darkGray)
        self.rules.append((QRegExp('#[^\n]*'), comment_format))

    def highlightBlock(self, text: str) -> None:
        for pattern, format_ in self.rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, format_)
                index = pattern.indexIn(text, index+length)


