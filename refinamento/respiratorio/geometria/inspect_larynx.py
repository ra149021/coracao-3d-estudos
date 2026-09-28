"""Render the independent original BP larynx assembly for visual inspection."""
from pathlib import Path
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from build_respiratory_assets import SourceGLB
catalog=json.loads((ROOT/'site/assets/larynx/catalog.json').read_text())
source=SourceGLB('larynx',ROOT/'site/assets/larynx/model.glb')
data={p['id']:source.geometry(p['id'])[:2] for p in catalog['parts']}
fig=plt.figure(figsize=(18,8),facecolor='#f5f2ed')
panels=[
 ('Cartilagens e hioide',lambda p:p['group'] in ['cartilagens','hioide'],{},12,70),
 ('Componentes vocais · vista superior',lambda p:p['group']=='vocais' or 'conus elasticus' in p['sourceName'] or 'arytenoid cartilage' in p['sourceName'],{'membranas':.12},83,90),
 ('Conjunto muscular · vista posterior',lambda p:p['group'] in ['cartilagens','musculos','vocais'],{'cartilagens':.12},20,-90),
]
light=np.array([.2,-.4,.9]);light/=np.linalg.norm(light)
for num,(title,include,alpha,elev,azim) in enumerate(panels,1):
 ax=fig.add_subplot(1,3,num,projection='3d',facecolor='#f5f2ed');bounds=[]
 for part in catalog['parts']:
  if not include(part):continue
  v,f=data[part['id']];v=v[:,[0,2,1]];tri=v[f]
  normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
  lighting=.4+.6*np.abs(normal@light)
  colors=np.array(to_rgb(part['color']))[None,:]*lighting[:,None]
  poly=Poly3DCollection(tri,facecolors=colors,edgecolors='none',linewidths=0,alpha=alpha.get(part['group'],1))
  ax.add_collection3d(poly);bounds.extend([v.min(0),v.max(0)])
 bounds=np.array(bounds);lo,hi=bounds.min(0),bounds.max(0);center=(lo+hi)/2;radius=(hi-lo).max()*.57
 ax.set(xlim=(center[0]-radius,center[0]+radius),ylim=(center[1]-radius,center[1]+radius),zlim=(center[2]-radius,center[2]+radius))
 ax.set_box_aspect((1,1,1));ax.view_init(elev,azim);ax.set_axis_off();ax.set_title(title,fontsize=14)
fig.suptitle('Laringe BodyParts3D · modelo independente\nPeças e relações da fonte preservadas; cores ilustrativas',fontsize=19,y=.96)
fig.text(.5,.08,'Ligamento e músculo vocais são componentes da prega vocal. A mucosa completa não está individualizada.\nBodyParts3D / The Database Center for Life Science — CC BY 4.0',ha='center',fontsize=11)
fig.subplots_adjust(left=0,right=1,bottom=.1,top=.82,wspace=-.05)
path=Path(__file__).with_name('larynx_inspecao.png');fig.savefig(path,dpi=160);print(path)
