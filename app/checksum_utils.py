import hashlib
import re


def sha1(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


def encode_non_ascii(text):
    result = []
    for c in text:
        cp = ord(c)
        if cp < 127:
            result.append(c)
        else:
            result.append(f'&#{cp};')
    return ''.join(result)


def normalize_attr_newlines(xml):
    def fix_tag(m):
        return m.group(0).replace('\n', '&#10;')
    return re.sub(r'<[^>]*>', fix_tag, xml)


def update_strings_checksum(xml):
    remove = re.sub(r'^(.*?) checksum="[0-9a-f]+"(>.*)', r'\1\2', xml, flags=re.DOTALL)
    normalized = normalize_attr_newlines(remove)
    decoded = normalized.replace('&#10;', '\n')
    encoded = encode_non_ascii(decoded)
    cs = sha1(encoded)
    result = re.sub(r'^(.* checksum=")[0-9a-f]+', rf'\g<1>{cs}', xml, flags=re.DOTALL)
    return result


def update_dialogue_checksum(xml):
    remove = re.sub(r'(<dialogue\s[^>]*) checksum="[0-9a-f]+"', r'\1', xml, count=1)
    encoded = encode_non_ascii(remove)
    cs = sha1(encoded)
    result = re.sub(r'(<dialogue\s)', rf'\1checksum="{cs}" ', remove, count=1)
    return result
