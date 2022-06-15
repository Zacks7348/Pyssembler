import logging
from pathlib import Path
from typing import Any, List, Tuple

from PyQt5 import QtWidgets, QtCore, QtGui


__LOGGER__ = logging.getLogger(__name__)


class ExplorerView(QtWidgets.QTreeView):

    open_file_requested = QtCore.pyqtSignal(Path)
    create_path_requested = QtCore.pyqtSignal(Path)
    delete_path_requested = QtCore.pyqtSignal(Path)

    assemble_file_requested = QtCore.pyqtSignal(Path)
    assemble_workspace_requested = QtCore.pyqtSignal(Path)

    # First argument is the path
    # Second argument is flag to run in Debug mode
    run_file_requested = QtCore.pyqtSignal(Path, bool)
    run_workspace_requested = QtCore.pyqtSignal(Path, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.__init_actions()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

        self.header().hide()
        self._model = ExplorerModel()
        self.setModel(self._model)

        for i in range(1, self._model.columnCount()):
            self.hideColumn(i)

        self.doubleClicked.connect(self._on_double_click)

    def __init_actions(self):
        self._new_dir_action = QtWidgets.QAction('New Directory')
        self._new_file_action = QtWidgets.QAction('New File')
        self._cut_action = QtWidgets.QAction('Cut')
        self._copy_action = QtWidgets.QAction('Copy')
        self._copy_path_action = QtWidgets.QAction('Copy Path')
        self._paste_action = QtWidgets.QAction('Paste')


    @QtCore.pyqtSlot()
    def set_workspace(self, path: Path):
        self._log.debug(f'Adding workspace {path}...')
        return self._model.set_workspace(path)

    @QtCore.pyqtSlot()
    def clear_workspace(self):
        self._log.debug(f'Clearing workspace...')
        return self._model.clear_workspace()

    def get_selected_paths(self):
        paths = []
        for index in self.selectedIndexes():
            path = index.internalPointer().path
            if path is not None:
                paths.append(path)
        return paths

    def open_menu(self, position: QtCore.QPoint):
        index = self.indexAt(position)
        path = None
        if not index.isValid():
            path = self._model.current_workspace()
        else:
            path = self._model.path(index)
        if path is None:
            # No workspace open
            return
        self._log.debug(f'Opening context menu for path {path}...')

        ctx_menu = QtWidgets.QMenu()
        new_menu = ctx_menu.addMenu('New')
        new_dir_action = new_menu.addAction('Directory')
        new_file_action = new_menu.addAction('File')
        ctx_menu.addSeparator()
        refactor_menu = ctx_menu.addMenu('Refactor')
        rename_action = refactor_menu.addAction('Rename')
        move_action = refactor_menu.addAction('Move')
        safe_delete_action = refactor_menu.addAction('Safe Delete')
        ctx_menu.addSeparator()
        cut_action = ctx_menu.addAction('Cut')
        copy_action = ctx_menu.addAction('Copy')
        copy_path_action = ctx_menu.addAction('Copy Path')
        paste_action = ctx_menu.addAction('Paste')
        ctx_menu.addSeparator()
        find_usages_action = ctx_menu.addAction('Find Usages')

        chosen_action = ctx_menu.exec_(self.viewport().mapToGlobal(position))

    def _on_double_click(self, index: QtCore.QModelIndex):
        path = self._model.path(index)
        self._log.debug(f'Double Click detected: {path}')
        if path is not None:
            self._log.debug(f'Requesting Open File: {path}')
            self.open_file_requested.emit(path)


class ExplorerNode:
    def __init__(self, path: Path, parent: 'ExplorerNode', watcher: QtCore.QFileSystemWatcher = None):
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self._log.debug(f'Generating Tree for path {path}...')
        self.path: Path = path
        self.parent: 'ExplorerNode' = parent
        self.children: List['ExplorerNode'] = []
        self._watcher = watcher

        if self.path is None:
            return

        if self.path.is_dir():
            self._log.debug(f'{path} is a directory! Generating sub-trees for each child...')
            for child in self.path.iterdir():
                self.insert_path(child)
        self._watch_path(self.path)
        self.children.sort(key=lambda c: c.value)

    @property
    def value(self):
        if self.path is None:
            return 'Workspaces'
        return self.path.name

    def insert_path(self, path: Path):
        if self.path is None:
            # Any path can be inserted into root node
            return self._insert_path(path)

        if self.path not in path.parents:
            # path is not a subdirectory of this node
            return None

        if self.path == path.parent:
            # This node is the parent
            return self._insert_path(path)

        for child in self.children:
            node = child.insert_path(path)
            if node is not None:
                return node
        return None

    def _insert_path(self, path: Path):
        self._log.debug(f'Inserting {path} into node {self.path}...')
        node = ExplorerNode(path, self, watcher=self._watcher)
        self.children.append(node)
        self.children.sort(key=lambda c: c.value)
        return node

    def clear(self):
        for child in self.children.copy():
            self._remove_path(child)

    def remove_path(self, path: Path):
        if (self.path is not None) and (self.path not in path.parents):
            return None

        for child in self.children:
            if child.path == path:
                self._remove_path(child)
                return child
        return None

    def _remove_path(self, node: 'ExplorerNode'):
        self._log.debug(f'Removing {node.path} from node {node.path}...')
        self.children.remove(node)
        self._stop_watching_path(node.path)
        # also stop watching children
        for child in node:
            self._stop_watching_path(child.path)

    def child(self, row: int) -> 'ExplorerNode':
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def child_count(self) -> int:
        return len(self.children)

    def row(self) -> int:
        return self.parent.children.index(self)

    def find(self, path: Path):
        if self.path == path:
            return True

        if (self.path is not None) and (self.path not in path.parents):
            return False

        for child in self.children:
            if child.find(path):
                return True
        return False

    def _to_string(self, prefix=''):
        s = f'{prefix}{self.value}\n'
        prefix += '\t'
        for child in self.children:
            s += child._to_string(prefix)
        return s

    def _watch_path(self, path: Path):
        if not path.is_dir() or self._watcher is None:
            return
        self._log.debug(f'Requesting monitoring for {path}...')
        if self._watcher.addPath(str(path)):
            self._log.debug(f'Monitoring {path}!')
        else:
            self._log.debug(f'Monitoring denied for {path}!')

    def _stop_watching_path(self, path: Path):
        if not path.is_dir() or self._watcher is None:
            return
        self._log.debug(f'Requesting to stop monitoring {path}...')
        if self._watcher.removePath(str(path)):
            self._log.debug(f'Stopped monitoring {path}!')
        else:
            self._log.debug(f'Stop monitoring denied for {path}!')

    def __str__(self):
        return self._to_string()

    def __iter__(self):
        yield self
        for child in self.children:
            for item in child:
                yield item


class ExplorerModel(QtCore.QAbstractItemModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        # self._root = ExplorerNode(None, None)
        self._watcher = QtCore.QFileSystemWatcher()
        self._root = ExplorerNode(None, None, watcher=self._watcher)
        self._watcher.directoryChanged.connect(self.on_directory_change)

    def set_workspace(self, path: Path):
        self._root.clear()
        if self._root.insert_path(path):
            # self._watcher.addPath(str(path))
            self.layoutChanged.emit()
            return True
        return False

    def clear_workspace(self):
        self._root.clear()

    def current_workspace(self):
        if self._root.child_count() == 0:
            return None
        return self._root.children[0].path

    def get_open_workspaces(self):
        return [node.path for node in self._root.children]

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = ...) -> QtCore.QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        child = parent.internalPointer().child(row) if parent.isValid() else self._root.child(row)
        if child is not None:
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def parent(self, child: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not child.isValid():
            return QtCore.QModelIndex()
        parent = child.internalPointer().parent
        if parent == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0

        parent_node = parent.internalPointer() if parent.isValid() else self._root
        return parent_node.child_count()

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        # Only 1 column, path name
        return 1

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        return QtCore.QVariant(index.internalPointer().value)

    def path(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return None

        return index.internalPointer().path

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        return super().flags(index)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> Any:
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant('Name')
        return QtCore.QVariant()

    def on_directory_change(self, path: str):
        self._log.debug(f'Detected change in {path}! Regenerating tree...')
        path = Path(path).resolve()
        self._root.remove_path(path)
        self._root.insert_path(path)
        self.layoutChanged.emit()



