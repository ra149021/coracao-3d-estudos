"""Evidence of source registration, never a substitute for interactive review."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from register_bp3d import OUT, COMMON, NEW, read_obj, z_mesh, apply

report=json.loads((OUT/'registration.json').read_text())
transform=report['scale'],np.array(report['rotation']),np.array(report['translation_mm'])
new={fj:dict(np.load(OUT/'meshes'/(fj+'.npz'))) for fj,*_ in NEW}
common={name:z_mesh(name) for _,name in COMMON}
fig=plt.figure(figsize=(15,10),facecolor='#f5f3ed')


def draw(ax,v,f,color,alpha=1):
    ax.add_collection3d(Poly3DCollection(v[f],facecolors=color,edgecolors=color,linewidths=0,alpha=alpha,shade=True))


def setup(ax,vs,title,elev=25,azim=-90):
    a=np.concatenate(vs);c=(a.min(0)+a.max(0))/2;r=(a.max(0)-a.min(0)).max()*.55
    ax.set_xlim(c[0]-r,c[0]+r);ax.set_ylim(c[1]-r,c[1]+r);ax.set_zlim(c[2]-r,c[2]+r)
    ax.set_box_aspect((1,1,1));ax.view_init(elev,azim);ax.set_axis_off();ax.set_title(title,fontsize=11)


ax=fig.add_subplot(231,projection='3d',proj_type='ortho')
name=COMMON[2][1];a,af=read_obj(COMMON[2][0]);a=apply(a,transform);b,bf=common[name]
draw(ax,b,bf,'#be8566',.45);draw(ax,a,af,'#0b978f',.5)
setup(ax,[a,b],'Peça comum: cúspide mitral posterior\nZ (rosa) × BP registrado (verde)',25,-110)

for k,(fj,title) in enumerate([('FJ2421','Tricúspide · cúspide anterior'),('FJ2420','Mitral · cúspide anterior')],start=2):
    ax=fig.add_subplot(2,3,k,projection='3d',proj_type='ortho')
    d=new[fj];draw(ax,d['z_world_mm'],d['faces'],'#178e87')
    setup(ax,[d['z_world_mm']],title+'\nFolheto e cordas da malha BodyParts3D',25,-90)

for k,side in [(4,'right'),(5,'left')]:
    ax=fig.add_subplot(2,3,k,projection='3d',proj_type='ortho')
    vs=[]
    for n,(v,f) in common.items():
        if side not in n:continue
        draw(ax,v,f,'#e2cba6' if 'leaflet' in n else '#ad6861');vs.append(v)
    for fj in (['FJ2421'] if side=='right' else ['FJ2420','FJ2418']):
        d=new[fj];v=d['z_world_mm'];draw(ax,v,d['faces'],'#178e87' if fj!='FJ2418' else '#596bab');vs.append(v)
    setup(ax,vs,('VD' if side=='right' else 'VE')+' · relações sem parede ventricular\nNovos folhetos em verde; porção papilar em azul',25,-90)

ax=fig.add_subplot(236,projection='3d',proj_type='ortho')
vs=[]
for n,(v,f) in common.items():
    draw(ax,v,f,'#e2cba6' if 'leaflet' in n else '#ad6861');vs.append(v)
for fj,d in new.items():
    v=d['z_world_mm'];draw(ax,v,d['faces'],'#178e87' if fj!='FJ2418' else '#596bab');vs.append(v)
setup(ax,vs,'Conjunto atrioventricular · vista superior\nUma única transformação; nenhuma deformação local',80,-90)
fig.suptitle('Complementos de geometria pronta — inspeção de integração\nRegistro numérico estável; a malha não demonstra a valva em movimento nem garante todas as inserções',fontsize=15)
fig.tight_layout(rect=(0,0,1,.94))
fig.savefig(OUT/'registro_inspecao.png',dpi=160)
print(OUT/'registro_inspecao.png')
