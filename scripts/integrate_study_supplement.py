"""Integrate the reviewed, public-text-only supplement without renaming chapters.

Run after reviewing expanded-study-supplement.json. Existing sections/questions
remain in their original positions. Re-running replaces only our named sections.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {'circulatory': 'site/assets/circulatory-theory.json', 'respiratory': 'site/assets/respiratory/theory.json'}
ALIASES = {'exp-heart': 'coracao', 'exp-vessels': 'vasos', 'exp-resp': 'respiratorio', 'exp-utah': 'utah_larynx'}
PUBLIC_URLS = {
    'exp-openstax-heart': 'https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy',
    'exp-openstax-electrical': 'https://openstax.org/books/anatomy-and-physiology-2e/pages/19-2-cardiac-muscle-and-electrical-activity',
    'exp-pulmonary-vascular': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6039811/',
}

def integrate(root=ROOT, check=False):
    source = json.loads((root / 'site/assets/expanded-study-supplement.json').read_text())
    theories = {system: json.loads((root / name).read_text()) for system, name in FILES.items()}
    declared = {item['id']: item for item in source['sources']}

    def remap(ref, system):
        ref = copy.deepcopy(ref)
        old = ref['source']
        ref['source'] = ALIASES.get(old, old)
        catalog = theories[system]['sources']
        if not any(item['id'] == ref['source'] for item in catalog):
            if old not in PUBLIC_URLS:
                raise ValueError('No reviewed public source mapping: ' + old)
            catalog.append({'id': old, 'label': declared[old]['label'], 'type': 'academic-reference', 'url': PUBLIC_URLS[old]})
        return ref

    cases = copy.deepcopy(source['cases'])
    for case in cases:
        system = case['system']
        assert any(c['id'] == case['chapterId'] for c in theories[system]['chapters'])
        case['references'] = [remap(ref, system) for ref in case['references']]
        if 'figure' in case:
            case['figure'] = remap(case['figure'], system)
    for proposal in source['chapterProposals']:
        system = proposal['system']
        chapter = next(c for c in theories[system]['chapters'] if c['id'] == proposal['chapterId'])
        section = {key: copy.deepcopy(proposal[key]) for key in ['heading', 'paragraphs']}
        section['id'] = 'expanded-section-' + proposal['chapterId']
        section['references'] = [remap(ref, system) for ref in proposal['references']]
        existing = next((i for i, item in enumerate(chapter['sections']) if item.get('id') == section['id']), None)
        if existing is None:
            chapter['sections'].append(section)
        else:
            chapter['sections'][existing] = section
    for system, theory in theories.items():
        for chapter in theory['chapters']:
            related = [{'id': case['id'], 'title': case['title']} for case in cases if case['system'] == system and case['chapterId'] == chapter['id']]
            if related:
                chapter['appliedCases'] = related
            else:
                chapter.pop('appliedCases', None)
    outputs = {FILES[system]: data for system, data in theories.items()}
    outputs['site/assets/study-cases.json'] = {'version': 1, 'notice': source['notice'], 'cases': cases}
    changed = []
    for filename, data in outputs.items():
        path = root / filename
        text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if not path.exists() or path.read_text() != text:
            changed.append(filename)
            if not check:
                path.write_text(text)
    return changed

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = integrate(check=args.check)
    print(json.dumps({'status': 'stale' if args.check and changed else 'ok', 'changed': changed}, ensure_ascii=False))
    raise SystemExit(1 if args.check and changed else 0)
