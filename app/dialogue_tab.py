import os

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableView, QHeaderView, QFileDialog, QMessageBox,
    QLabel, QSplitter, QTreeView, QAbstractItemView,
    QMenu,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem

from .dialogue_model import DialogueTableModel
from .dialogue_loader import load_dialogues
from .dialogue_tr_store import load_translations, save_translations
from .dialogue_exporter import export_dialogues


class DialogueFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._search_text = ''

    def set_search_text(self, text):
        self._search_text = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if not model or source_row >= len(model.entries):
            return False
        entry = model.entries[source_row]
        text = self._search_text
        if not text:
            return True
        eng = entry['english'].lower()
        trans = model.translations.get(
            f'{model.filename}::{entry["choices_id"]}::{entry["attr"]}', ''
        ).lower()
        return text in eng or text in trans


class DialogueTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.input_folder = None
        self.dialogues_data = []
        self.translations = {}
        self.current_file_idx = -1

        self.table_model = DialogueTableModel(self)
        self.proxy = DialogueFilterProxy(self)
        self.proxy.setSourceModel(self.table_model)
        self.tree_model = QStandardItemModel(self)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.btn_open = QPushButton('📁 Открыть папку dialogues/')
        self.btn_save = QPushButton('💾 Сохранить переводы')
        self.btn_export = QPushButton('▶ Экспорт в dialogues_Rus/')
        self.btn_open.clicked.connect(self._open_folder)
        self.btn_save.clicked.connect(self._save)
        self.btn_export.clicked.connect(self._export)
        self.btn_save.setEnabled(False)
        self.btn_export.setEnabled(False)
        toolbar.addWidget(self.btn_open)
        toolbar.addWidget(self.btn_save)
        toolbar.addWidget(self.btn_export)
        toolbar.addStretch()
        self.lbl_stats = QLabel('Загрузите папку с диалогами')
        toolbar.addWidget(self.lbl_stats)
        layout.addLayout(toolbar)

        filter_bar = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('🔍 Поиск по английскому или переводу...')
        self.search_field.textChanged.connect(self._on_search)
        filter_bar.addWidget(self.search_field, 1)
        layout.addLayout(filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setMinimumWidth(200)
        self.tree_view.clicked.connect(self._on_tree_click)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._tree_context_menu)
        splitter.addWidget(self.tree_view)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(24)
        splitter.addWidget(self.table)

        layout.addWidget(splitter, 1)

    def _open_folder(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку dialogues/', os.getcwd())
        if not path:
            return
        try:
            self.dialogues_data = load_dialogues(path)
            self.input_folder = path
            self.translations = load_translations()
            self._rebuild_tree()
            self.btn_save.setEnabled(True)
            self.btn_export.setEnabled(True)
            total_entries = sum(len(d['entries']) for d in self.dialogues_data)
            self.status_bar.showMessage(f'Загружено {len(self.dialogues_data)} файлов, {total_entries} строк')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить диалоги:\n{e}')

    def _rebuild_tree(self):
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['Dialogues'])
        for i, d in enumerate(self.dialogues_data):
            file_item = QStandardItem(d['filename'])
            file_item.setData(i, Qt.ItemDataRole.UserRole)
            file_item.setEditable(False)
            self.tree_model.appendRow(file_item)

    def _on_tree_click(self, index):
        item = self.tree_model.itemFromIndex(index)
        if item is None:
            return
        file_idx = item.data(Qt.ItemDataRole.UserRole)
        if file_idx is None:
            return
        self.current_file_idx = file_idx
        d = self.dialogues_data[file_idx]
        self.table_model.load(d['entries'], d['filename'], self.translations)
        self._update_stats()

    def _on_search(self, text):
        self.proxy.set_search_text(text)

    def _save(self):
        try:
            save_translations(self.translations)
            self._update_stats()
            self.status_bar.showMessage('Переводы диалогов сохранены')
            QMessageBox.information(self, 'Готово', 'Переводы сохранены в dialogues_translations.json')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сохранении:\n{e}')

    def _export(self):
        if not self.input_folder:
            QMessageBox.warning(self, 'Предупреждение', 'Сначала загрузите папку dialogues/')
            return
        try:
            out_folder = os.path.join(os.path.dirname(self.input_folder), 'dialogues_Rus')
            export_dialogues(self.input_folder, out_folder, self.translations)
            self.status_bar.showMessage(f'Экспорт завершён: {out_folder}')
            QMessageBox.information(self, 'Готово', f'Диалоги экспортированы в {out_folder}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при экспорте:\n{e}')

    def _tree_context_menu(self, pos):
        idx = self.tree_view.indexAt(pos)
        if not idx.isValid():
            return
        item = self.tree_model.itemFromIndex(idx)
        file_idx = item.data(Qt.ItemDataRole.UserRole)
        if file_idx is None:
            return
        menu = QMenu(self)
        show_act = QAction('Показать все строки', self)
        show_act.triggered.connect(lambda: self._show_file(file_idx))
        menu.addAction(show_act)

        open_act = QAction('Открыть исходный XML', self)
        open_act.triggered.connect(lambda: self._open_source(file_idx))
        menu.addAction(open_act)

        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def _show_file(self, file_idx):
        d = self.dialogues_data[file_idx]
        self.current_file_idx = file_idx
        self.table_model.load(d['entries'], d['filename'], self.translations)
        self._update_stats()

    def _open_source(self, file_idx):
        d = self.dialogues_data[file_idx]
        os.startfile(d['path'])

    def _update_stats(self):
        if self.current_file_idx < 0:
            self.lbl_stats.setText('')
            return
        d = self.dialogues_data[self.current_file_idx]
        total = len(d['entries'])
        trans = self.table_model.translated_count()
        self.lbl_stats.setText(f'{d["filename"]} — всего: {total}, ✅ {trans}')
