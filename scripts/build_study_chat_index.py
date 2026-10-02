"""Index existing, attributed theory sections for retrieval in the study chat."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BLOBS = {
    'assets/circulatory-theory.json': 'b94e2215a4e8fa46eb281dda4f88e919680b8d91',
    'assets/respiratory/theory.json': '43cd9077504a9a5a047995dcc277cf39f9d178e1',
}
entries = []
for system, relative in [('circulatory', 'assets/circulatory-theory.json'), ('respiratory', 'assets/respiratory/theory.json')]:
    raw = (ROOT / 'site' / relative).read_bytes()
    blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    if blob != PUBLIC_BLOBS[relative]:
        raise ValueError('A fonte mudou: confirme sua publicação antes de gerar contexto para uma API externa.')
    document = json.loads(raw)
    for chapter in document['chapters']:
        for ordinal, section in enumerate(chapter['sections']):
            texts = section.get('paragraphs', []) + section.get('bullets', [])
            table = section.get('table', {})
            texts += [' · '.join(map(str, row)) for row in table.get('rows', [])]
            text = '\n'.join(texts).strip()
            if not text:
                continue
            entries.append({'id': f"{chapter['id']}-{ordinal}", 'system': system, 'chapterId': chapter['id'],
                            'chapter': chapter['title'], 'heading': section['heading'], 'text': text,
                            'href': f"theory.html?system={system}&chapter={chapter['id']}",
                            'references': section.get('references', [])})
(ROOT / 'site/assets/study-chat-index.json').write_text(json.dumps({'version': 2, 'externalContextPolicy': 'verified-public-source-text-only',
    'publicSourceBlobs': PUBLIC_BLOBS, 'entries': entries}, ensure_ascii=False, indent=2) + '\n')
print(f'{len(entries)} attributed sections indexed')
