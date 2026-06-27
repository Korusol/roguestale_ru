from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class StringTableModel(QAbstractTableModel):
    COLUMNS = ['Section', 'Key', 'English', 'Translation', 'Status']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = []
        self.translations = {}

    def load_entries(self, entries):
        self.beginResetModel()
        self.entries = entries
        self._apply_translations()
        self.endResetModel()

    def set_translations(self, translations):
        self.beginResetModel()
        self.translations = translations
        self._apply_translations()
        self.endResetModel()

    def _apply_translations(self):
        mainkey = None
        for entry in self.entries:
            tag = entry['section']
            id_ = entry['key']
            paragraph = id_.startswith('paragraph ')
            if paragraph:
                parts = id_.split(' ', 1)
                key = f'{mainkey}.{parts[1]}'
            else:
                key = f'{tag}:"{id_}"'
                mainkey = key
            translation = self.translations.get(key, entry.get('local', ''))
            if not translation:
                translation = ''
            entry['_translation'] = translation
            entry['_key'] = key

    def get_translation_key(self, row):
        return self.entries[row]['_key']

    def entry_count(self):
        return len(self.entries)

    def translated_count(self):
        return sum(1 for e in self.entries if e.get('_translation', '') and match_cyrillic(e['_translation']))

    def untranslated_count(self):
        return self.entry_count() - self.translated_count()

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
                return entry['section']
            elif col == 1:
                return entry['key']
            elif col == 2:
                return entry['value']
            elif col == 3:
                return entry.get('_translation', '')
            elif col == 4:
                trans = entry.get('_translation', '')
                if trans and match_cyrillic(trans):
                    return '✓'
                return '✗'
        if role == Qt.ItemDataRole.BackgroundRole and col == 4:
            trans = entry.get('_translation', '')
            if trans and match_cyrillic(trans):
                return Qt.GlobalColor.green
            return Qt.GlobalColor.red
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or index.column() != 3:
            return False
        self.entries[index.row()]['_translation'] = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.BackgroundRole])
        return True

    def flags(self, index):
        if index.column() == 3:
            return super().flags(index) | Qt.ItemFlag.ItemIsEditable
        return super().flags(index)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return None

    def sections(self):
        seen = set()
        result = []
        for e in self.entries:
            s = e['section']
            if s not in seen:
                seen.add(s)
                result.append(s)
        return result


def match_cyrillic(text):
    alphabet = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    return not alphabet.isdisjoint(text.lower())
