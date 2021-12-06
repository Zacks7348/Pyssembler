from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QTextFormat
from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget, QMessageBox, QWidget

from pathlib import Path


class EditorManager(QTabWidget):
    """
    Manages a set of open editors
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setTabsClosable(True)
        self.__editors = {} # {path: editor}

        self.tabCloseRequested.connect(self.close_editor)

    def open_editor(self, path):
        """
        Open an editor on the file located at path
        """
        path = Path(path).resolve()
        if (p := str(path)) in self.__editors:
            self.setCurrentWidget(self.__editors[p])
            return
        filename = path.name
        editor = Editor(p)
        self.addTab(editor, filename)
        self.__editors[p] = editor
        self.setCurrentWidget(editor)

    def close_editor(self, index=None):
        """
        Close the editor with index, or close current editor if index is None
        """
        if index is None:
            editor = self.widget(self.currentIndex())
        else:
            editor = self.widget(index)
        if not editor.saved:
            res = QMessageBox.warning(
                self,
                'Pyssembler',
                f'Do you want to save {Path(editor.path).name}?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if res == QMessageBox.Cancel:
                return
            if res == QMessageBox.Yes:
                editor.save()
        self.removeTab(index)
        del self.__editors[editor.path]
    


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

    def __init__(self, path) -> None:
        super().__init__()
        self.line_nums = LineNumbers(self)
        self.path = path
        self.saved = True

        self.blockCountChanged.connect(self.update_line_nums_width)
        self.updateRequest.connect(self.update_line_nums)

        self.__read_file()

        self.textChanged.connect(self.__on_text_change)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(self.toPlainText())

    def __read_file(self):
        with open(self.path, 'r') as f:
            self.setPlainText(f.read())
        self.saved = True

    def __on_text_change(self):
        self.saved = False

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

        cr = self.contentsRect();
        self.line_nums.setGeometry(QRect(cr.left(), cr.top(),
                    self.line_nums_width(), cr.height()))

    def line_nums_paint_event(self, event):
        mypainter = QPainter(self.line_nums)

        #mypainter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
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