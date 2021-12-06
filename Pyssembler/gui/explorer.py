from PyQt5.QtWidgets import QFileSystemModel, QTreeView

from pathlib import Path

class Explorer(QTreeView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        model = QFileSystemModel()
        index = model.setRootPath('')
        self.setModel(model)
        self.setRootIndex(index)
        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(True)

        for i in range(1, 4):
            self.hideColumn(i)
        