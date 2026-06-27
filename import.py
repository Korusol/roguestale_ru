import hashlib
import re
import os


def sha1(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


def readfile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def composing(line):
    match = re.match(r'^@\((\d+)\)(.*)', line)
    if not match:
        return line
    width = int(match.group(1))
    content = match.group(2).replace('&#10;', '\n')

    encode = []
    n = 0
    for c in content:
        cp = ord(c)
        if n >= width:
            encode.append('\n')
            n = 0
        if cp < 0x3000:
            if cp == 10:
                n = 0
            else:
                n += 1
        else:
            n += 2
        encode.append(c)
    return ''.join(encode).replace('\n', '&#10;')


def map_translations(filename):
    translations = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not re.match(r'^\s*#', line):
                match = re.match(r'(\w+)\.(".*?"[^ ]*) (.*)', line.strip())
                if match:
                    tag, key, value = match.groups()
                    value = composing(value)
                    translations[f"{tag}:{key}"] = value
    return translations


def merge(xml, translations):
    mainkey = None
    total = 0
    success = 0

    def replace_tag(tag):
        def repl(match):
            nonlocal mainkey, total, success
            total += 1
            id_, value, extra = match.groups()
            paragraph = re.match(r'^paragraph (\d+)', id_)
            if paragraph:
                key = f"{mainkey}.{paragraph.group(1)}"
            else:
                key = f'{tag}:"{id_}"'
                mainkey = key
            russian = translations.get(key)
            if russian is None:
                print("Missing:", key)
                russian = ""
            else:
                escape = value.replace('\n', '&#10;')
                if russian == escape:
                    russian = ''
                else:
                    if matchRU(russian):
                        russian = repr(russian.encode('ascii', 'xmlcharrefreplace'))[2:-1]
                        russian = russian.replace('"', "")
                    success += 1
                    russian = russian.replace('#pp#', " ")
                    russian = f' local="{russian}"'
            return f'<str id="{id_}" value="{value}"{russian}{extra}>'
        return repl

    def sec_replace(match):
        tag, content, endtag = match.groups()
        assert tag == endtag
        content = re.sub(r'<str id="([^"]+)" value="([^"]+)"(.*?)>', replace_tag(tag), content)
        return f"<{tag}>{content}</{endtag}>"

    merged = re.sub(r'<([A-Z][a-zA-Z]*)>(.*?)</([A-Z][a-zA-Z]*)>', sec_replace, xml, flags=re.DOTALL)
    print(f"Finish {success}/{total}")
    return merged

def matchRU(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')):
    return not alphabet.isdisjoint(text.lower())

def checksum(xml):
    # Remove existing checksum
    remove_checksum = re.sub(r'^(.*?) checksum="[0-9a-f]+"(>.*)', r'\1\2', xml, flags=re.DOTALL)
    escape = remove_checksum.replace("&#10;", "\n")

    encode = []
    for c in escape:
        char_code = ord(c)
        if char_code < 127:
            encode.append(chr(char_code))
        else:
            encode.append(f"&#{char_code};")

    hash = sha1(''.join(encode))
    # Add new checksum
    sign_checksum = re.sub(r'^(.* checksum=")[0-9a-f]+', rf'\g<1>{hash}', xml, flags=re.DOTALL)
    return sign_checksum


def main(filename):
    xml = readfile(filename)
    translations = map_translations(filename + '.txt')
    merged = merge(xml, translations)
    final = checksum(merged)
    with open("Russian1.xml", "w", encoding='utf-8') as f:
        f.write(final)


main("Russian.xml")
