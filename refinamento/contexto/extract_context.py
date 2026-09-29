"""Extract existing Z-Anatomy context meshes, preserving every source triangle.

Reads the local cardiovascular GLB only. Does not write site assets or mutate
source data. World transform and site centering match build_heart_site_assets.py.
"""
from pathlib import Path
import hashlib
import json
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'malhas/CardioVascular41.glb'
PARTS = [
    ('brachiocephalic_trunk', 'Brachiocephalic trunk', 'Tronco braquiocefálico', '85', 'arteria'),
    ('right_common_carotid', 'Right common carotid artery', 'Artéria carótida comum direita', '86', 'arteria'),
    ('right_subclavian', 'Right subclavian artery', 'Artéria subclávia direita', '87', 'arteria'),
    ('left_common_carotid', 'Left common carotid artery', 'Artéria carótida comum esquerda', '88', 'arteria'),
    ('left_subclavian', 'Left subclavian artery', 'Artéria subclávia esquerda', '89', 'arteria'),
    ('right_internal_carotid', 'Internal carotid artery.r', 'Artéria carótida interna direita', '90', 'arteria'),
    ('left_internal_carotid', 'Internal carotid artery.l', 'Artéria carótida interna esquerda', '90', 'arteria'),
    ('right_external_carotid', 'External carotid artery.r', 'Artéria carótida externa direita', '91', 'arteria'),
    ('left_external_carotid', 'External carotid artery.l', 'Artéria carótida externa esquerda', '91', 'arteria'),
    ('thoracic_aorta', 'Thoracic aorta', 'Aorta descendente torácica', '92', 'arteria'),
    ('abdominal_aorta', 'Abdominal aorta', 'Aorta descendente abdominal', '93', 'arteria'),
    ('right_musculophrenic', 'Musculophrenic artery.r', 'Artéria musculofrênica direita', '116', 'arteria'),
    ('left_musculophrenic', 'Musculophrenic artery.l', 'Artéria musculofrênica esquerda', '116', 'arteria'),
    ('superior_phrenic', 'Superior phrenic arteries', 'Artérias frênicas superiores', '119', 'arteria'),
    ('azygos', 'Azygos vein', 'Veia ázigos', '122a', 'veia'),
    ('hemiazygos', 'Hemi-azygos vein', 'Veia hemiázigos', '122b', 'veia'),
    ('accessory_hemiazygos', 'Accessory hemi-azygos vein', 'Veia hemiázigos acessória', '122c', 'veia'),
]

raw = SOURCE.read_bytes()
assert raw[:4] == b'glTF'
assert struct.unpack_from('<I', raw, 4)[0] == 2
assert struct.unpack_from('<I', raw, 8)[0] == len(raw)
json_len, chunk_type = struct.unpack_from('<II', raw, 12)
assert chunk_type == 0x4e4f534a
scene = json.loads(raw[20:20 + json_len])
bin_len, chunk_type = struct.unpack_from('<II', raw, 20 + json_len)
assert chunk_type == 0x004e4942
binary = raw[28 + json_len:28 + json_len + bin_len]
assert len(binary) == bin_len
world = {}


def visit(index, parent):
    node = scene['nodes'][index]
    # Same matrix-only traversal as the main builder. No local registration.
    assert not any(k in node for k in ('translation', 'rotation', 'scale'))
    matrix = np.array(node.get('matrix', np.eye(4).flatten())).reshape(4, 4).T
    world[index] = parent @ matrix
    for child in node.get('children', []):
        visit(child, world[index])


for top in scene['scenes'][scene.get('scene', 0)]['nodes']:
    visit(top, np.eye(4))


