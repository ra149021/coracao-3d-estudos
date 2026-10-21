"""Generate the static chapter search index (Python standard library only)."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

SOURCES = ('assets/circulatory-theory.json', 'assets/respiratory/theory.json')
ROOT = Path(__file__).resolve().parents[1]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1
        elif tag in ('p', 'br', 'li', 'div'):
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain(value):
    parser = PlainText()
    parser.feed(str(value))
    return ' '.join(''.join(parser.parts).split())


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def chapter_text(chapter):
    values = [chapter['title'], chapter['summary'], *chapter.get('objectives', [])]
    for section in chapter.get('sections', []):
        values.append(section.get('heading', ''))
        values.extend(section.get('paragraphs', []))
        values.extend(section.get('bullets', []))
        table = section.get('table', {})
        values.extend(table.get('headers', []))
        for row in table.get('rows', []):
            values.extend(row)
    for question in chapter.get('recall', []):
        values.extend(question.get(key, '') for key in ('question', 'answer', 'explanation'))
    return plain(' '.join(str(value) for value in values))


def build_index(root):
    site = (Path(root) / 'site').resolve()
    items, hashes, seen = [], {}, set()
    for name, expected_system in zip(SOURCES, ('circulatory', 'respiratory')):
        path = (site / name).resolve()
        if not path.is_relative_to(site):
            raise ValueError(f'source path outside public site: {name}')
        raw = path.read_bytes()
        hashes[name] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw)
        if data['system'] != expected_system:
            raise ValueError(f'{name}: expected system {expected_system}')
        if not isinstance(data['chapters'], list) or not data['chapters']:
            raise ValueError(f'{name}: chapters must be a nonempty list')
        for chapter in data['chapters']:
            system, ident = data['system'], chapter['id']
            if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', ident):
                raise ValueError(f'{name}: invalid chapter id {ident!r}')
            if ident in seen:
                raise ValueError(f'{name}: duplicate chapter id {ident}')
            seen.add(ident)
            items.append({'id': f'{system}:{ident}', 'system': system, 'chapterId': ident,
                          'title': plain(chapter['title']), 'summary': plain(chapter['summary']),
                          'text': chapter_text(chapter),
                          'url': 'theory.html?' + urlencode({'system': system, 'chapter': ident})})
    return {'version': 1, 'sourceHashes': hashes, 'items': items}


def serialized(index):
    return json.dumps(index, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root (default: script location)')
    parser.add_argument('--check', action='store_true', help='Fail on missing/stale index; never write')
    args = parser.parse_args()
    try:
        index = build_index(args.root)
        output = args.root / 'site/assets/search-index.json'
        if args.check:
            if not output.is_file() or read_json(output) != index:
                raise ValueError('search-index.json is missing/stale; run python scripts/build_study_search.py')
        else:
            output.write_text(serialized(index), encoding='utf-8')
        print(f'OK: {len(index["items"])} chapters; {len(index["sourceHashes"])} SHA-256 sources; {output}')
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'ERROR: search index: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
