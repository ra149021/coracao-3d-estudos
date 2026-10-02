"""Download four attributed anatomical photographs from Wikimedia Commons.

Preserves original bytes, verifies the current license, and keeps this public
collection separate from the personal Anki originals and their derivatives.
"""
import hashlib
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ('Coronary arteries 1.jpg', 'publiccirculatorio_001', 'circulatory', 'coronarias', 'Artérias coronárias — peça humana', ['coronárias', 'coração']),
    ('Aortic valves.jpg', 'publiccirculatorio_002', 'circulatory', 'valvas', 'Valva aórtica — peça humana', ['valva aórtica', 'coração']),
    ('Human left lung.jpg', 'publicrespiratorio_001', 'respiratory', 'pulmoes', 'Pulmão esquerdo — peça humana', ['pulmão esquerdo', 'pulmões']),
    ('Right lung.jpg', 'publicrespiratorio_002', 'respiratory', 'pulmoes', 'Pulmão direito — peça humana', ['pulmão direito', 'pulmões']),
]


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'AtlasCardiorrespiratorio/1.0 (educational source verification)'})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError('Arquivo acima do limite esperado.')
    return data


def main():
    params = {'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size',
              'titles': '|'.join('File:' + file[0] for file in FILES)}
    data = json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)))
    pages = {page['title']: page['imageinfo'][0] for page in data['query']['pages'].values()}
    directory = ROOT / 'site/assets/public-specimens/originals'
    directory.mkdir(parents=True, exist_ok=True)
    images = []
    for name, identity, system, region, title, terms in FILES:
        info = pages['File:' + name]
        metadata = info['extmetadata']
        if metadata['LicenseShortName']['value'] != 'CC BY-SA 3.0' or 'Anatomist90' not in metadata['Artist']['value']:
            raise ValueError('Crédito ou licença alterados na fonte: ' + name)
        parts = urllib.parse.urlsplit(info['url'])
        if parts.scheme != 'https' or parts.hostname != 'upload.wikimedia.org':
            raise ValueError('Origem não oficial.')
        download = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))
        raw = get(download)
        image = Image.open(io.BytesIO(raw))
        image.load()
        if image.format != 'JPEG' or image.size != (info['width'], info['height']):
            raise ValueError('Formato ou tamanho diferente do declarado.')
        destination = directory / (identity + '.jpg')
        destination.write_bytes(raw)
        relative = destination.relative_to(ROOT / 'site').as_posix()
        images.append({'id': identity, 'system': system, 'region': region, 'kind': 'cadaver', 'viewType': 'photo',
                       'title': title, 'terms': terms, 'width': info['width'], 'height': info['height'],
                       'sourceFile': name, 'package': 'Wikimedia Commons · Anatomist90', 'noteIds': [],
                       'original': relative, 'thumbnail': relative, 'sha256': hashlib.sha256(raw).hexdigest(),
                       'sourceUrl': 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(name.replace(' ', '_')),
                       'downloadUrl': download, 'author': 'Anatomist90', 'license': 'CC BY-SA 3.0',
                       'licenseUrl': 'https://creativecommons.org/licenses/by-sa/3.0/', 'changes': 'Original JPEG preservado sem alterações.'})
    manifest = {'version': 2, 'collection': 'public', 'labelStatus': 'Nomes das peças conforme as descrições da fonte; sem rótulos locais acrescentados.',
                'counts': {'baseImages': 4, 'crops': 0, 'photoViews': 4, 'sheets': 0},
                'regions': {'coronarias': 'Coronárias', 'valvas': 'Valvas', 'pulmoes': 'Pulmões'}, 'images': images}
    (ROOT / 'site/assets/cadaver-public-gallery.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('4 imagens públicas, CC BY-SA 3.0, originais preservados.')


if __name__ == '__main__':
    main()
