from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QComboBox, 
    QDialog, 
    QFormLayout,
    QHBoxLayout, 
    QLabel,
    QPushButton, 
    QSpinBox, 
    QTabWidget,
    QVBoxLayout, 
    QWidget,
    QFontDialog)


class SettingsWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Settings')
        self.settings = QSettings()
        layout = QVBoxLayout()
        self.tabs = SettingsTabs(self.settings)
        layout.addWidget(self.tabs)

        button_layout = QHBoxLayout()
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        default_button = QPushButton('Restore Defaults')
        default_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(default_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_settings(self):
        self.settings.beginGroup('editor')
        self.settings.setValue('font', self.tabs.chosen_font.family())
        self.settings.setValue('fontSize', self.tabs.chosen_font.pointSize())
        self.settings.setValue('syntaxHighlighting', self.tabs.shCombo.currentIndex())
        self.settings.endGroup()
        self.settings.sync()
        self.close()
    
    def restore_defaults(self):
        self.settings.beginGroup('editor')
        self.settings.setValue('font', 'Courier')
        self.settings.setValue('fontSize', 14)
        self.settings.setValue('syntaxHighlighting', 1)
        self.settings.endGroup()
        self.settings.sync()
        self.close()


class SettingsTabs(QTabWidget):
    def __init__(self, settings) -> None:
        super().__init__()
        self.settings = settings
        self.__init_editor_tab()
        self.chosen_font = QFont()
        self.chosen_font.setFamily(str(self.settings.value('editor/fontFamily', 'Courier')))
        self.chosen_font.setPointSize(int(self.settings.value('editor/fontSize', 14)))

    def __init_editor_tab(self):
        self.editor = QWidget()
        editor_form = QFormLayout()

        font_button = QPushButton('Set Font')
        font_button.clicked.connect(self.font_dialog)
        editor_form.addRow(QLabel('Font'), font_button)

        self.shCombo = QComboBox()
        self.shCombo.addItems(['False', 'True'])
        self.shCombo.setCurrentIndex(bool(self.settings.value('editor/syntaxHighlighting', defaultValue=1)))
        editor_form.addRow(QLabel('Syntax Highlighting'), self.shCombo)

        self.editor.setLayout(editor_form)

        self.addTab(self.editor, 'Editor Settings')

    def font_dialog(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.chosen_font = font
