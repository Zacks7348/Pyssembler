from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel
from PyQt5.QtWidgets import QFileSystemModel, QTreeView

from pathlib import Path

class Explorer(QTreeView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        model = QFileSystemModel()
        model.setNameFilters(['*.asm'])
        model.setNameFilterDisables(False)
        index = model.setRootPath(str(Path.cwd()))
        self.setModel(model)
        self.setRootIndex(index)

        self.setIndentation(20)
        self.setHeaderHidden(True)
        self.setSortingEnabled(True)
        for i in range(1, 4):
            self.hideColumn(i)
        
