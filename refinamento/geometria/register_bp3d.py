"""Register preexisting BodyParts3D surfaces to the Z-Anatomy heart.

All fitting is one common similarity transform, with a positive scale and a
proper rotation. No per-part warp, hand placement or anatomical synthesis.
Run with the prepared codex-tools Python (numpy, scipy, matplotlib).
"""
from pathlib import Path
import json
import hashlib
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
COMMON = [
    ('FJ2433', 'Inferior leaflet of right atrioventricular valve'),
    ('FJ2436', 'Septal leaflet of right atrioventricular valve'),
    ('FJ2432', 'Posterior leaflet of left atrioventricular valve'),
    ('FJ2419', 'Anterior papillary muscle of right ventricle'),
    ('FJ2430', 'Inferior papillary muscle of right ventricle'),
    ('FJ2437', 'Septal papillary muscle of right ventricle'),
    ('FJ2429', 'Inferior papillary muscle of left ventricle'),
]
NEW = [
    ('FJ2421', 'FMA7238', 'anterior leaflet of tricuspid valve', 'Tricúspide · cúspide anterior', '46a'),
    ('FJ2420', 'FMA7242', 'anterior leaflet of mitral valve', 'Mitral · cúspide anterior', '58a'),
    ('FJ2418', 'FMA7265', 'anterolateral head of lateral papillary muscle of left ventricle', 'VE · cabeça anterolateral de músculo papilar (porção)', '59'),
]


def read_obj(fj):
    path = ROOT / 'fontes/bp3d/objetos_coracao' / (fj + '.obj')
    vertices, faces = [], []
    for line in path.read_text().splitlines():
        s = line.split()
        if s and s[0] == 'v':
            vertices.append(list(map(float, s[1:4])))
        if s and s[0] == 'f':
            ids = [int(x.split('/')[0]) - 1 for x in s[1:]]
            for k in range(1, len(ids) - 1):
                faces.append([ids[0], ids[k], ids[k+1]])
    v, f = np.array(vertices, dtype=float), np.array(faces, dtype=np.uint32)
    assert np.isfinite(v).all() and len(f) and f.max() < len(v)
    return v, f


manifest = {m['name']: m for m in json.loads((ROOT / 'malhas/heart_source/manifest.json').read_text())}


def z_mesh(name):
    data = np.load(ROOT / 'malhas/heart_source' / manifest[name]['file'], allow_pickle=False)
    return data['vertices'].astype(float) * 1000, data['faces']


def fit(source, target):
    """Least-squares similarity, column-vector convention q = s R p + t."""
    c1, c2 = source.mean(0), target.mean(0)
    a, b = source - c1, target - c2
    u, sig, vt = np.linalg.svd(b.T @ a)
    d = np.diag([1, 1, np.linalg.det(u @ vt)])
    rot = u @ d @ vt
    scale = np.trace(np.diag(sig) @ d) / np.sum(a*a)
    trans = c2 - scale * rot @ c1
    assert scale > 0 and abs(np.linalg.det(rot)-1) < 1e-6
    return scale, rot, trans


def apply(v, transform):
    s, r, t = transform
    return s * v @ r.T + t


def registration(pairs, rounds=100):
    # A bounding-box centre is less biased by differing local mesh density.
    centers = lambda vs: np.array([(v.min(0)+v.max(0))/2 for v in vs])
    transform = fit(centers([p[0] for p in pairs]), centers([p[1] for p in pairs]))
    trees = [cKDTree(p[1]) for p in pairs]
    previous = float('inf')
    for _ in range(rounds):
        src, dst = [], []
        for (a, b), tree in zip(pairs, trees):
            # Deterministic equal per-structure samples avoid one dense leaflet
            # dominating the smaller papillary structures.
            q = a[np.linspace(0, len(a)-1, min(500, len(a)), dtype=int)]
            dist, ix = tree.query(apply(q, transform))
            src.append(q)
            dst.append(b[ix])
        a, b = np.concatenate(src), np.concatenate(dst)
        transform = fit(a, b)
        rms = float(np.sqrt(np.mean(np.sum((apply(a, transform)-b)**2, axis=1))))
        if abs(previous-rms) < 1e-10:
            break
        previous = rms
    return transform


def metrics(a, b):
    # Conservative vertex-to-vertex distances; not true closest surface error.
    d = np.concatenate([cKDTree(a).query(b)[0], cKDTree(b).query(a)[0]])
    return {
        'symmetric_nearest_vertex_rms_mm': float(np.sqrt(np.mean(d*d))),
        'symmetric_nearest_vertex_median_mm': float(np.median(d)),
        'symmetric_nearest_vertex_p95_mm': float(np.quantile(d, .95)),
        'symmetric_nearest_vertex_max_mm': float(d.max()),
        'bbox_max_difference_mm': float(np.max(np.abs(np.array([a.min(0), a.max(0)]) - np.array([b.min(0), b.max(0)])))),
    }


