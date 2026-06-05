import re
import textwrap
from pathlib import Path

base_path = Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/index.html')
tomatis_path = Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/tomatis.html')
languages_path = Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/languages.html')
output_path = Path('d:/BITS/Modules/COMMMUNITY-PROJECT/website-design-test/redesign/styles.css')

style_pattern = re.compile(r'<style>(.*?)</style>', re.S | re.I)

def extract_style(path):
    text = path.read_text(encoding='utf-8')
    match = style_pattern.search(text)
    if not match:
        return ''
    return textwrap.dedent(match.group(1)).strip()


def prefix_css(css, prefix):
    css = css.strip()
    output = []
    i = 0
    while i < len(css):
        if css[i].isspace():
            output.append(css[i])
            i += 1
            continue
        if css[i] == '@':
            header_end = css.find('{', i)
            if header_end == -1:
                output.append(css[i:])
                break
            depth = 1
            j = header_end + 1
            while j < len(css) and depth:
                if css[j] == '{':
                    depth += 1
                elif css[j] == '}':
                    depth -= 1
                j += 1
            inner = css[header_end + 1:j - 1]
            output.append(css[i:header_end + 1])
            output.append(prefix_css(inner, prefix))
            output.append('}')
            i = j
            continue

        sel_end = css.find('{', i)
        if sel_end == -1:
            output.append(css[i:])
            break
        selectors = css[i:sel_end].strip()
        body_start = sel_end + 1
        depth = 1
        j = body_start
        while j < len(css) and depth:
            if css[j] == '{':
                depth += 1
            elif css[j] == '}':
                depth -= 1
            j += 1
        body = css[body_start:j - 1]
        prefixed = ', '.join(f'{prefix} {s.strip()}' for s in selectors.split(','))
        output.append(prefixed)
        output.append(' {')
        output.append(body)
        output.append('}')
        i = j
    return ''.join(output)


def remove_root_blocks(css):
    css = re.sub(r'(?s):root\s*\{.*?\}', '', css)
    css = re.sub(r'(?s)html\s*\{.*?\}', '', css)
    css = re.sub(r'(?s)body\s*\{.*?\}', '', css)
    return css


def make_page_specific(css, prefix, section_padding=None):
    css = remove_root_blocks(css)
    if section_padding:
        css = f'body.{prefix} {{ --section-padding: {section_padding}; }}\n\n' + css.strip()
    return prefix_css(css, f'body.{prefix}')


def add_hero_zoom(css):
    def replacer(match):
        block = match.group(0)
        if '--hero-zoom' not in block:
            block = block.replace('.hero {', '.hero {\n        --hero-zoom: 0%;', 1)
        if 'background-size:' not in block:
            block = re.sub(
                r'background:[^;]+;',
                'background-image: linear-gradient(180deg, rgba(20, 35, 67, 0.38), rgba(20, 35, 67, 0.18)), url("files/auroville-language-lab-slider-1.webp");\n        background-position: center center;\n        background-repeat: no-repeat;\n        background-size: calc(100% + var(--hero-zoom, 0%));',
                block,
                flags=re.S,
            )
        return block

    return re.sub(r'\.hero\s*\{.*?\}', replacer, css, flags=re.S)


def fix_page_hero_size(css):
    def repl(match):
        block = match.group(0)
        if 'background-size:' not in block:
            block = block.rstrip('}') + '\n        background-size: calc(100% + var(--hero-zoom, 0%));\n    }'
        return block
    return re.sub(r'body\.[^\s]+ \.hero\s*\{.*?\}', repl, css, flags=re.S)

base_css = extract_style(base_path)
base_css = add_hero_zoom(base_css)

page_tomatis = make_page_specific(extract_style(tomatis_path), 'page-tomatis')
page_lng = make_page_specific(extract_style(languages_path), 'page-languages', section_padding='80px 0')
page_tomatis = fix_page_hero_size(page_tomatis)
page_lng = fix_page_hero_size(page_lng)

output = '\n'.join([
    base_css,
    '/* Page-specific styles for page-tomatis */',
    page_tomatis,
    '/* Page-specific styles for page-languages */',
    page_lng,
])
output_path.write_text(output, encoding='utf-8')
print('Generated', output_path)
