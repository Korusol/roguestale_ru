# Roguetale Russian Localization

## Structure

- `Russian_orig.xml` — source English strings (game author's original)
- `Russian.xml` — English strings with some `local` attributes (update target)
- `Russian1.xml` — merged output with Russian translations
- `*.txt` — translation files: `TagName."key"` or `TagName."key".N` followed by translation
- `export.py` — extracts strings from `Russian_orig.xml` into `Russian_orig.xml.txt`
- `import.py` — reads `Russian.xml`, applies translations from `Russian.xml.txt`, writes `Russian1.xml`

## Workflow

1. **Export**: run `export.py` (reads `Russian_orig.xml`, writes `Russian_orig.xml.txt`)
2. **Translate**: edit the `.txt` file — each line is `TagName."key" translation`
3. **Import**: run `import.py` (reads `Russian.xml` + `Russian.xml.txt`, writes `Russian1.xml`)

Both scripts hardcode their filenames at the bottom — no CLI arguments.

## Import details

- Lines starting with `#` are skipped (comments)
- `@(width)` directive at line start reflows text to given character width (CJK-aware: wide chars count 2)
- `#pp#` in translated text is replaced with a space (hack: prevents the game from auto-generating indefinite articles on empty values)
- `&#10;` in source XML represents newlines; same encoding is used in output
- Source XML `<str>` values may contain **literal newlines** (multi-line attribute). `export.py` normalizes them to `&#10;` on extraction; `import.py` handles both forms
- `export.py` normalizes `value` newlines to `&#10;` but leaves `id` (the key) unchanged. Strings with newlines in the `id` create multi-line txt entries that `import.py`'s line-by-line `map_translations` cannot parse — these need `id` newlines also normalized to `&#10;`
- SHA1 checksum is computed on the XML (after stripping existing checksum, encoding non-ASCII as `&#N;`) and injected into the `<strings>` root tag
- Only strings containing Cyrillic characters get a `local` attribute; untranslated strings are left without it
- Paragraph strings (id matching `paragraph N`) use the parent key: `TagName."parent_key".N`
- Non-paragraph strings use the key pattern: `TagName:"key"` — this is used to look up translations

## Quirks

- `import.py` runs as a script at module level (`main("Russian.xml")` at line 128), not guarded by `if __name__ == "__main__"`
- The repo has no tests, no package manager, no CI — it's a standalone translation toolset
- Python 3.10, no third-party dependencies (stdlib only)
- No `.gitignore` at root (only `.idea/.gitignore`)

---

# Dialogue Translation (`dialogues/` → `dialogues_Rus/`)

## Overview

Dialogue XMLs under `dialogues/` are translated separately from the main string table — **no export/import pipeline**.

## Scripts

- `_extract_dialogues.py` — scans all XMLs, prints unique translatable strings (for review)
- `_translate_dialogues.py` — reads `dialogues/`, translates `title`/`response` attrs, writes `dialogues_Rus/`

## Rules

1. **Only `title` and `response` attributes** are translated. Everything else (`id`, `result`, `next`, etc.) is left as-is.
2. **Variable detection** — skip if the value is:
   - All uppercase `A-Z`, digits, underscores (`STR_INTRO_2`, `SET_ENEMY`, `LEAVE_DUNGEON`)
   - All lowercase `a-z` with underscores (`finish_quest`)
   - All non-letter characters (`----------`, `...`, `  (?)`)
   - Starts with `STR_BUY[` (shop command)
   - Empty
3. **No `#pp#`** — not relevant for dialogue files.
4. **Checksum** — each `<dialogue>` tag has a `checksum` attribute. After translation:
   - Strip existing checksum
   - Encode non-ASCII chars as `&#N;` (like `import.py`)
   - Compute SHA1 and inject it back

## Workflow

```
python _translate_dialogues.py
```

Reads all `.xml` from `dialogues/`, translates, writes to `dialogues_Rus/`.

To preview untranslated strings: `python _extract_dialogues.py`

## `_translate_dialogues.py` details

- `TR` dict at top: English → Russian mapping (~1000 entries)
- Skip patterns checked in order:
  1. `val.startswith('STR_BUY[')` — shop command
  2. `re.match(r'^STR_[A-Z_0-9]+$', val)` — pure STR_ variable
  3. `re.match(r'^[a-z_][a-z_0-9]*$', val)` — lowercase code ref
  4. `re.match(r'^[A-Z_0-9]+$', val)` — uppercase code ref
  5. `re.match(r'^[\W\d_]+$', val)` — non-letter separators
- `update_checksum(xml)` — mirrors `import.py`'s checksum logic
- Output: `dialogues_Rus/` (45 files, one per NPC/quest)