def validate(v, f):
    edges = np.concatenate([f[:, [0,1]], f[:, [1,2]], f[:, [2,0]]])
    graph = coo_matrix((np.ones(len(edges)), (edges[:,0], edges[:,1])), shape=(len(v),len(v))).tocsr()
    n, labs = connected_components(graph, directed=False)
    areas = np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)/2
    sorted_edges = np.sort(edges,axis=1)
    _, counts = np.unique(sorted_edges, axis=0, return_counts=True)
    return {
        'finite': bool(np.isfinite(v).all()), 'vertices': len(v), 'triangles': len(f),
        'connected_components_by_vertex_index': n,
        'component_vertex_counts': sorted(np.bincount(labs).tolist(), reverse=True),
        'boundary_edges': int(np.count_nonzero(counts==1)),
        'nonmanifold_edges': int(np.count_nonzero(counts>2)),
        'zero_area_triangles': int(np.count_nonzero(areas < 1e-10)),
        'surface_area_mm2': float(areas.sum()),
        'source_bounds_mm': [v.min(0).tolist(),v.max(0).tolist()],
    }


def to_site(v):
    # Registered vertices are Z-Anatomy Blender world expressed in mm.
    return ((v[:,[0,2,1]] * [.1,.1,-.1] - [2,130.5,2])*.25).astype('<f4')


def main():
    pairs = [(read_obj(fj)[0], z_mesh(name)[0]) for fj,name in COMMON]
    transform = registration(pairs)
    common_report = []
    for i, ((fj,name),(a,b)) in enumerate(zip(COMMON,pairs)):
        leave_out = registration(pairs[:i]+pairs[i+1:])
        common_report.append({
            'bp3d_element': fj, 'z_anatomy_name': name,
            'joint_fit': metrics(apply(a,transform),b),
            'held_out_fit': metrics(apply(a,leave_out),b),
        })
    (OUT/'meshes').mkdir(exist_ok=True)
    parts = []
    for fj,fma,name,label,req in NEW:
        v,f = read_obj(fj)
        original_validation = validate(v,f)
        # OBJ repeats positions at material/normal seams. Exact deduplication
        # changes only indexing, not a single geometric position or triangle.
        v,index = np.unique(v,axis=0,return_inverse=True)
        f=index[f].astype(np.uint32)
        reg = apply(v,transform)
        site = to_site(reg)
        assert np.isfinite(site).all() and np.abs(site).max()<10
        path = OUT/'meshes'/(fj+'.npz')
        np.savez_compressed(path,vertices=site,faces=f,z_world_mm=reg)
        d = dict(element=fj,fma=fma,sourceName=name,label=label,requirementId=req,
                 source='BodyParts3D 4.0',license='CC BY 4.0',file=str(path.relative_to(OUT)),
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 source_obj_sha256=hashlib.sha256((ROOT/'fontes/bp3d/objetos_coracao'/(fj+'.obj')).read_bytes()).hexdigest(),
                 validation=validate(v,f),original_obj_validation=original_validation,
                 processing='Single global similarity; exact position deduplication for OBJ seams; preserved triangles; no smoothing, remeshing, capping, local deformation or generated anatomy.',
                 site_bounds=[site.min(0).tolist(),site.max(0).tolist()],
                 integration_recommendation='integrate as named leaflet plus incorporated chordae' if fj!='FJ2418' else 'integrate only as named papillary portion, never full muscle group',
                 anatomical_validation='Six-view visual relationship inspection completed; leaflet/chordae align with existing valve/papillary assembly. Individual chord insertions, tissue mechanics and anatomical completeness are not independently validated.')
        parts.append(d)
    s,r,t = transform
    matrix = np.eye(4); matrix[:3,:3]=s*r;matrix[:3,3]=t
    result = {
        'method':'Single similarity transform fit to 7 homologous preexisting meshes; labelled ICP with equal-per-structure samples, proper rotation, uniform scale. No local warps.',
        'distance_warning':'Distances compare sampled vertices, not closest points on triangles. No physical precision claim: source atlas is an idealized anatomical model.',
        'input_units':'BodyParts3D OBJ millimetres; Z-Anatomy world metres converted to mm',
        'scale':s,'rotation':r.tolist(),'translation_mm':t.tolist(),'matrix_bp_mm_to_z_world_mm':matrix.tolist(),
        'common_meshes':common_report,'candidate_parts':parts,
        'visual_evidence':'registro_inspecao.png',
        'scope_limit':'Registration confidence is not proof that the idealized source mesh reproduces every real anatomical detail. FJ2418 is only the source-named anterolateral head/portion; 2 closed connected components are preserved.',
        'sources':[
            {'url':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html','kind':'official download and concept mapping'},
            {'url':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html','kind':'CC BY 4.0 and attribution'},
            {'url':'https://github.com/Z-Anatomy/Models-of-human-anatomy','revision':'7cc49aa8749632adcd564c0e75f096dc43f6a4b8'},
        ],
    }
    (OUT/'registration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'scale':s,'translation':t.tolist(),'common_meshes':common_report,'parts':parts},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
