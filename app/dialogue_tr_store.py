import json


DIALOGUES_TR_FILE = 'dialogues_translations.json'


def load_translations():
    try:
        with open(DIALOGUES_TR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_translations(translations):
    with open(DIALOGUES_TR_FILE, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)


def get_entry_key(entry, filename):
    cid = entry['choices_id']
    attr = entry['attr']
    return f'{filename}::{cid}::{attr}'


def get_translation(translations, entry, filename):
    key = get_entry_key(entry, filename)
    return translations.get(key, '')


def set_translation(translations, entry, filename, value):
    key = get_entry_key(entry, filename)
    translations[key] = value
