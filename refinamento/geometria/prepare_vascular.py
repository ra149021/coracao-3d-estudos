"""Prepare an exclusive BP3D coronary network; do not overlay duplicates."""
from pathlib import Path
import json
import struct
import hashlib
import numpy as np
from scipy.spatial import cKDTree
from register_bp3d import ROOT,OUT,read_obj,apply,to_site,validate

CONCEPTS=json.loads((ROOT/'malhas/bp3d_inventory.json').read_text())['concepts']
GROUPS=[
 ('FMA3802','81','Coronária direita · tronco','coronarias'),
 ('FMA3855','83','Coronária esquerda · tronco','coronarias'),
 ('FMA3807','96','Ramo do cone arterial direito','coronarias'),
 ('FMA3815','97','Ramos ventriculares anteriores direitos · não marginais','coronarias'),
 ('FMA3818','98','Ramo marginal direito','coronarias'),
 ('FMA3840','100','Ramo interventricular posterior','coronarias'),
 ('FMA3845','101','Ramos septais do interventricular posterior','coronarias'),
 ('FMA3835','102','Ramos ventriculares posteriores direitos','coronarias'),
 ('FMA74912','103','Ramo interventricular anterior · tronco','coronarias'),
 ('FMA3868','103a','Ramo do cone do interventricular anterior','coronarias'),
 ('FMA3892','103b','Ramos septais do interventricular anterior','coronarias'),
 ('FMA3860','103c','Ramo lateral (diagonal) do interventricular anterior','coronarias'),
 ('FMA3895','104','Ramo circunflexo · conjunto da fonte','coronarias'),
 ('FMA3870','','Ramos anteriores direitos do interventricular anterior','coronarias'),
 ('FMA4706','30k','Seio coronário','veias'),
 ('FMA66403','105','Veia interventricular anterior','veias'),
 ('FMA4707','106','Veia cardíaca magna · segmento da fonte','veias'),
 ('FMA4708','109','Veia marginal esquerda','veias'),
 ('FMA4712','110','Veias posteriores do ventrículo esquerdo','veias'),
 ('FMA4713','111','Veia interventricular posterior (cardíaca média)','veias'),
 ('FMA4716','112','Veia marginal direita','veias'),
 ('FMA4714','113','Veia cardíaca parva','veias'),
 ('FMA76767','114','Veias anteriores do ventrículo direito','veias'),
]
Z_NAMES=[
 'Right coronary artery','Right inferolateral branch of right coronary artery',
 'Left coronary artery','Anterior interventricular artery','Circumflex artery of heart',
 'Septal branches of anterior interventricular artery','Coronary sinus',
 'Great cardiac vein','Middle cardiac vein',"Inferior vein of left ventricle (//Posterior '')",
]


def glb_source():
    raw=(ROOT/'malhas/CardioVascular41.glb').read_bytes()
    n,typ=struct.unpack_from('<II',raw,12);assert typ==0x4e4f534a
    g=json.loads(raw[20:20+n]);size,typ=struct.unpack_from('<II',raw,20+n);assert typ==0x004e4942
    binary=raw[28+n:28+n+size];world={}
    def walk(ix,parent):
        node=g['nodes'][ix];assert not any(k in node for k in ['translation','rotation','scale'])
        world[ix]=parent@np.array(node.get('matrix',np.eye(4).flatten())).reshape(4,4).T
        for child in node.get('children',[]):walk(child,world[ix])
    for node in g['scenes'][g.get('scene',0)]['nodes']:walk(node,np.eye(4))
    def access(ix):
        a=g['accessors'][ix];assert not a.get('sparse');v=g['bufferViews'][a['bufferView']]
        dim={'SCALAR':1,'VEC3':3}[a['type']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']])
        return np.ndarray((a['count'],dim),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dim*dt.itemsize),dt.itemsize)).copy()
    out={}
    for ix,node in enumerate(g['nodes']):
        name=node.get('name')
        if name not in Z_NAMES or 'mesh' not in node:continue
        vs,fs,off=[],[],0
        for p in g['meshes'][node['mesh']]['primitives']:
            v=access(p['attributes']['POSITION']);v=v@world[ix][:3,:3].T+world[ix][:3,3]
            # Original GLB units are cm and (x, z, -y) axes.
            v=v[:,[0,2,1]]*[10,-10,10]
            f=access(p['indices']).reshape(-1,3).astype(np.uint32)
            if np.linalg.det(world[ix][:3,:3])<0:f=f[:,[0,2,1]]
            vs.append(v);fs.append(f+off);off+=len(v)
        out[name]=(np.concatenate(vs),np.concatenate(fs))
    assert len(out)==len(Z_NAMES)
    return out