def accessor(index):
    acc = scene['accessors'][index]
    assert not acc.get('sparse')
    view = scene['bufferViews'][acc['bufferView']]
    assert view['buffer'] == 0
    dim = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[acc['type']]
    dtype = np.dtype({5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[acc['componentType']])
    return np.ndarray((acc['count'], dim), dtype=dtype, buffer=binary,
                      offset=view.get('byteOffset', 0) + acc.get('byteOffset', 0),
                      strides=(view.get('byteStride', dim * dtype.itemsize), dtype.itemsize)).copy()


lookup = {}
for index, node in enumerate(scene['nodes']):
    if 'mesh' in node:
        lookup.setdefault(node.get('name', ''), []).append(index)

center = np.array([2.0, 130.5, 2.0])
scale = 0.25
meshdir = OUT / 'meshes'
meshdir.mkdir(exist_ok=True)
requirements = {a['id']: a for a in json.loads((ROOT / 'site/auditoria/matriz_coracao.json').read_text())['alvos']}
parts = []
for suffix, name, label, rid, kind in PARTS:
    assert len(lookup.get(name, [])) == 1, (name, lookup.get(name))
    nid = lookup[name][0]
    node = scene['nodes'][nid]
    source_primitives = scene['meshes'][node['mesh']]['primitives']
    vertices_chunks, faces_chunks, offset = [], [], 0
    for primitive in source_primitives:
        assert primitive.get('mode', 4) == 4
        vertices = accessor(primitive['attributes']['POSITION'])
        vertices = vertices @ world[nid][:3, :3].T + world[nid][:3, 3]
        faces = accessor(primitive['indices']).reshape(-1, 3).astype(np.uint32)
        if np.linalg.det(world[nid][:3, :3]) < 0:
            faces = faces[:, [0, 2, 1]]
        vertices_chunks.append(vertices)
        faces_chunks.append(faces + offset)
        offset += len(vertices)
    world_vertices = np.concatenate(vertices_chunks)
    faces = np.concatenate(faces_chunks).astype('<u4')
    vertices = ((world_vertices - center) * scale).astype('<f4')
    assert np.isfinite(vertices).all() and len(vertices) > 2 and len(faces) > 0
    assert faces.min() >= 0 and faces.max() < len(vertices)
    assert len(faces) == sum(scene['accessors'][p['indices']]['count'] // 3 for p in source_primitives)
    identifier = 'ctx_' + suffix
    path = meshdir / (identifier + '.npz')
    np.savez_compressed(path, vertices=vertices, faces=faces)
    saved = np.load(path, allow_pickle=False)
    assert np.array_equal(saved['vertices'], vertices) and np.array_equal(saved['faces'], faces)
    note = 'Geometria original preservada; relações espaciais e continuidade com as estruturas vizinhas ainda precisam de conferência individual.'
    if rid in ['90', '91']:
        note += ' Inclui a extensão original do vaso cervical/cranial; não foi recortada nem ampliada por dados de outros vasos.'
    if rid == '93':
        note += ' Segmento abdominal do roteiro; mostrar apenas quando o contexto vascular for ativado.'
    parts.append({
        'id': identifier, 'labelPT': label, 'label': label,
        'sourceName': name, 'requirementId': rid,
        'requirement': {'id': rid, 'label': requirements[rid]['estrutura'], 'source': requirements[rid]['fonte'], 'page': requirements[rid]['pagina']},
        'vertices': len(vertices), 'faces': len(faces), 'triangles': len(faces),
        'bounds': [vertices.min(0).tolist(), vertices.max(0).tolist()],
        'file': 'meshes/' + path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'color': '#b76560' if kind == 'arteria' else '#7597b1', 'tipo': kind,
        'grupo': 'contexto', 'group': 'contexto', 'defaultVisible': False,
        'source': 'Z-Anatomy', 'sourceFile': 'CardioVascular41.fbx via local GLB',
        'license': 'CC BY-SA 4.0', 'sourceNode': nid, 'sourceMesh': node['mesh'],
        'sourcePrimitiveCount': len(source_primitives),
        'sourceWorldMatrix': world[nid].tolist(),
        'sourceWorldBounds': [world_vertices.min(0).tolist(), world_vertices.max(0).tolist()],
        'processing': 'Original primitive vertices and triangles; full node world transform; ((world - [2, 130.5, 2]) * 0.25). No cut, weld, smoothing, deformation, local registration or synthesized anatomy.',
        'correspondence': 'associated', 'anatomicalValidation': 'pending_individual_review',
        'quizEligible': False, 'note': note,
    })

excluded = [
    {'requirementId': '30j', 'reason': 'Aorta is a composite requirement. Existing ascending/arch and exported thoracic/abdominal segments can support a group selection; no duplicate mesh was created.'},
    {'requirementId': '117', 'reason': 'Bronchial artery has a BP3D candidate FMA68109/FJ1933, but no exactly named mesh in this cardiovascular GLB.'},
    {'requirementId': '118', 'reason': 'Esophageal artery has a BP3D candidate FMA4149/FJ1934, but no exactly named mesh in this cardiovascular GLB.'},
    {'requirementId': '123', 'reason': 'Vagus meshes were not found in this GLB. Startup.blend inventories curve objects Vagus nerve (X).l/.r. No claim of complete or partial nerve coverage from this export.'},
    {'requirementId': '125', 'reason': 'Sympathetic trunk curves are in Startup.blend, not this cardiovascular GLB.'},
    {'requirementId': 'V42c', 'reason': 'Inferior tracheobronchial nodes have a named nonempty MESH in Startup.blend, but are absent from this cardiovascular GLB; not exported.'},
    {'requirementId': 'V42d', 'reason': 'Paratracheal cervical/thoracic nodes have named nonempty MESH objects in Startup.blend, but are absent from this cardiovascular GLB; not exported.'},
]
metadata = {
    'version': 1, 'parts': parts,
    'summary': {'objects': len(parts), 'requirementIds': sorted({p['requirementId'] for p in parts}),
                'requirements': len({p['requirementId'] for p in parts}),
                'arterias': sum(p['tipo'] == 'arteria' for p in parts),
                'veias': sum(p['tipo'] == 'veia' for p in parts), 'linfaticos': 0,
                'vertices': sum(p['vertices'] for p in parts), 'triangles': sum(p['faces'] for p in parts),
                'anatomicallyValidatedParts': 0},
    'source': {'file': str(SOURCE.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
               'license': 'CC BY-SA 4.0', 'upstream': 'https://github.com/LluisV/Z-Anatomy/tree/PC-Version/Resources/Models',
               'identityRecord': 'fontes/z_app/CardioVascular41.fbx.provenance.json'},
    'transform': {'method': 'Same source node world transform and site centering as main builder',
                  'sourceUnits': 'Original FBX/GLB world coordinates; site display units, not a clinical measurement scale',
                  'center': center.tolist(), 'uniformScale': scale,
                  'formula': '(source_world_vertices - [2, 130.5, 2]) * 0.25'},
    'integration': {'group': 'contexto', 'defaultVisible': False, 'includeInInitialCameraFit': False,
                    'quizEligibleByDefault': False,
                    'instruction': 'Optional context layer; keep main cardiac view and fit independent of distant cervical/abdominal extents. All source geometry was preserved.'},
    'excludedCandidates': excluded,
    'validation': {'finiteVertices': True, 'validIndices': True, 'sourceTriangleCountsPreserved': True,
                   'npzReadbackExact': True, 'anatomicalValidation': 'not_performed'},
    'limitations': ['Availability of a named source object is not anatomical validation.',
                    'The vessels were not individually repositioned or registered.',
                    'No phrenic nerve, pericardiacophrenic vessel, cardiac plexus, lymphatic duct or inferred connection was added.',
                    'Cervical/abdominal context is preserved at original extent; only the selected named objects were exported.'],
}
(OUT / 'context.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(metadata['summary'], ensure_ascii=False, indent=2))
