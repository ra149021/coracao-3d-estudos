"""Evaluate only the original cardiac surface modifiers with Blender auto-execution off.

Writes a separate candidate; never changes the source .blend or site assets.
"""
from pathlib import Path
import json
import numpy as np
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'malhas/heart_author_evaluated'
OUT.mkdir(parents=True,exist_ok=True)
NAMES=[p['sourceName'] for p in json.loads((ROOT/'site/assets/catalog.json').read_text())['parts'] if p['sourceFile'].startswith('Startup.blend')]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
print('Blender',bpy.app.version_string,'autoexec',bpy.context.preferences.filepaths.use_scripts_auto_execute,flush=True)
with bpy.data.libraries.load(str(ROOT/'fontes/z_anatomy/Startup.blend'),link=False) as (src,dst):
    assert all(n in src.objects for n in NAMES)
    dst.objects=NAMES
print('Loaded selected chambers',flush=True)
report=[]
for obj in dst.objects:
    bpy.context.scene.collection.objects.link(obj)
    original_modifiers=[]
    for mod in obj.modifiers:
        row={'name':mod.name,'type':mod.type,'show_viewport':mod.show_viewport,'show_render':mod.show_render}
        if mod.type=='SUBSURF':
            row.update(levels=mod.levels,render_levels=mod.render_levels,subdivision_type=mod.subdivision_type)
            mod.levels=mod.render_levels
        mod.show_viewport=mod.show_render
        original_modifiers.append(row)
    bpy.context.view_layer.update()
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    vertices=np.empty((len(mesh.vertices),3),dtype=np.float32);mesh.vertices.foreach_get('co',vertices.ravel())
    matrix=np.array(obj.matrix_world,dtype=np.float64)
    vertices=vertices@matrix[:3,:3].T+matrix[:3,3]
    faces=np.empty((len(mesh.loop_triangles),3),dtype=np.uint32);mesh.loop_triangles.foreach_get('vertices',faces.ravel())
    assert np.isfinite(vertices).all() and faces.max()<len(vertices)
    filename=obj.name.replace(' ','_').lower()+'.npz'
    np.savez_compressed(OUT/filename,vertices=vertices.astype(np.float32),faces=faces)
    report.append({'name':obj.name,'blender':bpy.app.version_string,'originalModifiers':original_modifiers,'vertices':len(vertices),'triangles':len(faces),'bounds_m':[vertices.min(0).tolist(),vertices.max(0).tolist()],'matrix_world':matrix.tolist(),'file':filename})
    print(obj.name,len(vertices),len(faces),flush=True)
    evaluated.to_mesh_clear()
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
