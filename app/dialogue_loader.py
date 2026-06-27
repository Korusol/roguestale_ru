import os
import re


def extract_dialogue_strings(xml_text):
    entries = []
    choices_pattern = re.compile(
        r'<choices\s+id="([^"]*)"\s+title="([^"]*)"[^>]*>'
        r'(.*?)'
        r'</choices>',
        re.DOTALL
    )
    choice_pattern = re.compile(
        r'<choice\s+title="([^"]*)"\s+response="([^"]*)"([^>]*?)/?>'
    )

    for cm in choices_pattern.finditer(xml_text):
        choices_id = cm.group(1)
        title = cm.group(2)
        body = cm.group(3)

        if title:
            entries.append({
                'choices_id': choices_id,
                'attr': 'title',
                'choice_index': -1,
                'english': title,
            })

        for i, ch in enumerate(choice_pattern.finditer(body)):
            ch_title = ch.group(1)
            ch_response = ch.group(2)
            if ch_title:
                entries.append({
                    'choices_id': choices_id,
                    'attr': f'choice[{i}].title',
                    'choice_index': i,
                    'english': ch_title,
                })
            if ch_response:
                entries.append({
                    'choices_id': choices_id,
                    'attr': f'choice[{i}].response',
                    'choice_index': i,
                    'english': ch_response,
                })

    return entries


def load_dialogues(folder_path):
    files = []
    for fname in sorted(os.listdir(folder_path)):
        if not fname.endswith('.xml'):
            continue
        path = os.path.join(folder_path, fname)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        entries = extract_dialogue_strings(text)
        files.append({
            'filename': fname,
            'path': path,
            'text': text,
            'entries': entries,
        })
    return files
