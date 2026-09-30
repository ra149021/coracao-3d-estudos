"""Fetch two pinned official data files and verify their Git blob identities."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '6c7f9016bd5899ac8edafd31b9900c151df42ed6'
FILES = {
    'NervousSystem100': (53887724, '4ec6e3cb2a1ba821aca02c1d523ac614fdf41a02'),
    'LymphoidOrgans100': (2130876, 'fa39c3f65ecbf7d97c3f56ba47b4382e957ef85e'),
}


def fetch(name, size, expected_blob):
    path = ROOT / 'fontes/z_app' / f'{name}.fbx'
    url = f'https://raw.githubusercontent.com/LluisV/Z-Anatomy/{COMMIT}/Resources/Models/FBX/{name}.fbx'
    raw = path.read_bytes() if path.is_file() else urllib.request.urlopen(url, timeout=120).read()
    blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    if len(raw) != size or blob != expected_blob:
        raise ValueError(f'{name}: source identity mismatch')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    provenance = dict(url=url, file=f'fontes/z_app/{name}.fbx', bytes=len(raw),
                      sha256=hashlib.sha256(raw).hexdigest(), git_blob=blob, commit=COMMIT,
                      purpose='Original positioned mediastinal anatomy; common display transform')
    path.with_suffix('.fbx.provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'{name}: {len(raw)} bytes; pinned Git blob verified')


if __name__ == '__main__':
    for name, (size, expected_blob) in FILES.items():
        fetch(name, size, expected_blob)
