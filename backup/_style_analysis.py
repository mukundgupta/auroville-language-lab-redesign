import re
from pathlib import Path

files = {
    'index': Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/index.html'),
    'tomatis': Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/tomatis.html'),
    'languages': Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/languages.html'),
}
pattern = re.compile(r'<style>(.*?)</style>', re.S | re.I)

def parse(css):
    blocks = []
    pos = 0
    while pos < len(css):
        m = re.search(r'@keyframes\s+[^{]+\{', css[pos:])
        if m:
            start = pos + m.start()
            blocks.extend(parse_blocks(css[pos:start]))
            j = start
            depth = 0
            while j < len(css):
                if css[j] == '{':
                    depth += 1
                elif css[j] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            blocks.append((css[start:j+1].strip(), None))
            pos = j + 1
        else:
            blocks.extend(parse_blocks(css[pos:]))
            break
    return blocks


def parse_blocks(text):
    blocks = []
    pos = 0
    while True:
        m = re.search(r'([^{}]+)\{', text[pos:])
        if not m:
            break
        sel = m.group(1).strip()
        start = pos + m.end()
        depth = 1
        j = start
        while j < len(text) and depth > 0:
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1
        blocks.append((sel, text[start:j-1].strip()))
        pos = j
    return blocks

styles = {}
for name, path in files.items():
    text = path.read_text(encoding='utf-8')
    m = pattern.search(text)
    styles[name] = m.group(1) if m else ''

base = parse(styles['index'])
for name in ['tomatis', 'languages']:
    other = parse(styles[name])
    base_dict = {sel: content for sel, content in base if content is not None}
    shared = []
    changed = []
    unique = []
    for sel, content in other:
        if content is None:
            continue
        if sel in base_dict:
            if base_dict[sel] == content:
                shared.append(sel)
            else:
                changed.append(sel)
        else:
            unique.append(sel)
    print('===', name, '===')
    print('shared', len(shared))
    print('changed', len(changed))
    print('unique', len(unique))
    print('changed selectors sample', changed[:20])
    print('unique selectors sample', unique[:20])
