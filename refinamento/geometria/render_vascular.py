import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from register_bp3d import OUT,z_mesh
from prepare_vascular import glb_source

report=json.loads((OUT/'vascular.json').read_text())
original=glb_source()
prepared={p['fma']:(p,dict(np.load(OUT/p['file']))) for p in report['parts']}
chambers=[z_mesh(n) for n in ['Right atrium','Right ventricle','Left atrium','Left ventricle']]
a=np.concatenate([v for v,f in chambers]);center=(a.min(0)+a.max(0))/2;radius=(a.max(0)-a.min(0)).max()*.53
fig=plt.figure(figsize=(13,11),facecolor='#f5f3ed')
for k,(network,azim,title) in enumerate([
    ('z',-90,'Z-Anatomy atual · vista anterior'),('bp',-90,'BodyParts3D · vista anterior'),
    ('z',90,'Z-Anatomy atual · vista posterior'),('bp',90,'BodyParts3D · vista posterior')],start=1):
    ax=fig.add_subplot(2,2,k,projection='3d',proj_type='ortho')
    for v,f in chambers:
        ax.add_collection3d(Poly3DCollection(v[f],facecolors='#b4a6a5',edgecolors='none',linewidths=0,alpha=.14))
    if network=='z':
        meshes=[(v,f,'#d97151' if 'arter' in name else '#4f8cba') for name,(v,f) in original.items()]
    else:
        meshes=[(d['z_world_mm'],d['faces'],'#d97151' if p['group']=='coronarias' else '#4f8cba') for p,d in prepared.values()]
    for v,f,color in meshes:
        ax.add_collection3d(Poly3DCollection(v[f],facecolors=color,edgecolors=color,linewidths=0,shade=True))
    ax.set_xlim(center[0]-radius,center[0]+radius);ax.set_ylim(center[1]-radius,center[1]+radius);ax.set_zlim(center[2]-radius,center[2]+radius)
    ax.set_box_aspect((1,1,1));ax.view_init(15,azim);ax.set_axis_off();ax.set_title(title,fontsize=12)
fig.suptitle('Comparação das redes coronárias prontas\n23 grupos BodyParts3D, 104 elementos únicos — alternativa exclusiva à rede Z-Anatomy',fontsize=15)
fig.tight_layout(rect=(0,0,1,.94));fig.savefig(OUT/'vascular_inspecao.png',dpi=160)
print(OUT/'vascular_inspecao.png')
