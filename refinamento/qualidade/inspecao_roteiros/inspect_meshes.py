"""Read-only geometry inspection of published atlas assets; never edits the models."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from build_respiratory_assets import SourceGLB
OUT=Path(__file__).resolve().parent

def inspect(vertices,faces):
    unique,remap=np.unique(vertices,axis=0,return_inverse=True)
    faces=remap[faces]
    edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(unique),len(unique))).tocsr()
    n,labels=connected_components(graph,directed=False)
    area=np.linalg.norm(np.cross(unique[faces[:,1]]-unique[faces[:,0]],unique[faces[:,2]]-unique[faces[:,0]]),axis=1)/2
    components=[]
    for component in range(n):
        local_faces=faces[labels[faces[:,0]]==component]
        v=unique[labels==component]
        e=np.sort(np.concatenate([local_faces[:,[0,1]],local_faces[:,[1,2]],local_faces[:,[2,0]]]),axis=1)
        _,counts=np.unique(e,axis=0,return_counts=True)
        components.append(dict(vertices=len(v),triangles=len(local_faces),bounds=[v.min(0).tolist(),v.max(0).tolist()],boundaryEdges=int(np.sum(counts==1)),nonManifoldEdges=int(np.sum(counts>2))))
    components.sort(key=lambda c:c['triangles'],reverse=True)
    return dict(vertices=len(vertices),uniquePositions=len(unique),triangles=len(faces),zeroAreaFaces=int(np.sum(area<=1e-14)),components=components,method='Components join exact coincident positions. No tolerance-based welding or anatomical labels inferred.')

result={'scope':'Topology inspection; component counts are not anatomical structures.','assets':[]}
for file,ids in [('site/assets/heart.glb',['heart_00','heart_01','heart_02','heart_03','heart_26','heart_27','heart_28','bp_FJ2421','bp_FJ2420']),('site/assets/respiratory/model.glb',['resp_pleura'])]:
    source=SourceGLB('inspection',ROOT/file)
    record={'path':file,'sha256':hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),'parts':{}}
    for part in ids:
        v,f,_=source.geometry(part);record['parts'][part]=inspect(v,f)
        print(part,record['parts'][part]['triangles'],'triangles;',len(record['parts'][part]['components']),'components; largest',record['parts'][part]['components'][:4],flush=True)
    result['assets'].append(record)
(OUT/'topology.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
