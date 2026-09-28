"""Numerically inspect the two independent exported anatomical assemblies."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'refinamento/geometria'))
from build_respiratory_assets import SourceGLB
from register_bp3d import validate

reports=[]
for system in ['respiratory','larynx']:
 directory=ROOT/'site/assets'/system
 catalog=json.loads((directory/'catalog.json').read_text())
 raw=(directory/'model.glb').read_bytes()
 assert len(raw)==catalog['model']['bytes']
 assert hashlib.sha256(raw).hexdigest()==catalog['model']['sha256']
 source=SourceGLB(system,directory/'model.glb')
 assert set(source.nodes)=={p['id'] for p in catalog['parts']}
 parts=[]
 for meta in catalog['parts']:
  v,f,node=source.geometry(meta['id'])
  assert np.isfinite(v).all() and f.min()>=0 and f.max()<len(v)
  assert len(v)==meta['vertices'] and len(f)==meta['triangles']
  assert np.allclose([v.min(0),v.max(0)],meta['bounds'],atol=1e-7)
  primitive=source.g['meshes'][source.g['nodes'][node]['mesh']]['primitives'][0]
  normals=source.accessor(primitive['attributes']['NORMAL'])
  assert np.isfinite(normals).all() and np.allclose(np.linalg.norm(normals,axis=1),1,atol=1e-6)
  # Exact-position welding is for analysis only. No output geometry is altered.
  unique,inverse=np.unique(v,axis=0,return_inverse=True)
  welded_faces=inverse[f]
  topology=validate(unique,welded_faces)
  exact_areas=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)
  parts.append({'id':meta['id'],'finite':True,'indices_valid':True,'bounds_match':True,'normals_unit':True,
                'triangles':len(f),'exact_zero_area_triangles':int((exact_areas==0).sum()),
                'topology_after_exact_position_weld':{
                 k:topology[k] for k in ['connected_components_by_vertex_index','component_vertex_counts','boundary_edges','nonmanifold_edges']}})
 reports.append({'system':system,'sha256':catalog['model']['sha256'],'parts':parts,
                 'note':'Topology can be open/disconnected in the author source, notably curve branches. No capping, deletion or deformation performed.'})
path=Path(__file__).with_name('asset_validation.json')
path.write_text(json.dumps(reports,ensure_ascii=False,indent=2))
for report in reports:
 print(json.dumps({'system':report['system'],'parts':len(report['parts']),
                   'triangles':sum(p['triangles'] for p in report['parts']),
                   'zero_area_faces':sum(p['exact_zero_area_triangles'] for p in report['parts']),
                   'parts_with_boundaries':sum(p['topology_after_exact_position_weld']['boundary_edges']>0 for p in report['parts']),
                   'parts_with_nonmanifold_edges':sum(p['topology_after_exact_position_weld']['nonmanifold_edges']>0 for p in report['parts'])}))
print(path)
