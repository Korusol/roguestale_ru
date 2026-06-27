import os
import re

from .checksum_utils import update_dialogue_checksum
from .dialogue_tr_store import load_translations


def get_skip_patterns():
    return [
        lambda v: v.startswith('STR_BUY['),
        lambda v: re.match(r'^STR_[A-Z_0-9]+$', v),
        lambda v: re.match(r'^[a-z_][a-z_0-9]*$', v),
        lambda v: re.match(r'^[A-Z_0-9]+$', v),
        lambda v: re.match(r'^[\W\d_]+$', v),
        lambda v: not v.strip(),
    ]


def should_translate(val):
    for check in get_skip_patterns():
        if check(val):
            return False
    return True


def apply_translations_to_xml(xml_text, translations, filename):
    translations = translations or {}
    attr_pattern = re.compile(r'(title|response)="([^"]*?)"')

    result_parts = []
    last_end = 0

    for cm in re.finditer(
        r'<choices\s+id="([^"]*)"(?:\s+title="([^"]*)")?[^>]*>.*?</choices>',
        xml_text, re.DOTALL
    ):
        result_parts.append(xml_text[last_end:cm.start()])
        block = cm.group(0)
        choices_id = cm.group(1)
        tmp = {'choices_id': choices_id}

        def make_replacer(cid):
            def replacer(m):
                attr_name = m.group(1)
                val = m.group(2)
                if not should_translate(val):
                    return m.group(0)
                full_key = f'{filename}::{cid}::{attr_name}'
                ru = translations.get(full_key, '')
                if ru and ru != val:
                    return f'{attr_name}="{ru}"'
                return m.group(0)
            return replacer

        block = attr_pattern.sub(make_replacer(choices_id), block)
        result_parts.append(block)
        last_end = cm.end()

    result_parts.append(xml_text[last_end:])
    return ''.join(result_parts)


def export_dialogues(input_folder, output_folder, translations=None):
    if translations is None:
        translations = load_translations()

    os.makedirs(output_folder, exist_ok=True)

    for fname in sorted(os.listdir(input_folder)):
        if not fname.endswith('.xml'):
            continue
        src = os.path.join(input_folder, fname)
        with open(src, 'r', encoding='utf-8') as f:
            xml_text = f.read()

        translated = apply_translations_to_xml(xml_text, translations, fname)
        translated = update_dialogue_checksum(translated)

        dst = os.path.join(output_folder, fname)
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(translated)
