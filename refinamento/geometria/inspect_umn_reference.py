"""Inspect an officially downloadable teaching model for LOCAL study only.

No model from this script belongs in the public bundle: a redistribution
license has not been identified. Read STL coordinates only; never run the
Cura configuration files inside the author's 3MF printing project.
"""
from pathlib import Path
import json
import zipfile
import hashlib
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT=Path(__file__).resolve().parent/'referencias_locais'
ARCHIVE=OUT/'UMN_MC_VALVES.zip'


def read_ascii_stl(data):
    points=[]
    for line in data.splitlines():
        if line.startswith(b'vertex '):points.append(line[7:])
    raw=np.loadtxt(io.BytesIO(b'\n'.join(points)),dtype=np.float64)
    assert len(raw)%3==0 and np.isfinite(raw).all()
    v,idx=np.unique(raw,axis=0,return_inverse=True)
    return v,idx.reshape(-1,3).astype(np.uint32)


def main():
    entries=[];meshes=[]
    with zipfile.ZipFile(ARCHIVE) as z:
        for info in z.infolist():
            if not info.filename.endswith('.stl'):continue
            # Full source retained in ZIP; inspect all four cuts without
            # executing any project or slicer instructions.
            data=z.read(info);v,f=read_ascii_stl(data)
            path=OUT/(Path(info.filename).stem+'.npz')
            np.savez_compressed(path,vertices=v.astype('<f4'),faces=f)
            entries.append({'file':path.name,'source_entry':info.filename,'source_sha256':hashlib.sha256(data).hexdigest(),
                'vertices':len(v),'triangles':len(f),'finite':True,'bounds':[v.min(0).tolist(),v.max(0).tolist()],
                'anatomical_parts_segmented':False,'source_label':Path(info.filename).stem,
                'license':'Not cleared for redistribution; local reference only'})
            # Three smaller pieces can be rendered in full without memory
            # heavy rasterization of the largest ~800k triangle shell.
            if info.file_size<60_000_000:meshes.append((info.filename,v,f))
            print(entries[-1],flush=True)
    fig=plt.figure(figsize=(15,9),facecolor='#f5f3ed')
    for i,(name,v,f) in enumerate(meshes):
        c=(v.min(0)+v.max(0))/2;rad=(v.max(0)-v.min(0)).max()*.55
        for view,(el,az) in enumerate([(35,-90),(35,90)]):
            ax=fig.add_subplot(2,3,view*3+i+1,projection='3d',proj_type='ortho')
            ax.add_collection3d(Poly3DCollection(v[f],facecolors='#c9907d',edgecolors='#c9907d',linewidths=0,shade=True))
            ax.set_xlim(c[0]-rad,c[0]+rad);ax.set_ylim(c[1]-rad,c[1]+rad);ax.set_zlim(c[2]-rad,c[2]+rad)
            ax.set_box_aspect((1,1,1));ax.view_init(el,az);ax.set_axis_off();ax.set_title(Path(name).stem+'\n'+str(len(f))+' triângulos originais',fontsize=10)
    fig.suptitle('UMN / Visible Heart Laboratories — cortes didáticos prontos\nReferência local separada; orientação das vistas apenas de inspeção, sem registro ao atlas BP3D',fontsize=14)
    fig.tight_layout(rect=(0,0,1,.94));fig.savefig(OUT/'UMN_MC_VALVES_inspecao.png',dpi=140)
    report={'source_page':'https://www.vhlab.umn.edu/atlas/echocardiography-tutorial/exam-views-models.shtml',
        'source_zip':'https://www.vhlab.umn.edu/atlas/3dscans/MC_VALVES.zip','parts':entries,
        'provenance_limit':'Page identifies instructional views and offers files for printing. Specific donor/scan parameters for this ZIP were not found; do not assign a donor or claim patient-specific accuracy.',
        'usage':'Local academic inspection only; public redistribution license not established. No meshes have been integrated into the BP3D anatomical scene.',
        'rendered':'Three smaller original pieces, in full, from two opposing directions; the largest piece is only numerically inspected in this pass.'}
    (OUT/'UMN_MC_VALVES_inspecao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
