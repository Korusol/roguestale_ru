import re


def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def decode_local(val):
    if not val:
        return ''
    val = val.strip('"')
    result = []
    i = 0
    while i < len(val):
        if val[i:i+2] == '&#':
            end = val.find(';', i)
            if end > i:
                cp = int(val[i+2:end])
                result.append(chr(cp))
                i = end + 1
                continue
        result.append(val[i])
        i += 1
    return ''.join(result)


def parse_string_table(xml_text):
    entries = []
    pattern = re.compile(r'<(\w+?)>(.*?)</\1>', re.DOTALL)
    str_pattern = re.compile(r'<str id="([^"]+)" value="([^"]*)"(.*?)>')
    local_pattern = re.compile(r'local="([^"]*)"')

    for tag_match in pattern.finditer(xml_text):
        section = tag_match.group(1)
        content = tag_match.group(2)
        for str_match in str_pattern.finditer(content):
            id_ = str_match.group(1)
            value = str_match.group(2)
            extra = str_match.group(3)
            local_match = local_pattern.search(extra)
            has_local = local_match is not None
            local_raw = local_match.group(1) if local_match else ''
            local_decoded = decode_local(local_raw)
            entries.append({
                'section': section,
                'key': id_,
                'value': value,
                'has_local': has_local,
                'local': local_decoded,
            })
    return entries
