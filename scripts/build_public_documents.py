"""Prepare the selected classroom documents for the static site and release."""
from pathlib import Path
import hashlib
import json
import shutil
import fitz

ROOT = Path(__file__).resolve().parents[1]
local = json.loads((ROOT / 'materiais/library-manifest.json').read_text())
catalog = json.loads((ROOT / 'site/assets/classroom.json').read_text())
release = ROOT / 'materiais/public-documents'
release.mkdir(parents=True, exist_ok=True)
documents = []
for item in catalog['documents']:
    identifier = item['id']
    entry = local['documents'][identifier]
    source = Path(entry['path'])
    with fitz.open(source) as pdf:
        assert len(pdf) == item['pages'], identifier
    target = ROOT / 'site/assets/lectures/slides' / identifier
    target.mkdir(parents=True, exist_ok=True)
    for number in range(1, item['pages'] + 1):
        shutil.copyfile(Path(entry['pageDirectory']) / f'{number}.jpg', target / f'{number}.jpg')
    shutil.copyfile(source, release / f'{identifier}.pdf')
    documents.append({
        'id': identifier, 'pages': item['pages'],
        'pageBaseUrl': f'assets/lectures/slides/{identifier}',
        'pdfUrl': f'https://github.com/ra149021/coracao-3d-estudos/releases/download/aulas-v1/{identifier}.pdf',
        'bytes': source.stat().st_size,
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    })
index = {'version': 1, 'documents': documents,
         'notice': 'Material docente · Carmem / UEM. Páginas e legendas preservadas; autoria independente das licenças das malhas do atlas.'}
(ROOT / 'site/assets/public-documents.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'documents': len(documents), 'pages': sum(d['pages'] for d in documents)}))
