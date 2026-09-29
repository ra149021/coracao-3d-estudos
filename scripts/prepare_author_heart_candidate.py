"""Replace only the original Z cardiac surfaces with the author's evaluated render modifiers.

Candidate only. Other meshes, IDs, positions and curriculum metadata are preserved.
"""
from pathlib import Path
import json,struct,hashlib
import numpy as np
from build_respiratory_assets import normal_array

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/heart-author';OUT.mkdir(exist_ok=True)
DOC=ROOT/'refinamento/qualidade';DOC.mkdir(exist_ok=True)
BASE=ROOT/'fontes/quality_baseline_v03'
SOURCE=BASE if (BASE/'heart.glb').exists() else ROOT/'site/assets'
raw=(SOURCE/'heart.glb').read_bytes()
n,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
old=json.loads(raw[20:20+n]);binary=raw[28+n:]
catalog=json.loads((SOURCE/'catalog.json').read_text())
evaluations={r['name']:r for r in json.loads((ROOT/'malhas/heart_author_evaluated/manifest.json').read_text())}
chunks=bytearray();accessors=[];views=[]
def read(i):
 a=old['accessors'][i];v=old['bufferViews'][a['bufferView']];dim={'SCALAR':1,'VEC3':3}[a['type']];dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]
 return np.ndarray((a['count'],dim),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dim*np.dtype(dtype).itemsize),np.dtype(dtype).itemsize)).copy()
def write(a,typ,component,target):
 while len(chunks)%4:chunks.append(0)
 data=a.tobytes();views.append({'buffer':0,'byteOffset':len(chunks),'byteLength':len(data),'target':target});chunks.extend(data)
 ac={'bufferView':len(views)-1,'componentType':component,'count':len(a),'type':typ}
 if typ=='VEC3':ac.update(min=a.min(0).tolist(),max=a.max(0).tolist())
 accessors.append(ac);return len(accessors)-1
report=[]
for node in old['nodes']:
 if 'mesh' not in node:continue
 part=next(p for p in catalog['parts'] if p['id']==node.get('extras',{}).get('partId',node['name']))
 mesh=old['meshes'][node['mesh']];assert len(mesh['primitives'])==1
 prim=mesh['primitives'][0];v=read(prim['attributes']['POSITION']);faces=read(prim['indices']).reshape(-1,3).astype('<u4');norm=read(prim['attributes']['NORMAL'])
 if part['sourceName'] in evaluations and evaluations[part['sourceName']]['originalModifiers']:
  info=evaluations[part['sourceName']];z=np.load(ROOT/'malhas/heart_author_evaluated'/info['file'],allow_pickle=False)
  newv=(((z['vertices'][:,[0,2,1]]*[100,100,-100])-np.array([2.,130.5,2.]))*.25).astype('<f4');newfaces=z['faces'].astype('<u4')
  norm,fallbacks=normal_array(newv,newfaces)
  report.append({'id':part['id'],'name':part['sourceName'],'oldVertices':len(v),'newVertices':len(newv),'oldTriangles':len(faces),'newTriangles':len(newfaces),'oldBounds':[v.min(0).tolist(),v.max(0).tolist()],'newBounds':[newv.min(0).tolist(),newv.max(0).tolist()],'boundsDifferenceNominalMm':float(np.max(np.abs(np.array([v.min(0),v.max(0)])-np.array([newv.min(0),newv.max(0)])))/.25*10),'normalFallbacks':fallbacks,'authorEvaluation':info})
  v,faces=newv,newfaces
  part.update(vertices=len(v),triangles=len(faces),bounds=[v.min(0).tolist(),v.max(0).tolist()],surfaceMethod='Original Z-Anatomy render modifiers evaluated in Blender; no custom parameters' if info['originalModifiers'] else 'Original source surface, without modifiers',sourceFile='Startup.blend · modificadores de renderização do autor' if info['originalModifiers'] else 'Startup.blend')
 prim['attributes']={'POSITION':write(v.astype('<f4'),'VEC3',5126,34962),'NORMAL':write(norm.astype('<f4'),'VEC3',5126,34962)}
 prim['indices']=write(faces.ravel().astype('<u4'),'SCALAR',5125,34963)
old['accessors']=accessors;old['bufferViews']=views;old['buffers']=[{'byteLength':len(chunks)}]
doc=json.dumps(old,separators=(',',':')).encode();doc+=b' '*((-len(doc))%4);chunks+=b'\0'*((-len(chunks))%4)
result=struct.pack('<4sII',b'glTF',2,28+len(doc)+len(chunks))+struct.pack('<II',len(doc),0x4e4f534a)+doc+struct.pack('<II',len(chunks),0x004e4942)+chunks
(OUT/'model.glb').write_bytes(result)
catalog['model'].update(bytes=len(result),sha256=hashlib.sha256(result).hexdigest(),triangles=sum(p['triangles'] for p in catalog['parts']))
catalog['title']='Coração · superfícies do autor'
catalog['surfaceEvaluation']={'source':'Startup.blend','blender':'4.2.22 LTS','scriptAutoExecution':False,'method':'Original render settings of SUBSURF modifiers, no added modifiers. Coordinates/registration of all other pieces unchanged.','surfaces':report}
(OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
(DOC/'heart_author_candidate.json').write_text(json.dumps({'candidateOnly':True,'model':catalog['model'],'surfaces':report},ensure_ascii=False,indent=2))
print(json.dumps({'bytes':len(result),'triangles':catalog['model']['triangles'],'surfaces':[{'id':r['id'],'triangles':r['newTriangles'],'boundsDifferenceNominalMm':r['boundsDifferenceNominalMm']} for r in report]}))
