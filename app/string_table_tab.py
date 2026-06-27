import os

from PySide6.QtCore import Qt, QSortFilterProxyModel, QStringListModel, QModelIndex
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QComboBox, QTableView, QHeaderView, QFileDialog, QMessageBox,
    QLabel, QStatusBar, QSplitter, QTextEdit, QDialog, QDialogButtonBox,
    QInputDialog, QMenu, QAbstractItemView,
)

from .string_model import StringTableModel, match_cyrillic
from .xml_loader import read_file, parse_string_table
from .txt_loader import parse_txt, export_txt_strings, write_txt
from .xml_exporter import export_xml


class StringFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._section_filter = ''
        self._status_filter = ''  # '', 'translated', 'untranslated'
        self._search_text = ''

    def set_section_filter(self, section):
        self._section_filter = section
        self.invalidateFilter()

    def set_status_filter(self, status):
        self._status_filter = status
        self.invalidateFilter()

    def set_search_text(self, text):
        self._search_text = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if not model or source_row >= len(model.entries):
            return False
        entry = model.entries[source_row]

        if self._section_filter and entry['section'] != self._section_filter:
            return False

        if self._status_filter == 'translated':
            trans = entry.get('_translation', '')
            if not trans or not match_cyrillic(trans):
                return False
        elif self._status_filter == 'untranslated':
            trans = entry.get('_translation', '')
            if trans and match_cyrillic(trans):
                return False

        if self._search_text:
            text = self._search_text
            found = False
            for field in [entry['section'], entry['key'], entry['value'], entry.get('_translation', '')]:
                if text in field.lower():
                    found = True
                    break
            if not found:
                return False

        return True


class StringTableTab(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.xml_path = None
        self.txt_path = None
        self.xml_original_text = None

        self.model = StringTableModel(self)
        self.proxy = StringFilterProxy(self)
        self.proxy.setSourceModel(self.model)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.btn_open_xml = QPushButton('📂 Открыть Russian.xml')
        self.btn_open_txt = QPushButton('📄 Открыть .txt')
        self.btn_save = QPushButton('💾 Сохранить .txt + XML')
        self.btn_open_xml.clicked.connect(self._open_xml)
        self.btn_open_txt.clicked.connect(self._open_txt)
        self.btn_save.clicked.connect(self._save)
        self.btn_save.setEnabled(False)
        toolbar.addWidget(self.btn_open_xml)
        toolbar.addWidget(self.btn_open_txt)
        toolbar.addWidget(self.btn_save)

        toolbar.addStretch()

        self.lbl_stats = QLabel('Загрузите XML')
        toolbar.addWidget(self.lbl_stats)

        layout.addLayout(toolbar)

        filter_bar = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('🔍 Поиск по всем полям...')
        self.search_field.textChanged.connect(self._on_search)
        filter_bar.addWidget(self.search_field, 1)

        self.section_combo = QComboBox()
        self.section_combo.addItem('Все секции', '')
        self.section_combo.currentIndexChanged.connect(self._on_section_filter)
        filter_bar.addWidget(self.section_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(['Все', 'Переведено', 'Не переведено'])
        self.status_combo.currentIndexChanged.connect(self._on_status_filter)
        filter_bar.addWidget(self.status_combo)

        layout.addLayout(filter_bar)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(24)
        layout.addWidget(self.table, 1)

    def _open_xml(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Открыть Russian.xml', os.getcwd(), 'XML files (*.xml);;All files (*)'
        )
        if not path:
            return
        try:
            self.xml_original_text = read_file(path)
            entries = parse_string_table(self.xml_original_text)
            self.model.load_entries(entries)
            self.xml_path = path

            self.section_combo.clear()
            self.section_combo.addItem('Все секции', '')
            for s in self.model.sections():
                self.section_combo.addItem(s, s)

            self._update_stats()
            self.btn_save.setEnabled(True)
            self.status_bar.showMessage(f'Загружен XML: {os.path.basename(path)} — {len(entries)} строк')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить XML:\n{e}')

    def _open_txt(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Открыть файл переводов', os.getcwd(), 'TXT files (*.txt);;All files (*)'
        )
        if not path:
            return
        try:
            translations = parse_txt(path)
            self.model.set_translations(translations)
            self.txt_path = path
            self._update_stats()
            self.status_bar.showMessage(f'Загружен TXT: {os.path.basename(path)} — {len(translations)} переводов')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить TXT:\n{e}')

    def _save(self):
        if not self.xml_path:
            QMessageBox.warning(self, 'Предупреждение', 'Сначала откройте XML.')
            return

        if self.txt_path:
            txt_out = self.txt_path
        else:
            txt_out = self.xml_path + '.txt'

        try:
            raw_translations = {}
            for entry in self.model.entries:
                trans = entry.get('_translation', '')
                if trans:
                    raw_translations[entry['_key']] = trans

            content = export_txt_strings(self.model.entries, raw_translations)
            write_txt(txt_out, content)

            xml_out = self.xml_path
            export_xml(self.xml_path, txt_out, xml_out)

            self.txt_path = txt_out
            self._update_stats()
            self.status_bar.showMessage(f'Сохранено: {os.path.basename(txt_out)} + xml')
            QMessageBox.information(self, 'Готово', f'Сохранено:\n{txt_out}\n{xml_out}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сохранении:\n{e}')

    def _on_search(self, text):
        self.proxy.set_search_text(text)

    def _on_section_filter(self, idx):
        self.proxy.set_section_filter(self.section_combo.itemData(idx))

    def _on_status_filter(self, idx):
        labels = ['', 'translated', 'untranslated']
        self.proxy.set_status_filter(labels[idx])

    def _update_stats(self):
        total = self.model.entry_count()
        translated = self.model.translated_count()
        untranslated = self.model.untranslated_count()
        self.lbl_stats.setText(f'Всего: {total}  ✅ {translated}  ❌ {untranslated}')

    def _context_menu(self, pos):
        idx = self.table.indexAt(pos)
        if not idx.isValid():
            return
        source_idx = self.proxy.mapToSource(idx)
        entry = self.model.entries[source_idx.row()]

        menu = QMenu(self)
        reflow_act = QAction('Reflow @(width)...', self)
        reflow_act.triggered.connect(lambda: self._reflow_row(source_idx.row()))
        menu.addAction(reflow_act)

        copy_key_act = QAction('Копировать ключ', self)
        copy_key_act.triggered.connect(lambda: self._copy_text(entry['key']))
        menu.addAction(copy_key_act)

        copy_eng_act = QAction('Копировать английский', self)
        copy_eng_act.triggered.connect(lambda: self._copy_text(entry['value']))
        menu.addAction(copy_eng_act)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _reflow_row(self, row):
        entry = self.model.entries[row]
        current = entry.get('_translation', '')
        width, ok = QInputDialog.getInt(self, 'Reflow', 'Ширина строки:', 60, 10, 200)
        if not ok:
            return
        from .reflow_utils import make_reflow_directive, apply_reflow
        directive = make_reflow_directive(current.replace('&#10;', '\n'), width)
        idx = self.model.index(row, 3)
        self.model.setData(idx, directive)

    def _copy_text(self, text):
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.clipboard().setText(text)
