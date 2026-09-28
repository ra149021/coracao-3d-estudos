"""Make a LOCAL reference GLB of 4 author-supplied teaching cuts.

There is no identified public redistribution license. Output stays under
referencias_locais/. Do not merge this specimen with the BodyParts3D atlas.
"""
from pathlib import Path
import json
import struct
import hashlib
import numpy as np

OUT=Path(__file__).resolve().parent/'referencias_locais'
report=json.loads((OUT/'UMN_MC_VALVES_inspecao.json').read_text())
meshes=[(p,dict(np.load(OUT/p['file'],allow_pickle=False))) for p in report['parts']]
bounds=np.array([d['vertices'].min(0) for p,d in meshes]+[d['vertices'].max(0) for p,d in meshes])
center=(bounds.min(0)+bounds.max(0))/2
g={'asset':{'version':'2.0','generator':'Local conversion of author-supplied UMN STL teaching cuts; no anatomical synthesis',
            'copyright':'University of Minnesota / Visible Heart Laboratories. LOCAL academic reference. Redistribution permission not established.'},
   'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[],
   'materials':[{'name':'Neutral study surface','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.69,.42,.37,1],'metallicFactor':0,'roughnessFactor':.8}}]}
binary=bytearray()


def add(arr,kind,component,target):
    while len(binary)%4:binary.append(0)
    start=len(binary);binary.extend(arr.tobytes());view=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':arr.nbytes,'target':target})
    ix=len(g['accessors']);a={'bufferView':view,'componentType':component,'count':len(arr),'type':kind}
    if kind=='VEC3':a.update(min=arr.min(0).tolist(),max=arr.max(0).tolist())
    g['accessors'].append(a);return ix


catalog=[]
for i,(part,d) in enumerate(meshes):
    original=d['vertices'];f=d['faces'].astype('<u4')
    v=((original-center)[:,[0,2,1]]*[.025,.025,-.025]).astype('<f4')
    tri=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    normals=np.zeros_like(v)
    for k in range(3):np.add.at(normals,f[:,k],tri)
    # Oppositely oriented incident faces can cancel at a source vertex. Use
    # its largest incident face for lighting; never change positions/faces.
    cancelled=np.flatnonzero(np.linalg.norm(normals,axis=1)<1e-12)
    for vertex_index in cancelled:
        incident=np.flatnonzero(np.any(f==vertex_index,axis=1))
        largest=incident[np.argmax(np.linalg.norm(tri[incident],axis=1))]
        normals[vertex_index]=tri[largest]
    normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
    assert np.isfinite(v).all() and np.isfinite(normals).all()
    assert np.allclose(np.linalg.norm(normals,axis=1),1,atol=1e-6)
    pos=add(v,'VEC3',5126,34962);norm=add(normals.astype('<f4'),'VEC3',5126,34962);ind=add(f.flatten(),'SCALAR',5125,34963)
    ident='umn_cut_'+str(i+1)
    g['scenes'][0]['nodes'].append(i);g['nodes'].append({'name':ident,'mesh':i,'extras':{'partId':ident,'sourceName':part['source_label']}})
    g['meshes'].append({'name':part['source_label'],'primitives':[{'attributes':{'POSITION':pos,'NORMAL':norm},'indices':ind,'material':0,'mode':4}]})
    catalog.append({'id':ident,'label':'Corte institucional '+str(i+1),'sourceName':part['source_label'],'sourceEntry':part['source_entry'],
        'vertices':len(v),'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()],
        'lighting_normals_fallback_vertices':len(cancelled),
        'anatomical_structure':'not assigned; object is an original teaching cut, not a segmented single structure'})
g['buffers']=[{'byteLength':len(binary)}]
encoded=json.dumps(g,ensure_ascii=False,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
blob=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
(OUT/'umn_reference.glb').write_bytes(blob)
(OUT/'umn_reference_catalog.json').write_text(json.dumps({'parts':catalog,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),
    'sourcePage':report['source_page'],'license':'LOCAL academic reference; public redistribution not cleared',
    'orientation':'Source coordinate axes kept with common Z-up to Y-up display rotation and uniform scaling. Anatomical axis labels NOT established.',
    'display_transform':{'center_source_units':center.tolist(),'scale':.025,'axis_map':'[x,z,-y]'},
    'relationships':'Original 4 STL coordinate relationships preserved. Do not register, overlay, or deform into the BP3D heart.',
    'validation':'All source coordinates finite; source ZIP CRC and SHA256 verified; 3 smaller cuts visually inspected. No individual anatomical label validation.',
    'limitations':['Source donor and scan parameters for this particular ZIP were not established.','Several objects are sections of the same heart; anatomical structures are not separate selectable objects.','STL has no tissue color/texture. Uniform color is illustrative.','Not counted towards integrated BP3D structure coverage.']},ensure_ascii=False,indent=2))
print(json.dumps({'output':str(OUT/'umn_reference.glb'),'bytes':len(blob),'triangles':sum(p['triangles'] for p in catalog)},indent=2))