def main():
    registration=json.loads((OUT/'registration.json').read_text())
    transform=registration['scale'],np.array(registration['rotation']),np.array(registration['translation_mm'])
    z=glb_source();trees={name:cKDTree(v) for name,(v,f) in z.items()}
    seen={};parts=[];(OUT/'vascular').mkdir(exist_ok=True)
    for fma,req,label,group in GROUPS:
        ids=CONCEPTS[fma]['available_elements'];vs,fs,off=[],[],0;original=[]
        for fj in ids:
            assert fj not in seen,(fj,seen.get(fj),fma)
            seen[fj]=fma
            v,f=read_obj(fj);vs.append(v);fs.append(f+off);off+=len(v)
            original.append({'element':fj,'sha256':hashlib.sha256((ROOT/'fontes/bp3d/objetos_coracao'/(fj+'.obj')).read_bytes()).hexdigest()})
        v=np.concatenate(vs);f=np.concatenate(fs);v,ix=np.unique(v,axis=0,return_inverse=True);f=ix[f].astype(np.uint32)
        reg=apply(v,transform);site=to_site(reg)
        path=OUT/'vascular'/(fma+'.npz');np.savez_compressed(path,vertices=site,faces=f,z_world_mm=reg)
        distances=np.array([tree.query(reg)[0] for tree in trees.values()]);which=distances.argmin(0);d=distances.min(0)
        near={name:float(np.mean((which==i)&(d<1))) for i,name in enumerate(trees)}
        nearest=sorted(near.items(),key=lambda x:x[1],reverse=True)[:3]
        parts.append(dict(fma=fma,id='bp_'+fma,sourceName=CONCEPTS[fma]['name'],label=label,group=group,requirementId=req,elements=ids,
            file=str(path.relative_to(OUT)),source='BodyParts3D 4.0',license='CC BY 4.0',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            source_meshes=original,validation=validate(v,f),site_bounds=[site.min(0).tolist(),site.max(0).tolist()],
            overlap_with_existing_Z={'warning':'Nearest vertices approximate proximity only. Distances do not prove identity; pipeline does not automatically subtract or fuse surfaces.',
              'fraction_bp_vertices_within_1mm_of_any_Z_vessel':float(np.mean(d<1)),
              'fraction_bp_vertices_within_2mm_of_any_Z_vessel':float(np.mean(d<2)),
              'median_nearest_vertex_mm':float(np.median(d)),
              'p95_nearest_vertex_mm':float(np.quantile(d,.95)),
              'closest_z_objects_fraction_within_1mm':nearest},
            anatomical_validation='Do not count all branch labels as visually validated. Inspect render and vessel term maps before integrating.'))
    report={
        'strategy':'Recommended as an alternate exclusive BP3D coronary/venous layer replacing all 10 current Z coronary and cardiac-vein objects. Never draw both networks simultaneously.',
        'replace_Z_names':Z_NAMES,'parts':parts,'unique_source_element_count':len(seen),'duplicate_elements':0,
        'registration':'Same common similarity from registration.json; not fitted separately to vessel network.',
        'term_notes':[
            'FMA3813 includes FMA3815 plus FMA3818. This export separates nonmarginal anterior branches (FMA3815) and right marginal branch (FMA3818); together they address the broader item 97. Never export FMA3813 again on top.',
            'Source FMA4707 represents FJ2656; its anterior interventricular continuation is exported separately as FMA66403. The complete great cardiac vein in conventional naming encompasses these connected segments; do not teach them as unrelated veins.',
            'FMA3895 remains the source circumflex aggregate. Marginal/posterior/atrial branches are not individually validated by this export.',
            'Right posterior ventricular branches (FMA3835) are not yet individually matched to the exact posterolateral term in the lecturer script.',
            'Vascular anatomy varies. This is the source atlas pattern, not a claim of one invariant arterial dominance or drainage pattern.',
        ],
        'unfilled_targets':['sinoatrial nodal branch','atrioventricular nodal branch','individually identified atrial branches','oblique vein of left atrium','pericardiacophrenic vessels'],
    }
    (OUT/'vascular.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'parts':len(parts),'elements':len(seen),'triangles':sum(p['validation']['triangles'] for p in parts),'summary':[{k:p[k] for k in ['fma','label','overlap_with_existing_Z']} for p in parts]},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
