import re
import io


def readfile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def export(text):
    list_ = []
    pattern = re.compile(r'<(\w+?)>(.*?)</\1>', re.DOTALL)
    str_pattern = re.compile(r'<str id="([^"]+)" value="([^"]+)".*?>')

    for tag_match in pattern.finditer(text):
        tag = tag_match.group(1)
        content = tag_match.group(2)

        for str_match in str_pattern.finditer(content):
            id_ = str_match.group(1).replace('\n', '&#10;')
            value = str_match.group(2)
            list_.append((tag, id_, value))

    return list_


def main(filename):
    t = readfile(filename)
    list_ = export(t)
    e = []
    mainkey = None

    for item in list_:
        tag, id_, value = item
        paragraph = re.match(r'^paragraph (\d+)', id_)

        if paragraph:
            id_ = f"{mainkey}.{paragraph.group(1)}"
        else:
            id_ = f'"{id_}"'
            mainkey = id_

        value = value.replace("\n", "&#10;")
        e.append(f"{tag}.{id_} {value}")

    with open(filename + ".txt", 'w', encoding='utf-8') as f:
        f.write("\n".join(e))


if __name__ == "__main__":
    main("Russian_orig.xml")