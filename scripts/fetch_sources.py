"""Download public anatomy data only; never execute downloaded content."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'fontes'
DATA.mkdir(exist_ok=True)
ALLOWED = {'api.github.com', 'raw.githubusercontent.com', 'dbarchive.biosciencedbc.jp', 'download.blender.org'}


def fetch(url, name, git_sha=None):
    assert urllib.parse.urlparse(url).scheme == 'https'
    assert urllib.parse.urlparse(url).hostname in ALLOWED
    target = DATA / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        data = target.read_bytes()
    else:
        req = urllib.request.Request(url, headers={'User-Agent': 'Local-Anatomy-Audit/1.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        target.write_bytes(data)
    if git_sha:
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if actual != git_sha:
            raise ValueError(f'Git blob mismatch: {name}')
    record = {'url': url, 'file': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': git_sha}
    target.with_suffix(target.suffix + '.provenance.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record), flush=True)
    return data


def catalog():
    for repo, branch, dest in [('Z-Anatomy/Models-of-human-anatomy', 'master', 'z_models_tree.json'),
                               ('LluisV/Z-Anatomy', 'PC-Version', 'z_app_tree.json')]:
        raw = fetch(f'https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1', dest)
        obj = json.loads(raw)
        print('TREE', repo, 'commit/tree', obj.get('sha'), 'truncated', obj.get('truncated'))
        for row in obj.get('tree', []):
            if row['type'] == 'blob' and (repo.endswith('Models-of-human-anatomy') or row['path'].startswith('Resources/Models/') or 'Cardio' in row['path']):
                print(row['path'], row.get('size'))
    base = 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
    for name in ['isa_parts_list_e.txt', 'isa_element_parts.txt', 'partof_parts_list_e.txt', 'partof_element_parts.txt', 'README_e.html']:
        fetch(base + name, 'bp3d/' + name)


def assets():
    for tree_name, repo, targets in [
        ('z_models_tree.json', 'Z-Anatomy/Models-of-human-anatomy', ['Z-Anatomy.zip', 'License.txt', 'Readme.md', 'TO DO List']),
        ('z_app_tree.json', 'LluisV/Z-Anatomy', ['Resources/Models/FBX/CardioVascular41.fbx', 'Resources/Models/FBX/References100.fbx', 'Resources/Models/License.txt'])]:
        tree = json.loads((DATA / tree_name).read_text())
        for row in tree['tree']:
            if row['path'] in targets:
                path = urllib.parse.quote(row['path'])
                folder = 'z_anatomy' if tree_name == 'z_models_tree.json' else 'z_app'
                fetch(f'https://raw.githubusercontent.com/{repo}/{tree["sha"]}/{path}', folder + '/' + Path(row['path']).name, row['sha'])
    fetch('https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip', 'bp3d/isa_BP3D_4.0_obj_99.zip')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['catalog', 'assets'])
    args = parser.parse_args()
    {'catalog': catalog, 'assets': assets}[args.operation]()
