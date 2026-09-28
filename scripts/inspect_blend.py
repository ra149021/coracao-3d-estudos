from pathlib import Path
import json
import re
import bpy

ROOT = Path(__file__).resolve().parents[1]
print('BLENDER_READY', bpy.app.version_string, flush=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ROOT/'fontes/z_anatomy/Startup.blend'), link=False) as (source, destination):
    destination.objects = source.objects
    destination.collections = source.collections
print('DATA_LOADED',len(bpy.data.objects),flush=True)
objects = []
for obj in bpy.data.objects:
    row = {'name': obj.name, 'type': obj.type, 'collections':[c.name for c in obj.users_collection],
           'parent':obj.parent.name if obj.parent else None,
           'matrix_world':[list(r) for r in obj.matrix_world], 'hidden':obj.hide_viewport}
    if obj.type == 'MESH':
        row.update(vertices=len(obj.data.vertices), polygons=len(obj.data.polygons), data_name=obj.data.name,
                   dimensions=list(obj.dimensions), materials=[m.name for m in obj.data.materials if m])
    if obj.type == 'FONT': row['text'] = obj.data.body
    if obj.type == 'CURVE': row['splines'] = len(obj.data.splines)
    objects.append(row)
collections = []
print('OBJECTS_INDEXED',len(objects),flush=True)
for c in bpy.data.collections:
    meshes = [o.name for o in c.all_objects if o.type=='MESH' and len(o.data.polygons)>0]
    collections.append({'name':c.name,'children':[x.name for x in c.children],'objects':[o.name for o in c.objects],'meshes':meshes})
out=ROOT/'malhas'
out.mkdir(exist_ok=True)
(out/'z_blend_inventory.json').write_text(json.dumps({'blender':bpy.app.version_string,'objects':objects,'collections':collections},ensure_ascii=False,indent=2))
print('TOTAL',len(objects),'MESHES',sum(x['type']=='MESH' and x['polygons']>0 for x in objects), flush=True)
for c in collections:
    if re.search('heart|pericard|myocardi|cardiac|coronary|valv|chorda|papill|septum|ovalis',c['name'],re.I):
        print('COLLECTION',c['name'],'MESH_COUNT',len(c['meshes']),'DIRECT_OBJECTS',len(c['objects']), flush=True)
for o in objects:
    if o['type']=='MESH' and re.search('heart|atri|ventri|papill|coronar|pericard|chorda|ovalis|fibrous|sinuatrial|sinoatrial|terminal|sept|valv|cusp',o['name'],re.I):
        print('MESH',o['name'],o['vertices'],o['polygons'],flush=True)
