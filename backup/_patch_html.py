import re
from pathlib import Path

files = [
    ('index.html', None),
    ('tomatis.html', 'page-tomatis'),
    ('languages.html', 'page-languages'),
]

for name, body_class in files:
    path = Path(name)
    text = path.read_text(encoding='utf-8')
    new_text, count = re.subn(r'<style>.*?</style>', '<link rel="stylesheet" href="styles.css" />', text, flags=re.S, count=1)
    if count != 1:
        raise SystemExit(f'Expected one <style> block in {name}, found {count}')
    text = new_text
    if body_class:
        new_text, count = re.subn(r'<body\s*>', f'<body class="{body_class}">', text, count=1)
        if count != 1:
            raise SystemExit(f'Expected one <body> tag in {name}, found {count}')
        text = new_text
    path.write_text(text, encoding='utf-8')
    print(f'Patched {name}')
