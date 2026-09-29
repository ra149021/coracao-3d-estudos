from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'malhas/heart_source'
entries=json.loads((source/'manifest.json').read_text())
data={x['name']:dict(np.load(source/x['file'])) for x in entries}
verts=np.concatenate([m['vertices'] for m in data.values()])
center=(verts.min(0)+verts.max(0))/2
span=(verts.max(0)-verts.min(0)).max()/2*1.08
views=[
 ('Coração — todos os 17 objetos',None,20,-90,False),
 ('Coração — vista oposta',None,20,90,False),
 ('Átrio direito — corte de inspeção',['Right atrium'],20,-90,True),
 ('Ventrículo direito — corte de inspeção',[n for n in data if 'right ventricle' in n or n=='Right ventricle'],20,-90,True),
 ('Ventrículo esquerdo — corte de inspeção',[n for n in data if 'left ventricle' in n or n=='Left ventricle'],20,-90,True),
 ('Folhetos e músculos papilares',[n for n in data if 'leaflet' in n or 'papillary' in n],35,-90,False)
]
fig=plt.figure(figsize=(15,10),facecolor='#f5f5f5')
for k,(title,names,elev,azim,cut) in enumerate(views):
 ax=fig.add_subplot(2,3,k+1,projection='3d',proj_type='ortho')
 chosen=data if names is None else {n:data[n] for n in names}
 for name,mesh in chosen.items():
  v=mesh['vertices'];faces=mesh['faces'];tris=v[faces]
  if cut and name in ['Right atrium','Right ventricle','Left ventricle']:
   tris=tris[tris.mean(1)[:,1]>np.median(v[:,1])]
  color='#cb7776' if 'Right' in name else '#aa4752'
  if 'leaflet' in name:color='#dcc487'
  if 'papillary' in name:color='#925447'
  pc=Poly3DCollection(tris,facecolors=color,edgecolors=color,linewidths=0,shade=True,alpha=1)
  ax.add_collection3d(pc)
 ax.set_xlim(center[0]-span,center[0]+span);ax.set_ylim(center[1]-span,center[1]+span);ax.set_zlim(center[2]-span,center[2]+span)
 ax.view_init(elev=elev,azim=azim);ax.set_box_aspect((1,1,1));ax.set_axis_off();ax.set_title(title,fontsize=11)
fig.suptitle('Z-Anatomy — geometria original, sem acréscimos\nCortes por remoção de faces para inspeção; nomes ainda não validados visualmente',fontsize=15)
fig.tight_layout(rect=(0,0,1,.94))
out=ROOT/'site/auditoria/evidencias';out.mkdir(parents=True,exist_ok=True)
fig.savefig(out/'z_coracao_inspecao.png',dpi=150)
print(out/'z_coracao_inspecao.png')
