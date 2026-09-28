"""Check the local reference conversion against its original STL-derived NPZ.

No remote requests; no modifications to positions, connectivity or assets.
The report is local because the source assets are not cleared for publication.
"""
from pathlib import Path
import hashlib
import json
import struct
import numpy as np

LOCAL = Path(__file__).resolve().parent / 'referencias_locais'
raw = (LOCAL / 'umn_reference.glb').read_bytes()
magic, version, size = struct.unpack_from('<4sII', raw)
assert (magic, version, size) == (b'glTF', 2, len(raw))
json_size, kind = struct.unpack_from('<II', raw, 12)
assert kind == 0x4e4f534a
gltf = json.loads(raw[20:20 + json_size])
binary_start = 28 + json_size
binary_size, binary_kind = struct.unpack_from('<II', raw, 20 + json_size)
assert binary_kind == 0x004e4942 and binary_size == len(raw) - binary_start
catalog = json.loads((LOCAL / 'umn_reference_catalog.json').read_text())
assert hashlib.sha256(raw).hexdigest() == catalog['sha256']
center = np.array(catalog['display_transform']['center_source_units'], dtype=np.float32)


def accessor(index):
    entry = gltf['accessors'][index]
    view = gltf['bufferViews'][entry['bufferView']]
    dtype = {5126: '<f4', 5125: '<u4'}[entry['componentType']]
    components = {'VEC3': 3, 'SCALAR': 1}[entry['type']]
    offset = binary_start + view.get('byteOffset', 0) + entry.get('byteOffset', 0)
    return np.frombuffer(raw, dtype=dtype, count=entry['count'] * components,
                         offset=offset).reshape(entry['count'], components)


results = []
assert len(gltf['meshes']) == len(catalog['parts']) == 4
for part, mesh in zip(catalog['parts'], gltf['meshes']):
    source = np.load(LOCAL / (part['sourceName'] + '.npz'), allow_pickle=False)
    primitive = mesh['primitives'][0]
    vertices = accessor(primitive['attributes']['POSITION'])
    normals = accessor(primitive['attributes']['NORMAL'])
    faces = accessor(primitive['indices']).reshape(-1, 3)
    expected = ((source['vertices'] - center)[:, [0, 2, 1]] * [.025, .025, -.025]).astype('<f4')
    assert np.array_equal(vertices, expected)
    assert np.array_equal(faces, source['faces'])
    assert np.isfinite(vertices).all() and np.isfinite(normals).all()
    assert faces.min() >= 0 and faces.max() < len(vertices)
    lengths = np.linalg.norm(normals, axis=1)
    areas_twice = np.linalg.norm(np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]],
                                          vertices[faces[:, 2]] - vertices[faces[:, 0]]), axis=1)
    assert np.allclose(lengths, 1, atol=1e-6)
    assert (areas_twice > 0).all()
    results.append({'id': part['id'], 'positions_equal_expected_transform': True,
                    'triangles_equal_source': True, 'finite': True,
                    'indices_in_bounds': True, 'zero_area_triangles': 0,
                    'zero_normals': 0, 'normal_length_min': float(lengths.min()),
                    'normal_length_max': float(lengths.max())})

report = {'glb_header_length_hash_valid': True, 'sha256': catalog['sha256'], 'parts': results}
(LOCAL / 'umn_glb_verificacao.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
