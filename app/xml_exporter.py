import re

from .checksum_utils import update_strings_checksum
from .reflow_utils import apply_reflow


def matchRU(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')):
    return not alphabet.isdisjoint(text.lower())


def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def parse_txt_translations(filename):
    translations = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'^\s*#', line):
                continue
            match = re.match(r'(\w+)\.(".*?"[^ ]*) (.*)', line.strip())
            if match:
                tag, key, value = match.groups()
                value = apply_reflow(value)
                translations[f'{tag}:{key}'] = value
    return translations


def encode_xml_local(text):
    step = repr(text.encode('ascii', 'xmlcharrefreplace'))[2:-1].replace('"', '')
    return step


def strip_local(extra):
    return re.sub(r'\s*local="[^"]*"', '', extra)


def build_output_xml(xml_text, translations):
    mainkey = None

    def replace_tag(tag):
        def repl(match):
            nonlocal mainkey
            id_, value, extra = match.groups()
            paragraph = re.match(r'^paragraph (\d+)', id_)
            if paragraph:
                key = f'{mainkey}.{paragraph.group(1)}'
            else:
                key = f'{tag}:"{id_}"'
                mainkey = key
            russian = translations.get(key)
            if russian is None:
                russian = ''
            else:
                extra = strip_local(extra)
                escape = value.replace('\n', '&#10;')
                if russian == escape:
                    russian = ''
                else:
                    if matchRU(russian):
                        russian = encode_xml_local(russian)
                    russian = russian.replace('#pp#', ' ')
                    russian = f' local="{russian}"'
            return f'<str id="{id_}" value="{value}"{russian}{extra}>'
        return repl

    def sec_replace(match):
        tag, content, endtag = match.groups()
        content = re.sub(r'<str id="([^"]+)" value="([^"]+)"(.*?)>', replace_tag(tag), content)
        return f'<{tag}>{content}</{endtag}>'

    merged = re.sub(r'<([A-Z][a-zA-Z]*)>(.*?)</([A-Z][a-zA-Z]*)>', sec_replace, xml_text, flags=re.DOTALL)
    return merged


def export_xml(source_xml_path, txt_path, output_path):
    xml_text = read_file(source_xml_path)
    translations = parse_txt_translations(txt_path)
    merged = build_output_xml(xml_text, translations)
    final = update_strings_checksum(merged)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final)
    return output_path
