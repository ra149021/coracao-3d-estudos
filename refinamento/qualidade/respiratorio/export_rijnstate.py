"""Convert the complete official STL to an independent, unsegmented GLB.

No smoothing, decimation, hole filling or inferred anatomical labels. Exact
coincident positions are welded to encode an indexed mesh. Original positions
are recoverable from the common transform recorded in catalog.json.
"""
from pathlib import Path
import sys
import re
import json
import hashlib
import struct
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_respiratory_assets import normal_array

HERE = Path(__file__).resolve().parent
OUT = HERE / 'rijnstate_reference'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT / 'fontes/qualidade_respiratorio/rijnstate_lung_2023.stl'
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'cdcc80f0eedf269f45d740c8a9a15a37e491f4ca79fc8a8fa699d9bc891084a3'
assert b'endsolid' in raw[-100:]
v = np.fromstring(b' '.join(re.findall(rb'vertex\s+([^\r\n]+)', raw)).decode(), sep=' ').reshape(-1, 3)
vertices, inverse = np.unique(v, axis=0, return_inverse=True)
faces = inverse.reshape(-1, 3).astype('<u4')
assert len(faces) == 312856 and np.isfinite(vertices).all()
edges = np.concatenate([faces[:, [0,1]], faces[:, [1,2]], faces[:, [2,0]]])
graph = coo_matrix((np.ones(len(edges)), (edges[:,0], edges[:,1])), shape=(len(vertices),len(vertices))).tocsr()
nc, labels = connected_components(graph, directed=False)
counts = np.sort(np.bincount(labels))[::-1]
center = (vertices.min(0) + vertices.max(0)) / 2
scale = .05
display = ((vertices-center)[:, [0,2,1]] * [scale,scale,-scale]).astype('<f4')
normals, fallbacks = normal_array(display, faces)
area = np.linalg.norm(np.cross(display[faces[:,1]]-display[faces[:,0]],
                               display[faces[:,2]]-display[faces[:,0]]), axis=1)
g = {'asset': {'version':'2.0', 'generator':'Source triangles preserved; common display transform',
              'copyright':'Meershoek, Loonen, Maal, Hekma, Hugen (2023); CC BY-NC-SA 4.0'},
     'scene':0, 'scenes':[{'nodes':[0]}],
     'nodes':[{'name':'rijnstate_broncovascular_model', 'mesh':0,
               'extras':{'partId':'rijnstate_broncovascular_model'}}],
     'meshes':[], 'accessors':[], 'bufferViews':[], 'buffers':[],
     'materials':[{'name':'Cor neutra de inspeção', 'doubleSided':True,
                   'pbrMetallicRoughness':{'baseColorFactor':[.76,.68,.56,1], 'metallicFactor':0, 'roughnessFactor':.74}}]}
binary = bytearray()
def put(a, kind, component, target):
    binary.extend(b'\0'*(-len(binary)%4)); start=len(binary); binary.extend(a.tobytes())
    idx=len(g['accessors']); view=len(g['bufferViews'])
    g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes,'target':target})
    acc={'bufferView':view,'componentType':component,'count':len(a),'type':kind}
    if kind=='VEC3': acc.update(min=a.min(0).tolist(),max=a.max(0).tolist())
    g['accessors'].append(acc); return idx
pos=put(display,'VEC3',5126,34962); norm=put(normals,'VEC3',5126,34962); ind=put(faces.ravel(),'SCALAR',5125,34963)
g['meshes'].append({'name':'LongSegmentenModel', 'primitives':[{'attributes':{'POSITION':pos,'NORMAL':norm},'indices':ind,'material':0,'mode':4}]})
g['buffers'].append({'byteLength':len(binary)})
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*(-len(j)%4)
blob=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
(OUT/'model.glb').write_bytes(blob)
provenance=json.loads(SOURCE.with_suffix('.provenance.json').read_text())
part={'id':'rijnstate_broncovascular_model','label':'Modelo broncovascular de referência · conjunto',
      'sourceName':'LongSegmentenModel','group':'referencia','source':'Meershoek et al., Rijnstate / Radboud (2023)',
      'license':'CC BY-NC-SA 4.0','quizEligible':False,'defaultVisible':True,'requirementIds':[],
      'color':'#c2ad8f','tissueColor':'#c2ad8f','vertices':len(vertices),'triangles':len(faces),
      'bounds':[display.min(0).tolist(),display.max(0).tolist()],
      'note':'Reconstrução de CT preparada pelos autores para impressão. Traqueia, brônquios, vasos e contexto cardíaco formam um conjunto sem rótulos individuais. Cores neutras não identificam tecidos.'}
cat={'version':1,'system':'respiratory','title':'Referência broncovascular de CT',
     'description':'Modelo independente com adaptações de impressão; não registra nem substitui as peças do Z-Anatomy.',
     'parts':[part],'groups':{'referencia':'Conjunto da fonte'},'mainGroups':['referencia'],
     'translucencyGroups':[],'labelGroups':[],
     'presets':[{'id':'exterior','label':'Conjunto original','groups':['referencia'],'direction':[0,0,1],
                 'note':'Modelo monocromático, sem separação editável de vasos, vias aéreas ou segmentos.'}],
     'model':{'file':'model.glb','bytes':len(blob),'parts':1,'triangles':len(faces),'sha256':hashlib.sha256(blob).hexdigest()},
     'orientation':{'x':'eixo +X da fonte, lado anatômico não certificado','y':'eixo +Z da fonte','z':'eixo −Y da fonte',
                    'transform':{'source_center':center.tolist(),'permutation':[0,2,1],'signed_scale':[scale,scale,-scale]},
                    'preserved':'Uma transformação rígida com escala comum; sem registro ao atlas.'},
     'limitations':['STL sem cores, texturas ou rótulos de tecidos; um grande componente fundido.',
                    'Superfícies manualmente suavizadas e truncadas pelos autores para impressão.',
                    'Entalhes para ímãs pertencem ao artefato didático, não à anatomia.',
                    'Não demonstra pleuras, paredes vasculares ou parênquima segmentar completo.',
                    'Não é um padrão anatômico universal nem soma estruturas à cobertura do roteiro.'],
     'sources':[dict(name='Meershoek et al. (2023)',**provenance)]}
(OUT/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2))
audit={'source':provenance,'export':cat['model'],'vertices_original':len(vertices),'triangles_preserved':True,
       'finite':bool(np.isfinite(display).all()),'indices_in_bounds':bool(faces.max()<len(display)),
       'unit_normals':bool(np.allclose(np.linalg.norm(normals,axis=1),1,atol=1e-6)),
       'normal_fallbacks':fallbacks,'zero_area_faces_float32':int((area==0).sum()),
       'connected_components':int(nc),'component_vertex_counts':counts.tolist(),
       'semantic_segmentation_available':False,'geometric_changes':'None; exact-position indexing and common display transform only.'}
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(cat['model'],indent=2))
