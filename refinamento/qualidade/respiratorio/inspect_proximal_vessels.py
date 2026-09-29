"""Inspect preserved proximal pulmonary vessels against the shared Z world."""
from pathlib import Path
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_respiratory_assets import SourceGLB

cat = json.loads((ROOT / 'site/assets/respiratory/catalog.json').read_text())
src = SourceGLB('respiratory', ROOT / 'site/assets/respiratory/model.glb')
airways = {'Trachea', 'Left main bronchus', 'Right main bronchus',
           'Left superior lobar bronchus', 'Left inferior lobar bronchus',
           'Right superior lobar bronchus', 'Intermediate bronchus.r',
           'Middle lobar bronchus.r', 'Right inferior lobar bronchus'}
fig = plt.figure(figsize=(16, 8), facecolor='#f5f2ed')
for n, (title, azim) in enumerate([('Vasos e brônquios proximais · vista posterior', -90),
                                  ('Relação lateral · lobos translúcidos', 20)], 1):
    ax = fig.add_subplot(1, 2, n, projection='3d', facecolor='#f5f2ed')
    bounds = []
    for p in cat['parts']:
        if p['group'] not in ['vascular_pulmonar', 'pulmoes'] and p['sourceName'] not in airways:
            continue
        v, f, _ = src.geometry(p['id']); v = v[:, [0, 2, 1]]
        alpha = .08 if p['group'] == 'pulmoes' else 1
        ax.add_collection3d(Poly3DCollection(v[f], facecolors=p['color'],
                                            linewidths=0, alpha=alpha, shade=True))
        bounds.extend([v.min(0), v.max(0)])
    bounds = np.array(bounds); low, high = bounds.min(0), bounds.max(0)
    center = (low + high) / 2; radius = (high - low).max() * .51
    ax.set(xlim=(center[0]-radius, center[0]+radius),
           ylim=(center[1]-radius, center[1]+radius), zlim=(center[2]-radius, center[2]+radius))
    ax.set_box_aspect((1, 1, 1)); ax.view_init(8, azim); ax.set_axis_off()
    ax.set_title(title, fontsize=14)
fig.suptitle('Z-Anatomy · oito vasos proximais no registro original\n'
             'Artérias em azul e veias em vermelho: cores didáticas, sem rede segmentar', fontsize=17)
fig.subplots_adjust(left=.01, right=.99, bottom=.01, top=.88, wspace=.01)
out = Path(__file__).with_name('proximal_vessels_inspection.png')
fig.savefig(out, dpi=140)
print(out)
