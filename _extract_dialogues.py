import os, re, json

attr_pattern = re.compile(r'(title|response)="([^"]*?)"')

all_texts = set()
file_texts = {}

for fname in sorted(os.listdir('dialogues')):
    if not fname.endswith('.xml'):
        continue
    path = os.path.join('dialogues', fname)
    text = open(path, 'r', encoding='utf-8').read()
    texts = set()
    for attr, val in attr_pattern.findall(text):
        if val and not val.startswith('STR_') and not re.match(r'^[\W\d_]+$', val):
            texts.add(val)
            all_texts.add(val)
    file_texts[fname] = texts

print(f'Files: {len(file_texts)}')
print(f'Unique translatable strings: {len(all_texts)}')
print()
for v in sorted(all_texts):
    print(v)
