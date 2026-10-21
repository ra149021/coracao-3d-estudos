#!/usr/bin/env python3
"""Read-only GLB validation/inventory; stdlib only. Does NOT validate anatomy.

python scripts/audit_3d_models.py --recovery /path/to/recovered/site --output docs/qa/3d/inventory.json
The recovery directory is read only. No topology or coordinates are rewritten.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def audit(path, site):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data)
    assert magic == b'glTF' and version == 2 and length == len(data), f'GLB header: {path}'
    offset, document, binary = 12, None, None
    while offset < length:
        size, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        assert size % 4 == 0 and offset + size <= length, f'Chunk length: {path}'
        chunk = data[offset:offset + size]
        if kind == 0x4E4F534A:
            document = json.loads(chunk)
        elif kind == 0x004E4942:
            binary = chunk
        offset += size
    assert document and binary is not None and offset == length
    assert len(document['buffers']) == 1 and document['buffers'][0]['byteLength'] <= len(binary)

    def values(index):
        accessor = document['accessors'][index]
        assert 'sparse' not in accessor, 'Sparse accessor not supported by this audit'
        view = document['bufferViews'][accessor['bufferView']]
        assert view.get('buffer', 0) == 0
        code, component_size = COMPONENTS[accessor['componentType']]
        width = WIDTHS[accessor['type']]
        size = width * component_size
        stride = view.get('byteStride', size)
        begin = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        end = begin + (accessor['count'] - 1) * stride + size
        assert stride >= size and end <= view.get('byteOffset', 0) + view['byteLength'] <= len(binary)
        fmt = '<' + code * width
        if stride == size:
            return list(struct.iter_unpack(fmt, memoryview(binary)[begin:end]))
        return [struct.unpack_from(fmt, binary, begin + i * stride) for i in range(accessor['count'])]

    records, vertex_count, triangle_count = [], 0, 0
    for mesh in document['meshes']:
        mesh_vertices, mesh_triangles = 0, 0
        bounds_min, bounds_max = [math.inf] * 3, [-math.inf] * 3
        for primitive in mesh['primitives']:
            assert primitive.get('mode', 4) == 4, 'Only triangle primitives are supported'
            positions = values(primitive['attributes']['POSITION'])
            assert positions and all(len(p) == 3 and all(math.isfinite(v) for v in p) for p in positions)
            for axis in range(3):
                bounds_min[axis] = min(bounds_min[axis], min(p[axis] for p in positions))
                bounds_max[axis] = max(bounds_max[axis], max(p[axis] for p in positions))
            indices = [v[0] for v in values(primitive['indices'])] if 'indices' in primitive else list(range(len(positions)))
            assert len(indices) % 3 == 0 and min(indices) >= 0 and max(indices) < len(positions), f'Invalid indices: {path}'
            if 'NORMAL' in primitive['attributes']:
                normals = values(primitive['attributes']['NORMAL'])
                assert len(normals) == len(positions) and all(all(math.isfinite(v) for v in n) for n in normals)
            mesh_vertices += len(positions)
            mesh_triangles += len(indices) // 3
        records.append({'name': mesh.get('name'), 'vertices': mesh_vertices, 'triangles': mesh_triangles,
                        'local_bounds': [bounds_min, bounds_max]})
        vertex_count += mesh_vertices
        triangle_count += mesh_triangles
    nodes = [n for n in document.get('nodes', []) if 'mesh' in n]
    ids = [n.get('extras', {}).get('partId', n.get('name')) for n in nodes]
    catalog_path = path.with_name('catalog.json')
    if path.parent.name == 'respiratory-context':
        catalog_path = path.with_name('parts.json')
    catalog_matches = True
    if catalog_path.is_file():
        parts = json.loads(catalog_path.read_text())['parts']
        catalog_matches = len(ids) == len(parts) and set(ids) == {p['id'] for p in parts}
        assert catalog_matches, f'Catalog/node identity mismatch: {path}'
        for node in nodes:
            part = next(p for p in parts if p['id'] == node.get('extras', {}).get('partId', node.get('name')))
            record = records[node['mesh']]
            assert part['vertices'] == record['vertices'] and part['triangles'] == record['triangles'], f'Catalog metrics: {part["id"]}'
    result = {'path': str(path.relative_to(site)), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'meshes': len(records), 'mesh_nodes': len(nodes), 'vertices': vertex_count, 'triangles': triangle_count,
              'finite': True, 'indices_in_bounds': True, 'catalog_names_match': catalog_matches,
              'segmentation_catalog': str(catalog_path.relative_to(site)) if catalog_path.is_file() else None,
              'mesh_metrics': records}
    if path.parent.name == 'heart-ct':
        provenance = json.loads(path.with_name('provenance.json').read_text())
        assert result['sha256'] == provenance['sha256'] and result['bytes'] == provenance['bytes']
    if path.parent.name == 'lung-ct':
        provenance = json.loads(path.with_name('audit.json').read_text())['export']
        assert result['sha256'] == provenance['sha256'] and result['triangles'] == provenance['triangles']
    if path.parent.name == 'respiratory-context':
        provenance = json.loads(path.with_name('provenance.json').read_text())
        assert result['sha256'] == provenance['output_sha256'] and result['bytes'] == provenance['output_bytes']
        assert provenance['shared_meshes_byte_identical'] == 175
        result['shared_source_meshes_byte_identical_at_extraction'] = 175
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recovery', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    site = ROOT / 'site'
    report = {'scope': 'Structural GLB validation only; no anatomical certification.',
              'models': [audit(path, site) for path in sorted((site / 'assets').rglob('*.glb'))]}
    if args.recovery:
        recovered = [audit(path, args.recovery) for path in sorted((args.recovery / 'assets').rglob('*.glb'))]
        local = {m['path']: m for m in report['models']}
        report['recovery_comparison'] = [{**m, 'same_as_local': m['sha256'] == local.get(m['path'], {}).get('sha256')} for m in recovered]
        report['recovered_viewer_same_as_local'] = (args.recovery / 'real-model-viewer.js').read_bytes() == (site / 'real-model-viewer.js').read_bytes()
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + '\n')
    else:
        print(text)

if __name__ == '__main__':
    main()
