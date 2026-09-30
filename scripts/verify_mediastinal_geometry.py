"""Verify preserved atlas arrays and source identity entirely from local files.

Run with the project's prepared Python environment. Only the JSON report is
written; no atlas, requirement, classification or source file is changed.
Equality establishes preservation of the converted source geometry. It does
not establish anatomical accuracy, completeness or individual visual approval.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile

import numpy as np

sys.dont_write_bytecode = True
from build_respiratory_assets import SourceGLB

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'refinamento/qualidade/mediastino/geometry_validation.json'
BASELINE = 'cc95e5f6cf91b4329ffa3542e5e5d354d5cad137'
SOURCE_COMMIT = '6c7f9016bd5899ac8edafd31b9900c151df42ed6'
CENTER = np.array([0., 142., 0.])
SCALE = .2
NEW_PARTS = [
    ('Oesophagus', 'VisceralSystem100', 'contexto_mediastino', []),
    ('Ascending aorta', 'CardioVascular41', 'contexto_mediastino', []),
    ('Aortic arch', 'CardioVascular41', 'contexto_mediastino', []),
    ('Thoracic aorta', 'CardioVascular41', 'contexto_mediastino', []),
    ('Left subclavian artery', 'CardioVascular41', 'contexto_mediastino', []),
    ('Superior vena cava', 'CardioVascular41', 'contexto_mediastino', []),
    ('Azygos vein', 'CardioVascular41', 'contexto_mediastino', []),
    ('Inferior tracheobronchial nodes', 'LymphoidOrgans100', 'linfaticos_torax', ['R186']),
    ('Superior tracheobronchial nodes', 'LymphoidOrgans100', 'linfaticos_torax', ['R187']),
    ('Paratracheal cervical nodes', 'LymphoidOrgans100', 'linfaticos_torax', ['R188']),
    ('Paratracheal thoracic nodes', 'LymphoidOrgans100', 'linfaticos_torax', ['R188']),
    ('Vagus nerve (X).l', 'NervousSystem100', 'nervos_torax', ['R181']),
    ('Vagus nerve (X).r', 'NervousSystem100', 'nervos_torax', ['R181']),
    ('Sympathetic trunk.l', 'NervousSystem100', 'nervos_torax', ['R184']),
    ('Sympathetic trunk.r', 'NervousSystem100', 'nervos_torax', ['R184']),
]
NEW_IDS = [
    'resp_oesophagus', 'resp_ascending_aorta', 'resp_aortic_arch', 'resp_thoracic_aorta',
    'resp_left_subclavian_artery', 'resp_superior_vena_cava', 'resp_azygos_vein',
    'resp_inferior_tracheobronchial_nodes', 'resp_superior_tracheobronchial_nodes',
    'resp_paratracheal_cervical_nodes', 'resp_paratracheal_thoracic_nodes',
    'resp_vagus_nerve_x_l', 'resp_vagus_nerve_x_r',
    'resp_sympathetic_trunk_l', 'resp_sympathetic_trunk_r',
]
# Independently pinned identities, rather than accepting provenance claims.
NEW_FBX = {
    'NervousSystem100': {
        'bytes': 53887724,
        'git_blob': '4ec6e3cb2a1ba821aca02c1d523ac614fdf41a02',
        'sha256': '3ea1aad64956cad27348a27b8fb50494b7cc307c6bc77bee0810ec2a67dff2b1',
    },
    'LymphoidOrgans100': {
        'bytes': 2130876,
        'git_blob': 'fa39c3f65ecbf7d97c3f56ba47b4382e957ef85e',
        'sha256': '310ff82f502f4f3a79e85f99ddc2009bba9514338119af9edff87b20cf1b3609',
    },
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def baseline_bytes(path):
    return subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT)


class AtlasGLB:
    """Read uncompressed accessor arrays without applying any node transform."""

    def __init__(self, raw):
        require(raw[:4] == b'glTF', 'Invalid GLB signature')
        version, total = struct.unpack_from('<II', raw, 4)
        require(version == 2 and total == len(raw), 'Invalid GLB version or size')
        size, kind = struct.unpack_from('<II', raw, 12)
        require(kind == 0x4e4f534a, 'Missing JSON chunk')
        self.g = json.loads(raw[20:20 + size])
        bin_size, kind = struct.unpack_from('<II', raw, 20 + size)
        require(kind == 0x004e4942, 'Missing BIN chunk')
        self.binary = raw[28 + size:]
        require(bin_size == len(self.binary), 'Invalid BIN chunk size')
        require(self.g['buffers'] == [{'byteLength': len(self.binary)}], 'Invalid buffer declaration')
        self.nodes = {node['name']: node for node in self.g['nodes']}
        require(len(self.nodes) == len(self.g['nodes']), 'Duplicate GLB node names')

    def accessor(self, index):
        acc = self.g['accessors'][index]
        view = self.g['bufferViews'][acc['bufferView']]
        require(view['buffer'] == 0 and not acc.get('sparse'), 'Unexpected accessor storage')
        width = {'SCALAR': 1, 'VEC3': 3}[acc['type']]
        dtype = np.dtype({5126: '<f4', 5125: '<u4'}[acc['componentType']])
        start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
        stride = view.get('byteStride', width * dtype.itemsize)
        end = start + (acc['count'] - 1) * stride + width * dtype.itemsize
        require(acc['count'] > 0 and start >= 0 and stride >= width * dtype.itemsize
                and start % dtype.itemsize == 0
                and end <= view.get('byteOffset', 0) + view['byteLength'] <= len(self.binary),
                'Accessor exceeds BIN or buffer view storage')
        result = np.ndarray((acc['count'], width), dtype=dtype, buffer=self.binary,
                            offset=start, strides=(stride, dtype.itemsize)).copy()
        if acc['type'] == 'VEC3':
            require(acc.get('min') == result.min(0).tolist() and acc.get('max') == result.max(0).tolist(),
                    'Accessor min/max disagree with stored arrays')
        return result

    def arrays(self, part_id):
        node = self.nodes[part_id]
        require(not any(k in node for k in ('matrix', 'translation', 'rotation', 'scale')),
                f'{part_id}: output node adds a transform')
        require(not any(k in node for k in ('skin', 'children')) and node.get('extras') == {'partId': part_id},
                f'{part_id}: unexpected hierarchy, skin or part ID')
        primitives = self.g['meshes'][node['mesh']]['primitives']
        require(len(primitives) == 1 and primitives[0].get('mode', 4) == 4,
                f'{part_id}: expected one triangle primitive')
        primitive = primitives[0]
        require('targets' not in primitive, f'{part_id}: unexpected morph targets')
        for key, accessor in [('POSITION', primitive['attributes']['POSITION']),
                              ('NORMAL', primitive['attributes']['NORMAL']),
                              ('indices', primitive['indices'])]:
            acc = self.g['accessors'][accessor]
            require((acc['type'], acc['componentType']) == (('SCALAR', 5125) if key == 'indices' else ('VEC3', 5126)),
                    f'{part_id}: unexpected {key} accessor type')
        return {'POSITION': self.accessor(primitive['attributes']['POSITION']),
                'NORMAL': self.accessor(primitive['attributes']['NORMAL']),
                'indices': self.accessor(primitive['indices'])}


def verify():
    model_path = ROOT / 'site/assets/respiratory/model.glb'
    model_raw = model_path.read_bytes()
    base_raw = baseline_bytes('site/assets/respiratory/model.glb')
    model, baseline = AtlasGLB(model_raw), AtlasGLB(base_raw)
    catalog = json.loads((ROOT / 'site/assets/respiratory/catalog.json').read_text())
    base_catalog = json.loads(baseline_bytes('site/assets/respiratory/catalog.json'))
    requirements_raw = (ROOT / 'site/assets/respiratory/requirements.json').read_bytes()
    require(requirements_raw == baseline_bytes('site/assets/respiratory/requirements.json'),
            'Requirement classifications or validation changed from the baseline')
    requirements = {r['id']: r for r in json.loads(requirements_raw)['alvos']}
    parts, old_parts = catalog['parts'], base_catalog['parts']
    require(len(old_parts) == 175 and len(parts) == 190, 'Expected 175 original and 15 new parts')
    ids = [p['id'] for p in parts]
    require(len(set(ids)) == len(ids), 'Duplicate catalog IDs')
    require(ids == list(model.nodes), 'Catalog and GLB part order disagree')
    require(ids[175:] == NEW_IDS, 'Unexpected new IDs or order')
    require(model.g.get('scene', 0) == 0 and model.g['scenes'] == [{'nodes': list(range(len(parts)))}],
            'Output scene does not contain each part exactly once')
    require(model.g['nodes'][:175] == baseline.g['nodes'], 'Original GLB node metadata changed')
    require(parts[:175] == old_parts, 'Original catalog part metadata changed')
    require(catalog['orientation'] == base_catalog['orientation'], 'Display orientation changed')
    expected_transform = {'source': 'FBX world centimetres', 'center': CENTER.tolist(), 'scale': SCALE}
    require(catalog['orientation']['transform'] == expected_transform, 'Unexpected display transform')
    require(catalog['model']['bytes'] == len(model_raw), 'Catalog model size mismatch')
    require(catalog['model']['sha256'] == sha256(model_raw), 'Catalog model hash mismatch')
    manifest = json.loads((ROOT / 'refinamento/respiratorio/geometria/parts_manifest.json').read_text())
    audit = json.loads((ROOT / 'refinamento/respiratorio/geometria/mesh_audit.json').read_text())
    base_audit = json.loads(baseline_bytes('refinamento/respiratorio/geometria/mesh_audit.json'))
    require(manifest == parts and audit['parts'][:175] == base_audit['parts'],
            'Manifest or original audit metadata disagree')
    require([a['id'] for a in audit['parts']] == ids, 'Audit part order mismatch')
    require(audit['display_transform'] == catalog['orientation'], 'Audit display transform mismatch')
    for part in parts:
        associations = part['requirementIds'] + part.get('relatedRequirementIds', [])
        associations += [match['id'] for match in part.get('requirementMatches', [])]
        require(all(identifier in requirements for identifier in associations),
                f"{part['id']}: association references a nonexistent requirement")

    old_digest, old_array_bytes, old_array_count = hashlib.sha256(), 0, 0
    for part in old_parts:
        before, after = baseline.arrays(part['id']), model.arrays(part['id'])
        for key in ('POSITION', 'NORMAL', 'indices'):
            raw = before[key].tobytes()
            require(before[key].shape == after[key].shape and raw == after[key].tobytes(),
                    f"{part['id']}: original {key} array changed")
            old_digest.update(raw)
            old_array_bytes += len(raw)
            old_array_count += 1
    require(model.binary[:len(baseline.binary)] == baseline.binary,
            'Original BIN chunk is not preserved as an exact prefix')

    geometry_checks = []
    total_vertices = total_triangles = total_degenerates = 0
    max_normal_error = 0.
    for part, audit_part in zip(parts, audit['parts']):
        arrays = model.arrays(part['id'])
        vertices, normals = arrays['POSITION'], arrays['NORMAL']
        require(arrays['indices'].size % 3 == 0, f"{part['id']}: incomplete triangle")
        faces = arrays['indices'].reshape(-1, 3)
        require(vertices.shape == normals.shape and vertices.shape[1] == 3,
                f"{part['id']}: invalid normals or positions")
        require(np.isfinite(vertices).all() and np.isfinite(normals).all(),
                f"{part['id']}: non-finite geometry")
        require(int(faces.max()) < len(vertices), f"{part['id']}: index out of bounds")
        lengths = np.linalg.norm(normals.astype(np.float64), axis=1)
        normal_error = float(np.abs(lengths - 1.).max())
        require(normal_error <= 1e-6, f"{part['id']}: normals are not unit length")
        cross = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]],
                         vertices[faces[:, 2]] - vertices[faces[:, 0]])
        degenerates = int((np.linalg.norm(cross, axis=1) == 0).sum())
        require(degenerates == audit_part['degenerate_triangles'],
                f"{part['id']}: degeneracy audit mismatch")
        require(audit_part['finite'] is True and audit_part['indices_in_bounds'] is True
                and audit_part['source_triangles_preserved'] is True,
                f"{part['id']}: audit integrity flags mismatch")
        require(part['vertices'] == len(vertices) and part['triangles'] == len(faces),
                f"{part['id']}: catalog counts mismatch")
        require(part['bounds'] == [vertices.min(0).tolist(), vertices.max(0).tolist()],
                f"{part['id']}: catalog bounds mismatch")
        geometry_checks.append({'id': part['id'], 'finite': True, 'indices_in_bounds': True,
                                'unit_normal_max_abs_error': normal_error,
                                'degenerate_triangles': degenerates})
        total_vertices += len(vertices)
        total_triangles += len(faces)
        total_degenerates += degenerates
        max_normal_error = max(max_normal_error, normal_error)
    require(catalog['model']['parts'] == len(parts) and catalog['model']['triangles'] == total_triangles,
            'Catalog model totals mismatch')
    require(audit['source_triangle_count'] == total_triangles, 'Audit triangle total mismatch')

    readers = {name: SourceGLB(name) for name in sorted({item[1] for item in NEW_PARTS})}
    for name, reader in readers.items():
        source_names = [node['name'] for node in reader.g['nodes'] if 'mesh' in node]
        require(len(source_names) == len(set(source_names)), f'{name}: duplicate source mesh node names')
    source_geometry_checks = []
    for part, (name, source, group, expected_ids) in zip(parts[175:], NEW_PARTS):
        require(part['sourceName'] == name and part['sourceFile'] == source + '.fbx'
                and part['group'] == group, f'{name}: unexpected source or group')
        require(part['defaultVisible'] is False and part['quizEligible'] is False,
                f'{name}: new parts must stay hidden and out of the quiz')
        require(part['requirementIds'] == expected_ids, f'{name}: requirement associations changed')
        for requirement_id in expected_ids:
            require(requirement_id in requirements and name in requirements[requirement_id]['z_evidencia'],
                    f'{name}: association does not exist in the requirements')
            require(any(match['id'] == requirement_id and match['separateStructure'] is True
                        and match['match'] == 'source_name_candidate' for match in part['requirementMatches']),
                    f'{name}: direct nominal requirement match is missing')
        require(all(m['visualValidation'] == 'pending_individual' for m in part['requirementMatches']),
                f'{name}: match visual validation was promoted')
        reader = readers[source]
        world_vertices, source_faces, node_index = reader.geometry(name)
        expected_positions = ((world_vertices - CENTER) * SCALE).astype('<f4')
        expected_indices = source_faces.astype('<u4').reshape(-1, 1)
        arrays = model.arrays(part['id'])
        require(arrays['POSITION'].shape == expected_positions.shape
                and arrays['POSITION'].tobytes() == expected_positions.tobytes(),
                f'{name}: positions differ from the source under the common transform')
        require(arrays['indices'].shape == expected_indices.shape
                and arrays['indices'].tobytes() == expected_indices.tobytes(),
                f'{name}: triangle order or connectivity differs from the source')
        require(part['sourceNode'] == node_index, f'{name}: source node mismatch')
        part_index = 175 + len(source_geometry_checks)
        audit_part = audit['parts'][part_index]
        world_bounds = [world_vertices.min(0).tolist(), world_vertices.max(0).tolist()]
        require(audit_part['sourceFile'] == source + '.fbx' and audit_part['sourceNode'] == node_index
                and audit_part['sourceWorldBounds'] == world_bounds,
                f'{name}: source audit metadata mismatch')
        check = geometry_checks[part_index]
        require(check['degenerate_triangles'] == 0, f'{name}: degenerate triangles found')
        source_geometry_checks.append(dict(
            source_name=name, source_file=source + '.fbx', source_node=node_index,
            source_glb=reader.path.relative_to(ROOT).as_posix(),
            source_world_matrix=reader.world[node_index].tolist(),
            source_world_bounds=world_bounds,
            vertices=part['vertices'], triangles=part['triangles'],
            position_float32_bytes_exact=True, indices_uint32_bytes_exact=True,
            position_sha256=sha256(expected_positions.tobytes()),
            indices_sha256=sha256(expected_indices.tobytes()),
            normal_sha256=sha256(arrays['NORMAL'].tobytes()),
            default_visible=False, quiz_eligible=False, requirement_ids=expected_ids,
            requirement_matches_validation='pending_individual', **check))

    raw_source_checks = []
    for name, expected in NEW_FBX.items():
        relative_path = 'fontes/z_app/' + name + '.fbx'
        path = ROOT / relative_path
        raw = path.read_bytes()
        identity = dict(bytes=len(raw), sha256=sha256(raw),
                        git_blob=hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest())
        require(identity == expected, f'{name}: raw FBX differs from pinned official identity')
        url = f'https://raw.githubusercontent.com/LluisV/Z-Anatomy/{SOURCE_COMMIT}/Resources/Models/FBX/{name}.fbx'
        provenance = json.loads(path.with_suffix('.fbx.provenance.json').read_text())
        require(all(provenance[k] == value for k, value in identity.items())
                and provenance['url'] == url and provenance['commit'] == SOURCE_COMMIT
                and provenance['file'] == relative_path, f'{name}: source provenance mismatch')
        raw_source_checks.append(dict(file=relative_path, official_pinned_url=url,
                                      commit=SOURCE_COMMIT, pinned_identity_matches=True, **identity))

    # Connect each newly fetched raw FBX to its local converted input, without
    # replacing any source or atlas output. Compare selected geometry rather
    # than requiring converter metadata or buffer layout to be byte-identical.
    assimp = shutil.which('assimp')
    require(assimp is not None, 'Assimp is required for independent temporary FBX reconversion')
    assimp_version = subprocess.check_output([assimp, 'version'], text=True).strip()
    reconversion_checks = []
    with tempfile.TemporaryDirectory(prefix='atlas-mediastinal-verification-') as temporary:
        for name in NEW_FBX:
            converted = Path(temporary) / (name + '.glb')
            command = [assimp, 'export', str(ROOT / 'fontes/z_app' / (name + '.fbx')),
                       str(converted), '-fglb2']
            subprocess.run(command, check=True, capture_output=True, timeout=120)
            reader = SourceGLB(name, converted)
            converted_names = [node['name'] for node in reader.g['nodes'] if 'mesh' in node]
            require(len(converted_names) == len(set(converted_names)), f'{name}: duplicate reconverted mesh names')
            names = [part_name for part_name, source, _, _ in NEW_PARTS if source == name]
            for part_name in names:
                vertices, faces, _ = readers[name].geometry(part_name)
                fresh_vertices, fresh_faces, _ = reader.geometry(part_name)
                require(vertices.shape == fresh_vertices.shape and vertices.tobytes() == fresh_vertices.tobytes()
                        and faces.shape == fresh_faces.shape and faces.tobytes() == fresh_faces.tobytes(),
                        f'{part_name}: local source GLB differs from the independently reconverted pinned FBX')
            reconversion_checks.append(dict(
                source_file='fontes/z_app/' + name + '.fbx',
                command=[Path(assimp).name, 'export', 'fontes/z_app/' + name + '.fbx',
                         '<temporary>/' + name + '.glb', '-fglb2'],
                reconverted_glb_bytes=len(reader.raw), reconverted_glb_sha256=sha256(reader.raw),
                selected_source_world_positions_and_indices_byte_exact=True, compared_parts=names))

    return dict(
        report_version=1, passed=True, verifier_sha256=sha256(Path(__file__).read_bytes()),
        baseline=dict(commit=BASELINE, model_sha256=sha256(base_raw),
                      parts=175, triangles=base_catalog['model']['triangles'], bytes=len(base_raw)),
        model=dict(file='site/assets/respiratory/model.glb', sha256=sha256(model_raw),
                   parts=len(parts), vertices=total_vertices, triangles=total_triangles, bytes=len(model_raw)),
        display_transform=expected_transform,
        preservation=dict(parts=175, arrays=old_array_count, bytes=old_array_bytes,
                          position_normal_indices_byte_exact=True,
                          concatenated_array_sha256=old_digest.hexdigest(),
                          original_binary_prefix_byte_exact=True, original_metadata_unchanged=True),
        geometry=dict(finite_parts=len(parts), indices_in_bounds_parts=len(parts),
                      normalized_normal_parts=len(parts), normal_length_tolerance=1e-6,
                      maximum_normal_length_error=max_normal_error,
                      degenerate_triangles=total_degenerates, new_part_degenerate_triangles=0,
                      ids_unique=True, manifest_and_audit_match=True),
        requirements=dict(sha256=sha256(requirements_raw), unchanged_from_baseline=True,
                          status_and_visual_validation_unchanged=True,
                          new_associations_use_existing_ids=True),
        raw_source_identities=raw_source_checks,
        source_glb_identities=[dict(file=reader.path.relative_to(ROOT).as_posix(),
                                    bytes=len(reader.raw), sha256=sha256(reader.raw),
                                    generator=reader.g.get('asset', {}).get('generator'))
                               for reader in readers.values()],
        independent_fbx_reconversion=dict(assimp_version=assimp_version, sources=reconversion_checks),
        new_parts=source_geometry_checks,
        verified_claims=[
            'All 175 original POSITION, NORMAL and index arrays are byte-identical to the pinned baseline.',
            'All 15 new POSITION float32 and index uint32 arrays equal the on-disk converted source under one common transform.',
            'The two added raw FBX files match independently pinned official Git blob identities and SHA-256 hashes.',
            'The eight selected nerve and lymph-node source geometries equal independent temporary reconversions of the pinned raw FBX files.',
            'New parts remain hidden by default, outside the quiz, with existing nominal requirement associations and pending individual visual validation.',
        ],
        limits=[
            'Array equality proves preservation of converted source surfaces; it does not certify anatomical accuracy, completeness, nerve endings or lymphatic drainage.',
            'Temporary FBX reconversion compares the eight selected pieces from the two new sources using the installed Assimp version; it does not certify the converter against the authoring application or other exports.',
            'Finite unit normals and zero-area triangle checks do not certify manifoldness, absence of self-intersection or outward normal orientation.',
            'Nominal requirement associations do not complete contextual grooves, pulmonary plexuses, individual ganglia or individual lymph nodes.',
            'No online fetch, visual validation or classification promotion is performed.',
        ])


def main():
    try:
        report = verify()
    except Exception as error:
        # Always replace any previous passing report if a subsequent check or
        # input read fails. Unexpected errors also exit unsuccessfully.
        report = dict(report_version=1, passed=False,
                      error=f'{type(error).__name__}: {error}', baseline_commit=BASELINE)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'report': REPORT.relative_to(ROOT).as_posix(),
                      'model': report.get('model'), 'error': report.get('error')}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
