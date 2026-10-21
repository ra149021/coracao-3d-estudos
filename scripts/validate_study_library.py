"""Audit public study data without network access or private library reads."""
import argparse
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urlsplit

from build_study_search import ROOT, SOURCES, build_index, read_json

EXPECTED_LECTURES = {'C1', 'C2', 'C3', 'R1', 'R2', 'R3', 'R4'}
IDENTIFIER = re.compile(r'[A-Za-z0-9_-]+')


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key in ('href', 'src', 'poster'):
                self.links.append(value)
            if value and key in ('id', 'name'):
                self.ids.add(value)


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(root):
    site = (Path(root) / 'site').resolve()
    errors, warnings, external = [], set(), set()
    counts = {'chapters': 0, 'questions': 0, 'references': 0, 'jpgPages': 0,
              'transcripts': 0, 'segments': 0, 'localLinks': 0}
    documents = read_json(site / 'assets/public-documents.json')['documents']
    videos = read_json(site / 'assets/public-lectures.json')['videos']

    def unique(entries, context):
        seen = set()
        for entry in entries:
            ident = entry.get('id')
            if not isinstance(ident, str) or not IDENTIFIER.fullmatch(ident):
                errors.append(f'{context}: invalid id {ident!r}')
                continue
            if ident in seen:
                errors.append(f'{context}: duplicate id {ident}')
            seen.add(ident)
        return seen

    doc_ids = unique(documents, 'documents')
    video_ids = unique(videos, 'lectures')
    docs = {d['id']: d for d in documents}
    lectures = {v['id']: v for v in videos}
    if video_ids != EXPECTED_LECTURES:
        errors.append('lectures: expected exactly seven IDs C1,C2,C3,R1,R2,R3,R4')
    libraries = [read_json(site / name) for name in SOURCES]
    chapters_by_system = {d['system']: {c['id'] for c in d['chapters']} for d in libraries}

    def local_path(value, origin):
        decoded = unquote(value)
        # Public assets must never escape site, including via symlinks.
        path = (site / decoded.lstrip('/') if decoded.startswith('/') else origin.parent / decoded).resolve()
        if not path.is_relative_to(site):
            errors.append(f'{origin.relative_to(site)}: path outside public site: {value}')
            return None
        return path

    pages_cache = {}

    def page_info(path):
        if path not in pages_cache:
            page = PageLinks()
            page.feed(path.read_text(encoding='utf-8'))
            pages_cache[path] = page
        return pages_cache[path]

    def link(value, origin):
        if not isinstance(value, str) or not value or '${' in value:
            return
        url = urlsplit(value)
        if url.scheme in ('http', 'https') or url.netloc:
            external.add(value)
            return
        if url.scheme in ('data', 'blob', 'mailto', 'tel'):
            return
        if url.scheme:
            errors.append(f'{origin.relative_to(site)}: unsupported link scheme {value}')
            return
        if url.path.startswith('/local/'):
            warnings.add('Local /local/ endpoints not tested; no private manifest is read.')
            return
        path = local_path(url.path, origin) if url.path else origin
        if path is None:
            return
        if path.is_dir():
            path = path / 'index.html'
        if not path.is_file():
            errors.append(f'{origin.relative_to(site)}: missing local link/asset {value}')
            return
        counts['localLinks'] += 1
        if url.fragment and path.suffix == '.html' and unquote(url.fragment) not in page_info(path).ids:
            errors.append(f'{origin.relative_to(site)}: missing fragment {value}')
        query = parse_qs(url.query)
        if path.name == 'theory.html':
            system = query.get('system', ['circulatory'])[0]
            chapter = query.get('chapter', [None])[0]
            if system not in chapters_by_system or (chapter and chapter not in chapters_by_system[system]):
                errors.append(f'{origin.relative_to(site)}: invalid theory target {value}')
        if path.name == 'classroom.html':
            if 'doc' in query:
                ident = query['doc'][0]
                page = query.get('page', ['1'])[0]
                if ident not in doc_ids or not page.isdigit() or not 1 <= int(page) <= docs[ident]['pages']:
                    errors.append(f'{origin.relative_to(site)}: invalid document/page target {value}')
            if 'video' in query and query['video'][0] not in video_ids:
                errors.append(f'{origin.relative_to(site)}: invalid video target {value}')

    for document in documents:
        origin = site / 'assets/public-documents.json'
        directory = local_path(document['pageBaseUrl'], site / 'index.html')
        pages = document['pages']
        if type(pages) is not int or pages < 1:
            errors.append(f'document {document["id"]}: invalid page count')
            continue
        if directory:
            for number in range(1, pages + 1):
                image = directory / f'{number}.jpg'
                if not image.is_file():
                    errors.append(f'document {document["id"]}: missing JPG {image.relative_to(site)}')
                elif not image.read_bytes().startswith(b'\xff\xd8\xff'):
                    errors.append(f'document {document["id"]}: invalid JPG signature {image.relative_to(site)}')
                else:
                    counts['jpgPages'] += 1
        if document.get('pdfUrl'):
            link(document['pdfUrl'], site / 'index.html')

    for video in videos:
        duration = video.get('duration')
        if not finite(duration) or duration <= 0:
            errors.append(f'lecture {video["id"]}: invalid duration')
            continue
        transcript_path = local_path(video['transcriptUrl'], site / 'index.html')
        if transcript_path is None:
            continue
        if not transcript_path.is_file():
            errors.append(f'transcript {video["id"]}: missing {video["transcriptUrl"]}')
            continue
        transcript = read_json(transcript_path)
        if transcript.get('id') != video['id'] or transcript.get('automatic') is not True or not transcript.get('notice'):
            errors.append(f'transcript {video["id"]}: invalid id/automatic/notice metadata')
        segments = transcript.get('segments')
        if not isinstance(segments, list) or not segments:
            errors.append(f'transcript {video["id"]}: empty or invalid segments')
            continue
        previous = -1
        for position, segment in enumerate(segments):
            start, end = segment.get('start'), segment.get('end')
            if not finite(start) or not finite(end) or not 0 <= start < end <= duration + 1 or start < previous:
                errors.append(f'transcript {video["id"]} segment {position}: invalid time range/order')
            else:
                previous = start
            if not isinstance(segment.get('text'), str) or not segment['text'].strip():
                errors.append(f'transcript {video["id"]} segment {position}: empty text')
        counts['transcripts'] += 1
        counts['segments'] += len(segments)
        link(video['url'], site / 'index.html')

    global_chapters, global_questions = set(), set()
    for data, name in zip(libraries, SOURCES):
        system = data['system']
        origin = site / name
        unique(data['sources'], name + ' sources')
        unique(data['chapters'], name + ' chapters')
        sources = {s['id']: s for s in data['sources']}
        catalog_name = 'assets/catalog.json' if system == 'circulatory' else 'assets/respiratory/catalog.json'
        part_ids = unique(read_json(site / catalog_name)['parts'], catalog_name)
        req_path = site / ('auditoria/matriz_coracao.json' if system == 'circulatory' else 'assets/respiratory/requirements.json')
        requirements = unique(read_json(req_path)['alvos'], str(req_path.relative_to(site))) if req_path.exists() else set()
        for source in data['sources']:
            if 'url' in source:
                link(source['url'], site / 'index.html')
            if source['id'] in docs and source.get('pageCount') != docs[source['id']]['pages']:
                errors.append(f'{name}: source {source["id"]} pageCount disagrees with public documents')
        for chapter in data['chapters']:
            ident = chapter['id']
            if ident in global_chapters:
                errors.append(f'chapter: duplicate global id {ident}')
            global_chapters.add(ident)
            counts['chapters'] += 1
            for required in ('title', 'summary'):
                if not isinstance(chapter.get(required), str) or not chapter[required].strip():
                    errors.append(f'{ident}: missing {required}')
            questions = chapter.get('recall', [])
            unique(questions, ident + ' questions')
            for question in questions:
                if question['id'] in global_questions:
                    errors.append(f'question: duplicate global id {question["id"]}')
                global_questions.add(question['id'])
            counts['questions'] += len(questions)
            for part in chapter.get('partIds', []):
                if part not in part_ids:
                    errors.append(f'{ident}: unknown part id {part}')
            for requirement in chapter.get('requirementIds', []):
                if requirement not in requirements:
                    errors.append(f'{ident}: unknown requirement id {requirement}')
            for obj in objects(chapter):
                if 'source' not in obj:
                    continue
                source_id = obj['source']
                counts['references'] += 1
                if source_id not in sources:
                    errors.append(f'{ident}: unknown source {source_id}')
                    continue
                source = sources[source_id]
                if 'page' in obj:
                    page = obj['page']
                    bound = source.get('pageCount')
                    if type(page) is not int or page < 1 or (bound is not None and page > bound):
                        errors.append(f'{ident}: invalid page {page!r} for source {source_id} (limit {bound})')
                    if bound is None:
                        warnings.add(f'Source {source_id}: page range cannot be checked (no pageCount).')
                    if source_id not in docs:
                        warnings.add(f'Source {source_id}: no public JPG/PDF bundled; page metadata only, source file not tested.')
                if 'time' in obj:
                    token = obj['time']
                    values = re.split(r'[–—-]', token)
                    seconds = []
                    for value in values:
                        if not re.fullmatch(r'\d{1,3}:\d{2}(?::\d{2})?', value.strip()):
                            break
                        fields = [int(n) for n in value.strip().split(':')]
                        if any(n >= 60 for n in fields[1:]):
                            break
                        total = 0
                        for number in fields:
                            total = total * 60 + number
                        seconds.append(total)
                    if (len(seconds) != len(values) or len(seconds) not in (1, 2)
                            or seconds != sorted(seconds) or source_id not in lectures
                            or seconds[-1] > lectures[source_id]['duration'] + 1):
                        errors.append(f'{ident}: invalid lecture time {source_id} {token}')

    expected = build_index(root)
    index = read_json(site / 'assets/search-index.json')
    if index != expected:
        errors.append('search-index.json is stale or modified: run python scripts/build_study_search.py')
    for item in index.get('items', []):
        link(item['url'], site / 'index.html')

    # Static literal references only; expressions/templates are not claimed as verified.
    for path in sorted(site.rglob('*')):
        if not path.is_file() or any(part.startswith('.') or part == 'node_modules' for part in path.relative_to(site).parts):
            continue
        if path.suffix == '.html':
            for value in page_info(path).links:
                link(value, path)
        elif path.suffix == '.css':
            text = path.read_text(encoding='utf-8')
            for match in re.finditer(r'url\(\s*[\"\']?([^\"\')]+)[\"\']?\s*\)', text):
                link(match[1].strip(), path)
        elif path.suffix == '.js':
            text = path.read_text(encoding='utf-8')
            patterns = [r'''(?:from\s*|import\s*|import\s*\(|fetch\s*\()\s*['"]([^'"\n]+)['"]''']
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    value = match[1]
                    if value.startswith(('./', '../', '/', 'assets/', 'http://', 'https://')):
                        link(value, path)
    return {'errors': sorted(set(errors)), 'warnings': sorted(warnings), 'externalNotTested': sorted(external), 'counts': counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--json', action='store_true', help='Machine-readable report, including untested external URLs')
    args = parser.parse_args()
    try:
        report = validate(args.root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        report = {'errors': [f'Invalid library: {error}'], 'warnings': [], 'externalNotTested': [], 'counts': {}}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for error in report['errors']:
            print('ERROR: ' + error, file=sys.stderr)
        for warning in report['warnings']:
            print('WARNING: ' + warning)
        print(('FAIL' if report['errors'] else 'OK') + ': ' + json.dumps(report['counts'], ensure_ascii=False))
        print(f'External URLs NOT TESTED: {len(report["externalNotTested"])} (use --json for list)')
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
