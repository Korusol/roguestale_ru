import re


def apply_reflow(line, width=None):
    match = re.match(r'^@\((\d+)\)(.*)', line)
    if not match:
        return line
    if width is None:
        width = int(match.group(1))
    content = match.group(2).replace('&#10;', '\n')

    result = []
    n = 0
    for c in content:
        cp = ord(c)
        if n >= width:
            result.append('\n')
            n = 0
        if cp < 0x3000:
            if cp == 10:
                n = 0
            else:
                n += 1
        else:
            n += 2
        result.append(c)
    return ''.join(result).replace('\n', '&#10;')


def make_reflow_directive(text, width):
    if not text:
        return text
    escaped = text.replace('\n', '&#10;')
    return f'@({width}){escaped}'
