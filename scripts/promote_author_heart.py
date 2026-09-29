"""Validate the evaluated author surfaces and promote them, preserving a local baseline."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'fontes/quality_baseline_v03'
CANDIDATE = ROOT / 'site/assets/heart-author'
DEST = ROOT / 'site/assets'

def arrays(path):
    raw = path.read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20 + length])
    binary = raw[28 + length:]
    def read(index):
        accessor = doc['accessors'][index]
        view = doc['bufferViews'][accessor['bufferView']]
        dim = {'SCALAR': 1, 'VEC3': 3}[accessor['type']]
        dtype = np.dtype({5126: '<f4', 5125: '<u4', 5123: '<u2'}[accessor['componentType']])
        return np.ndarray((accessor['count'], dim), dtype=dtype, buffer=binary,
            offset=view.get('byteOffset', 0) + accessor.get('byteOffset', 0),
            strides=(view.get('byteStride', dim * dtype.itemsize), dtype.itemsize)).copy()
    result = {}
    for node in doc['nodes']:
        if 'mesh' not in node:
            continue
        primitive = doc['meshes'][node['mesh']]['primitives'][0]
        result[node.get('extras', {}).get('partId', node['name'])] = [
            read(primitive['attributes']['POSITION']), read(primitive['attributes']['NORMAL']),
            read(primitive['indices'])]
    return result

BASE.mkdir(parents=True, exist_ok=True)
for name in ('heart.glb', 'catalog.json'):
    if not (BASE / name).exists():
        shutil.copy2(DEST / name, BASE / name)
old = arrays(BASE / 'heart.glb')
new = arrays(CANDIDATE / 'model.glb')
assert old.keys() == new.keys()
changed = [key for key in old if any(not np.array_equal(a, b) for a, b in zip(old[key], new[key]))]
assert changed == ['heart_00', 'heart_01', 'heart_02', 'heart_03'], changed
for vertices, normals, indices in new.values():
    assert np.isfinite(vertices).all() and np.isfinite(normals).all()
    assert indices.max() < len(vertices)
    assert np.allclose(np.linalg.norm(normals, axis=1), 1, atol=1e-5)
catalog = json.loads((CANDIDATE / 'catalog.json').read_text())
catalog['title'] = 'Coração e circulação'
catalog['model']['file'] = 'heart.glb'
catalog['surfaceEvaluation']['limitation'] = 'Modificadores originais melhoram a continuidade das superfícies das quatro câmaras; não acrescentam estruturas internas ou certificam precisão anatômica.'
shutil.copy2(CANDIDATE / 'model.glb', DEST / 'heart.glb')
(DEST / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
report = dict(accepted=True, method='Somente SUBSURF com parâmetros de renderização originais do autor',
    changed=changed, unchangedMeshes=len(new)-len(changed), oldTriangles=sum(len(v[2])//3 for v in old.values()),
    newTriangles=sum(len(v[2])//3 for v in new.values()), bytes=(DEST/'heart.glb').stat().st_size,
    baselineSha256=hashlib.sha256((BASE/'heart.glb').read_bytes()).hexdigest(),
    sha256=hashlib.sha256((DEST/'heart.glb').read_bytes()).hexdigest(),
    finite=True, validIndices=True, unitNormals=True, anatomicalCoverageChanged=False, newStructures=0)
(ROOT / 'refinamento/qualidade/heart_author_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False))
