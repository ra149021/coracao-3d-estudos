"""Fit one common similarity from homologous laryngeal cartilages.

No deformation or independent fitting of new parts. Prepared meshes are source
surfaces, not procedurally modeled substitutes. Registration does not certify
individual tissue insertions or anatomical completeness.
"""
from pathlib import Path
import sys
import json
import hashlib
import zipfile
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'refinamento/geometria'))
from build_respiratory_assets import SourceGLB, CENTER, SCALE
from register_bp3d import registration, apply, metrics, validate

COMMON = [
    ('FJ2808', 'Thyroid cartilage'), ('FJ2769', 'Cricoid cartilage'),
    ('FJ2775', 'Arytenoid cartilage.l'), ('FJ2792', 'Arytenoid cartilage.r'),
    ('FJ2776', 'Corniculate cartilage.l'), ('FJ2793', 'Corniculate cartilage.r'),
    ('FJ2770', 'Epiglottis'),
]
NEW = [
    ('FJ2773', 'FMA55118', 'left cuneiform cartilage', 'Cartilagem cuneiforme · lado esquerdo', 'laringe'),
    ('FJ2795', 'FMA55117', 'right cuneiform cartilage', 'Cartilagem cuneiforme · lado direito', 'laringe'),
    ('FJ2788', 'FMA46593', 'left vocalis', 'Músculo vocal · lado esquerdo', 'musculos_laringe'),
    ('FJ2806', 'FMA46592', 'right vocalis', 'Músculo vocal · lado direito', 'musculos_laringe'),
    ('FJ2787', 'FMA55246', 'left vocal ligament', 'Ligamento vocal · lado esquerdo', 'ligamentos_laringe'),
    ('FJ2805', 'FMA55245', 'right vocal ligament', 'Ligamento vocal · lado direito', 'ligamentos_laringe'),
    ('FJ2777', 'FMA55252', 'left conus elasticus', 'Cone elástico · lado esquerdo', 'ligamentos_laringe'),
    ('FJ2794', 'FMA55251', 'right conus elasticus', 'Cone elástico · lado direito', 'ligamentos_laringe'),
    ('FJ2771', 'FMA55227', 'hyo-epiglottic ligament', 'Ligamento hioepiglótico', 'ligamentos_laringe'),
    ('FJ2807', 'FMA55230', 'thyro-epiglottic ligament', 'Ligamento tireoepiglótico', 'ligamentos_laringe'),
    ('FJ2780', 'FMA46585', 'left oblique arytenoid', 'Músculo aritenóideo oblíquo · lado esquerdo', 'musculos_laringe'),
    ('FJ2798', 'FMA46584', 'right oblique arytenoid', 'Músculo aritenóideo oblíquo · lado direito', 'musculos_laringe'),
]


def main():
    archive = zipfile.ZipFile(ROOT / 'fontes/bp3d/isa_BP3D_4.0_obj_99.zip')
    entries = {Path(name).stem: name for name in archive.namelist() if name.endswith('.obj')}
    cache = {}

    def read(fj):
        if fj in cache: return cache[fj]
        raw = archive.read(entries[fj])
        vertices, faces = [], []
        for line in raw.decode().splitlines():
            fields = line.split()
            if fields and fields[0] == 'v': vertices.append([float(x) for x in fields[1:4]])
            elif fields and fields[0] == 'f':
                ids = [int(x.split('/')[0])-1 for x in fields[1:]]
                for i in range(1, len(ids)-1): faces.append([ids[0], ids[i], ids[i+1]])
        vertices, inverse = np.unique(np.array(vertices), axis=0, return_inverse=True)
        faces = inverse[np.array(faces)].astype('<u4')
        assert np.isfinite(vertices).all() and faces.max() < len(vertices)
        cache[fj] = vertices, faces, hashlib.sha256(raw).hexdigest()
        return cache[fj]

    skeleton = SourceGLB('SkeletalSystem100')
    visceral = SourceGLB('VisceralSystem100')
    pairs = [(read(fj)[0], (visceral if name=='Epiglottis' else skeleton).geometry(name)[0] * 10) for fj, name in COMMON]
    transform = registration(pairs, rounds=180)
    comparison = []
    for i, ((fj, name), (a, b)) in enumerate(zip(COMMON, pairs)):
        held = registration(pairs[:i]+pairs[i+1:], rounds=180)
        comparison.append(dict(element=fj, sourceName=name, joint_fit=metrics(apply(a, transform), b), held_out=metrics(apply(a, held), b)))
    parts = []
    directory = OUT / 'bp3d_meshes'
    directory.mkdir(exist_ok=True)
    for fj, fma, name, label, group in NEW:
        vertices, faces, source_hash = read(fj)
        registered_mm = apply(vertices, transform)
        display = ((registered_mm / 10 - CENTER) * SCALE).astype('<f4')
        path = directory / (fj + '.npz')
        np.savez_compressed(path, vertices=display, faces=faces, source_vertices=vertices, world_fbx_mm=registered_mm)
        parts.append(dict(element=fj, fma=fma, sourceName=name, label=label, group=group,
                          source='BodyParts3D 4.0', license='CC BY 4.0', sourceFile=entries[fj],
                          source_obj_sha256=source_hash, file=str(path.relative_to(OUT)),
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          validation=validate(vertices, faces), bounds=[display.min(0).tolist(),display.max(0).tolist()],
                          integration_status='not_for_fusion_with_z_anatomy'))
    scale, rotation, translation = transform
    matrix = np.eye(4); matrix[:3,:3]=scale*rotation;matrix[:3,3]=translation
    report = dict(method='One common proper similarity, labelled ICP on 7 homologous original laryngeal cartilages; no per-part fit or warp.',
                  target_units='FBX world millimetres', scale=scale, rotation=rotation.tolist(), translation_mm=translation.tolist(),
                  matrix_bp_mm_to_fbx_world_mm=matrix.tolist(), common_meshes=comparison, parts=parts,
                  warning='Conservative nearest-vertex distances, not exact surface error. No clinical accuracy claim.',
                  decision='Rejected for fine-tissue fusion. Use the independent original-coordinate BodyParts3D larynx assembly instead.',
                  source_duplicate_excluded='FJ2440 and FJ2769 have identical cricoid vertex positions; only FJ2769 used.',
                  sources=[{'url':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html'},
                           {'url':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html'}])
    (OUT / 'larynx_registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'scale':scale,'common_meshes':comparison,'parts':len(parts)},indent=2))


if __name__ == '__main__': main()
