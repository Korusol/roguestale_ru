from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMessageBox, QApplication,
)
from PySide6.QtGui import QAction, QKeySequence

from .string_table_tab import StringTableTab
from .dialogue_tab import DialogueTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Roguetale — Редактор переводов')
        self.resize(1200, 700)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Готов')

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.string_tab = StringTableTab(self.status_bar)
        self.dialogue_tab = DialogueTab(self.status_bar)

        self.tabs.addTab(self.string_tab, '📖 String Table')
        self.tabs.addTab(self.dialogue_tab, '💬 Dialogues')

        self._build_menu()

    def _build_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Файл')

        open_xml_act = QAction('Открыть Russian.xml', self)
        open_xml_act.setShortcut(QKeySequence('Ctrl+O'))
        open_xml_act.triggered.connect(self.string_tab._open_xml)
        file_menu.addAction(open_xml_act)

        open_txt_act = QAction('Открыть .txt переводов', self)
        open_txt_act.setShortcut(QKeySequence('Ctrl+T'))
        open_txt_act.triggered.connect(self.string_tab._open_txt)
        file_menu.addAction(open_txt_act)

        save_act = QAction('Сохранить String Table', self)
        save_act.setShortcut(QKeySequence('Ctrl+S'))
        save_act.triggered.connect(self.string_tab._save)
        file_menu.addAction(save_act)

        file_menu.addSeparator()

        open_dlg_act = QAction('Открыть папку dialogues/', self)
        open_dlg_act.setShortcut(QKeySequence('Ctrl+D'))
        open_dlg_act.triggered.connect(self.dialogue_tab._open_folder)
        file_menu.addAction(open_dlg_act)

        save_dlg_act = QAction('Сохранить переводы диалогов', self)
        save_dlg_act.triggered.connect(self.dialogue_tab._save)
        file_menu.addAction(save_dlg_act)

        export_dlg_act = QAction('Экспорт диалогов в dialogues_Rus/', self)
        export_dlg_act.triggered.connect(self.dialogue_tab._export)
        file_menu.addAction(export_dlg_act)

        file_menu.addSeparator()

        exit_act = QAction('Выход', self)
        exit_act.setShortcut(QKeySequence('Ctrl+Q'))
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        help_menu = menubar.addMenu('Помощь')
        about_act = QAction('О программе', self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _show_about(self):
        QMessageBox.about(
            self, 'О программе',
            'Редактор переводов для Roguetale\n\n'
            'Загружайте Russian.xml + Russian.xml.txt, редактируйте '
            'переводы в таблице, сохраняйте — XML обновится автоматически.\n\n'
            'Для диалогов: открывайте папку dialogues/, переводите, '
            'экспортируйте в dialogues_Rus/.'
        )
