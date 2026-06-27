import re


def parse_txt(filename):
    translations = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or re.match(r'^\s*#', line):
                continue
            match = re.match(r'(\w+)\.(".*?"[^ ]*) (.*)', line)
            if match:
                tag, key, value = match.groups()
                translations[f'{tag}:{key}'] = value
    return translations


def export_txt_strings(entries, translations):
    lines = []
    mainkey = None
    for entry in entries:
        tag = entry['section']
        id_ = entry['key']
        value = entry['value']

        paragraph = re.match(r'^paragraph (\d+)', id_)
        if paragraph:
            id_ = f"{mainkey}.{paragraph.group(1)}"
        else:
            id_ = f'"{id_}"'
            mainkey = id_

        value = value.replace('\n', '&#10;')
        translation = translations.get(f'{tag}:{id_}', value)
        lines.append(f'{tag}.{id_} {translation}')
    return '\n'.join(lines)


def write_txt(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
