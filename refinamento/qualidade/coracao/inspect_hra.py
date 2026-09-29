"""Inspect the original NIH/HRA GLB; never invent anatomy or alter source files."""
from pathlib import Path
import struct,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'fontes/qualidade_coracao/nih_hra_heart_download.bin'

def read_glb():
 b=SOURCE.read_bytes(); n,t=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n]);offset=20+n
 bn,bt=struct.unpack_from('<II',b,offset);buf=b[offset+8:offset+8+bn]
 def accessor(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']]
  dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
  k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  offset=v.get('byteOffset',0)+a.get('byteOffset',0)
  if 'byteStride' in v:
   out=np.ndarray((a['count'],k),dtype=dtype,buffer=buf,offset=offset,strides=(v['byteStride'],np.dtype(dtype).itemsize)).copy()
  else: out=np.frombuffer(buf,dtype=dtype,count=a['count']*k,offset=offset).reshape(-1,k).copy()
  return out
 data=[]
 for m in g['meshes']:
  assert len(m['primitives'])==1
  p=m['primitives'][0];v=accessor(p['attributes']['POSITION']);f=accessor(p['indices']).reshape(-1,3)
  data.append({'name':m['name'],'vertices':v,'faces':f,'normals':accessor(p['attributes']['NORMAL']), 'colors':accessor(p['attributes']['COLOR_0']) if 'COLOR_0' in p['attributes'] else None})
 return g,data

if __name__=='__main__':
 g,data=read_glb()
 # Matplotlib uses Z-up: rearrange glTF XYZ to XZY for the inspection image only.
 allv=np.concatenate([d['vertices'][:,[0,2,1]] for d in data]);center=(allv.min(0)+allv.max(0))/2;span=np.max(np.ptp(allv,axis=0))/2*1.08
 panels=[('Conjunto · vista anterior',list(range(14)),20,90,None),('Conjunto · vista posterior',list(range(14)),20,-90,None),('Valvas e peças papilares',list(range(9)),40,90,None),('VD aberto por corte de inspeção',[1,3,4,6,7,11,12],18,90,11),('Septo interventricular individual',[12],20,35,None),('Átrios separados · vista superior',[9,10],75,90,None)]
 fig=plt.figure(figsize=(16,10),facecolor='#f2f3f5')
 for k,(title,ids,elev,azim,cut) in enumerate(panels):
  ax=fig.add_subplot(2,3,k+1,projection='3d',proj_type='ortho')
  for i in ids:
   d=data[i];v=d['vertices'][:,[0,2,1]];tris=v[d['faces']]
   if cut==i: tris=tris[tris.mean(axis=1)[:,1]<np.median(v[:,1])]
   color='#d8c7a0' if i<4 else '#b47969' if i<9 else '#bf7b7e' if i in [9,13] else '#8b5861' if i==12 else '#cc9490'
   ax.add_collection3d(Poly3DCollection(tris,facecolors=color,edgecolors=color,linewidths=0,shade=True))
  if k in [2,4]:
   vv=np.concatenate([data[i]['vertices'][:,[0,2,1]] for i in ids]);c=(vv.min(0)+vv.max(0))/2;s=np.max(np.ptp(vv,axis=0))/2*1.12
  else:c=center;s=span
  ax.set_xlim(c[0]-s,c[0]+s);ax.set_ylim(c[1]-s,c[1]+s);ax.set_zlim(c[2]-s,c[2]+s)
  ax.view_init(elev=elev,azim=azim);ax.set_box_aspect((1,1,1));ax.set_axis_off();ax.set_title(title,fontsize=12)
 fig.suptitle('HRA / Visible Human Male · geometria original NIH 3DPX-021000\n14 malhas · 164.119 triângulos · cores didáticas; sem textura fotográfica. Corte ilustrativo não gravado na malha.',fontsize=15)
 fig.tight_layout(rect=(0,0,1,.93));out=Path(__file__).with_name('hra_inspecao.png');fig.savefig(out,dpi=140);print(out)
