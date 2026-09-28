"""Inspect complete exported source surfaces; no downsampling or anatomy synthesis."""
from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_respiratory_assets import SourceGLB

catalog = json.loads((ROOT / 'site/assets/respiratory/catalog.json').read_text())
source = SourceGLB('respiratory', ROOT / 'site/assets/respiratory/model.glb')
data = {part['id']: source.geometry(part['id'])[:2] for part in catalog['parts']}
fig = plt.figure(figsize=(15, 14), facecolor='#f5f2ed')
panels = [
    ('Lobos e árvore brônquica', {'arvore','pulmoes'}, [], {'pulmoes': .15}, 15, 80),
    ('Vias superiores · relação original', {'nariz','seios','faringe','laringe'}, [], {}, 15, 15),
    ('Laringe · cartilagens e estruturas internas', {'laringe','musculos_laringe','ligamentos_laringe'}, [], {'laringe': .22}, 18, 60),
    ('Pleura agregada, pulmões e diafragma', {'pleuras','pulmoes'}, ['Diaphragm_node'], {'pleuras': .08, 'pulmoes': .22}, 12, 65),
]
for number, (title, groups, names, opacity, elevation, azimuth) in enumerate(panels, 1):
    axis = fig.add_subplot(2, 2, number, projection='3d', facecolor='#f5f2ed')
    bounds = []
    for part in catalog['parts']:
        if part['group'] not in groups and part['sourceName'] not in names: continue
        if part['sourceName'].startswith('(Anteromedial'): continue
        vertices, faces = data[part['id']]
        vertices = vertices[:, [0, 2, 1]]
        collection = Poly3DCollection(vertices[faces], facecolor=part['color'], linewidths=0,
                                      edgecolors='none', alpha=opacity.get(part['group'], 1))
        axis.add_collection3d(collection)
        bounds.extend([vertices.min(0), vertices.max(0)])
    bounds = np.array(bounds); lo, hi = bounds.min(0), bounds.max(0)
    center = (lo + hi) / 2; radius = (hi - lo).max() * .55
    axis.set(xlim=(center[0]-radius,center[0]+radius),
             ylim=(center[1]-radius,center[1]+radius),zlim=(center[2]-radius,center[2]+radius))
    axis.set_box_aspect((1, 1, 1)); axis.view_init(elevation, azimuth)
    axis.set_axis_off(); axis.set_title(title, fontsize=14, pad=0)
fig.suptitle('Inspeção geométrica · superfícies prontas Z-Anatomy\nCores ilustrativas; peças e relações da fonte preservadas',fontsize=18)
fig.subplots_adjust(left=.01,right=.99,bottom=.035,top=.91,wspace=.01,hspace=.02)
path = Path(__file__).with_name('inspecao_geometrica.png')
fig.savefig(path, dpi=150)
print(path)
