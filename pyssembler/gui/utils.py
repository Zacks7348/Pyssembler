from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QMessageBox


def request_new_file(parent, title, root,
                     file_filter='ASM files (*.asm);;All files (*)',
                     options=QFileDialog.Options() | QFileDialog.DontUseNativeDialog,
                     default_suffix='.asm'):
    """
    Prompt the user to create a new file

    :param parent: Parent widget
    :param title: The name of the window
    :param file_filter: Types of files to display
    :param root: The path to initially display in the dialog
    :param options: Dialog options
    :param default_suffix: If user does not provide an extension, append
    :return: The path chosen or None if user cancels
    """
    file_dialog = QFileDialog()
    file_dialog.setDefaultSuffix(default_suffix)
    filename, _ = file_dialog.getSaveFileName(
        parent,
        title,
        str(root),
        file_filter,
        options=options)
    if filename:
        # For some reason setting defualt suffix in the file dialog
        # does not add suffix to result. Manually do it
        if not filename.endswith(default_suffix):
            filename += default_suffix
        filename = Path(filename)
    return filename


def request_open_file(parent, title, root,
                      file_filter='ASM files (*.asm);;All files (*)',
                      options=QFileDialog.Options() | QFileDialog.DontUseNativeDialog,
                      default_suffix='.asm'):
    """
    Prompt the user to open a file

    :param parent: Parent widget
    :param title: The name of the window
    :param file_filter: Types of files to display
    :param root: The path to initially display in the dialog
    :param options: Dialog options
    :param default_suffix: If user does not provide an extension, append
    :return: The path chosen or None if user cancels
    """
    file_dialog = QFileDialog()
    file_dialog.setDefaultSuffix(default_suffix)
    filename, _ = file_dialog.getOpenFileName(
        parent,
        title,
        str(root),
        file_filter,
        options=options)
    if filename:
        # For some reason setting defualt suffix in the file dialog
        # does not add suffix to result. Manually do it
        if not filename.endswith(default_suffix):
            filename += default_suffix
        filename = Path(filename).resolve()
    return filename


def request_choose_directory(parent, title, root):
    """
    Prompt the user to choose a directory

    :param parent: Parent widget
    :param title: The name of the window
    :param root: The path to initially display in the dialog
    :return: The path chosen or None if user cancels
    """
    path = QFileDialog.getExistingDirectory(parent, title, str(root))
    if path:
        path = Path(path).resolve()
    return path


def request_choice(parent, title, message,
                   options=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel):
    return QMessageBox.warning(
        parent,
        title,
        message,
        options
    )
