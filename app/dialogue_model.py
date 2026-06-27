from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

from .dialogue_tr_store import get_translation, set_translation
from .dialogue_exporter import should_translate


class DialogueTableModel(QAbstractTableModel):
    COLUMNS = ['Type', 'English', 'Translation', 'Status']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = []
        self.filename = ''
        self.translations = {}

    def load(self, entries, filename, translations):
        self.beginResetModel()
        self.entries = entries
        self.filename = filename
        self.translations = translations
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        entry = self.entries[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if col == 0:
                return entry['attr']
            elif col == 1:
                return entry['english']
            elif col == 2:
                trans = get_translation(self.translations, entry, self.filename)
                return trans
            elif col == 3:
                trans = get_translation(self.translations, entry, self.filename)
                return '✓' if trans else '✗'
        if role == Qt.ItemDataRole.BackgroundRole and col == 3:
            trans = get_translation(self.translations, entry, self.filename)
            return Qt.GlobalColor.green if trans else Qt.GlobalColor.red
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or index.column() != 2:
            return False
        entry = self.entries[index.row()]
        set_translation(self.translations, entry, self.filename, value)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.BackgroundRole])
        return True

    def flags(self, index):
        if index.column() == 2:
            return super().flags(index) | Qt.ItemFlag.ItemIsEditable
        return super().flags(index)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return None

    def translated_count(self):
        count = 0
        for e in self.entries:
            if get_translation(self.translations, e, self.filename):
                count += 1
        return count
