"""Read Blender SDNA/data blocks without running any embedded scripts.

Supports the little-endian 64-bit Blender 3.5 source file used in this audit.
Offsets are obtained from the file's own DNA and checked against declared sizes.
This inventory describes source data, not evaluated modifiers or visual validity.
"""
from pathlib import Path
import struct
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

class BlendData:
    def __init__(self, path):
        self.raw = path.read_bytes()
        assert self.raw[:12] == b'BLENDER-v305', self.raw[:12]
        self.blocks = {}
        self.scopes = {}
        owner = None
        offset=12
        while offset+24 <= len(self.raw):
            code,size,ptr,sdna,num=struct.unpack_from('<4sIQII',self.raw,offset)
            block={'code':code,'size':size,'ptr':ptr,'sdna':sdna,'num':num,'start':offset+24}
            if code!=b'DATA':
                owner=ptr
                self.scopes[owner]={}
            else:
                self.scopes[owner][ptr]=block
            if ptr:self.blocks[ptr]=block
            if code==b'DNA1': dna=self.raw[offset+24:offset+24+size]
            offset+=24+size
            if code==b'ENDB':break
        assert offset==len(self.raw)
        p=8
        def uint():
            nonlocal p
            v=struct.unpack_from('<I',dna,p)[0];p+=4;return v
        def strings(n):
            nonlocal p
            arr=[]
            for _ in range(n):
                end=dna.index(0,p);arr.append(dna[p:end].decode());p=end+1
            p=(p+3)&~3
            return arr
        names=strings(uint());assert dna[p:p+4]==b'TYPE';p+=4
        types=strings(uint());assert dna[p:p+4]==b'TLEN';p+=4
        lengths=struct.unpack_from('<'+'H'*len(types),dna,p);p+=len(types)*2;p=(p+3)&~3
        assert dna[p:p+4]==b'STRC';p+=4
        count=uint();self.structs={};self.struct_order=[]
        for _ in range(count):
            ti,nf=struct.unpack_from('<HH',dna,p);p+=4;fields={};off=0
            for _ in range(nf):
                fti,fni=struct.unpack_from('<HH',dna,p);p+=4
                name=names[fni];ft=types[fti];size=8 if '*' in name else lengths[fti]
                for a in re.findall(r'\[(\d+)\]',name):size*=int(a)
                fields[name.lstrip('*').split('[')[0]]={'offset':off,'size':size,'type':ft,'pointer':'*' in name}
                off+=size
            if types[ti] in ['ID','Object','Mesh','Collection','CollectionObject','CollectionChild','CustomData','CustomDataLayer','MPoly','MLoop','MVert']:
                assert off==lengths[ti],(types[ti],off,lengths[ti])
            self.structs[types[ti]]={'fields':fields,'size':lengths[ti]}
            self.struct_order.append(types[ti])

    def block(self,ptr,owner=None):return self.scopes.get(owner,{}).get(ptr,self.blocks.get(ptr))
    def address(self,ptr,typ,field,owner=None):
        return self.block(ptr,owner)['start']+self.structs[typ]['fields'][field]['offset']
    def value(self,ptr,typ,field,fmt,owner=None):return struct.unpack_from('<'+fmt,self.raw,self.address(ptr,typ,field,owner))
    def name(self,ptr):
        start=self.blocks[ptr]['start']+self.structs['ID']['fields']['name']['offset']
        return self.raw[start:start+66].split(b'\0')[0][2:].decode('utf-8','replace')
    def linked(self,ptr,field,node_type,object_field):
        first=self.value(ptr,'Collection',field,'Q')[0];seen=set();out=[]
        while first:
            assert first not in seen
            seen.add(first)
            out.append(self.value(first,node_type,object_field,'Q',ptr)[0])
            first=self.value(first,node_type,'next','Q',ptr)[0]
        return out
    def layers(self,mesh_ptr,field):
        base=self.address(mesh_ptr,'Mesh',field)
        layerptr=struct.unpack_from('<Q',self.raw,base)[0]
        n=struct.unpack_from('<i',self.raw,base+self.structs['CustomData']['fields']['totlayer']['offset'])[0]
        out=[]
        if not layerptr:return out
        layerbase=self.block(layerptr,mesh_ptr)['start'];fields=self.structs['CustomDataLayer']['fields']
        for i in range(n):
            o=layerbase+i*self.structs['CustomDataLayer']['size']
            name=self.raw[o+fields['name']['offset']:o+fields['name']['offset']+68].split(b'\0')[0].decode('utf-8','replace')
            out.append({'name':name,'type':struct.unpack_from('<i',self.raw,o)[0],
                        'data':struct.unpack_from('<Q',self.raw,o+fields['data']['offset'])[0]})
        return out
    def geometry(self,mesh_ptr):
        nv=self.value(mesh_ptr,'Mesh','totvert','i')[0]
        npoly=self.value(mesh_ptr,'Mesh','totpoly','i')[0]
        nl=self.value(mesh_ptr,'Mesh','totloop','i')[0]
        vl,pl,ll=self.layers(mesh_ptr,'vdata'),self.layers(mesh_ptr,'pdata'),self.layers(mesh_ptr,'ldata')
        pos=next((l for l in vl if l['name']=='position'),None)
        if pos:
            block=self.block(pos['data'],mesh_ptr);assert block['size']>=nv*12
            vertices=np.frombuffer(self.raw,dtype='<f4',count=nv*3,offset=block['start']).reshape(-1,3).copy()
        else:
            ptr=self.value(mesh_ptr,'Mesh','mvert','Q')[0] or next(l['data'] for l in vl if l['type']==0)
            block=self.block(ptr,mesh_ptr);assert block['size']==nv*16,(block,nv)
            vertices=np.ndarray((nv,3),dtype='<f4',buffer=self.raw,offset=block['start'],strides=(16,4)).copy()
        poly_ptr=self.value(mesh_ptr,'Mesh','mpoly','Q')[0] or next(l['data'] for l in pl if l['type']==25)
        block=self.block(poly_ptr,mesh_ptr);assert block['size']==npoly*12
        polys=np.ndarray((npoly,2),dtype='<i4',buffer=self.raw,offset=block['start'],strides=(12,4))
        loop_ptr=self.value(mesh_ptr,'Mesh','mloop','Q')[0] or next(l['data'] for l in ll if l['type']==26)
        block=self.block(loop_ptr,mesh_ptr);assert block['size']==nl*8
        loops=np.ndarray((nl,),dtype='<i4',buffer=self.raw,offset=block['start'],strides=(8,))
        faces=[]
        for start,n in polys:
            face=loops[start:start+n]
            for j in range(1,n-1):faces.append((face[0],face[j],face[j+1]))
        faces=np.asarray(faces,dtype=np.int32)
        assert np.isfinite(vertices).all()
        assert np.abs(vertices).max()<10, 'Anatomical mesh coordinates outside expected meters scale'
        assert faces.min()>=0 and faces.max()<nv
        return vertices,faces

    def curve_info(self,curve_ptr):
        first=self.value(curve_ptr,'Curve','nurb','Q')[0]
        bevel=self.value(curve_ptr,'Curve','ext2','f')[0]
        profile=self.value(curve_ptr,'Curve','bevobj','Q')[0]
        count=points=0;seen=set()
        while first:
            assert first not in seen
            seen.add(first)
            count+=1
            points+=self.value(first,'Nurb','pntsu','i',curve_ptr)[0]
            first=self.value(first,'Nurb','next','Q',curve_ptr)[0]
        return {'splines':count,'control_points':points,'bevel_depth':bevel,'bevel_object':profile,
                'surface_curve':points>=2 and (bevel>0 or profile!=0)}


def main():
    reader=BlendData(ROOT/'fontes/z_anatomy/Startup.blend')
    objects=[];collections=[];obj_by_ptr={}
    for ptr,b in reader.blocks.items():
        if b['code']!=b'OB\0\0':continue
        typ=reader.value(ptr,'Object','type','h')[0]
        data_ptr=reader.value(ptr,'Object','data','Q')[0]
        matrix=np.array(reader.value(ptr,'Object','obmat','16f')).reshape(4,4).T
        row={'name':reader.name(ptr),'type':{0:'EMPTY',1:'MESH',2:'CURVE',4:'FONT'}.get(typ,str(typ)),
             'pointer':ptr,'data_pointer':data_ptr,'matrix_world':matrix.tolist(),'collections':[]}
        if typ==1:
            row.update(vertices=reader.value(data_ptr,'Mesh','totvert','i')[0],polygons=reader.value(data_ptr,'Mesh','totpoly','i')[0],data_name=reader.name(data_ptr))
        elif typ==2:
            row.update(reader.curve_info(data_ptr))
        objects.append(row);obj_by_ptr[ptr]=row
    cols={ptr:b for ptr,b in reader.blocks.items() if b['code']==b'GR\0\0'}
    direct={ptr:reader.linked(ptr,'gobject','CollectionObject','ob') for ptr in cols}
    children={ptr:reader.linked(ptr,'children','CollectionChild','collection') for ptr in cols}
    cache={}
    def all_objects(ptr):
        if ptr not in cache:
            cache[ptr]=set(direct[ptr])
            for child in children[ptr]:cache[ptr].update(all_objects(child))
        return cache[ptr]
    for ptr in cols:
        name=reader.name(ptr)
        for op in direct[ptr]:obj_by_ptr[op]['collections'].append(name)
        meshes=[obj_by_ptr[op]['name'] for op in all_objects(ptr) if obj_by_ptr[op]['type']=='MESH' and obj_by_ptr[op]['polygons']>0]
        curves=[obj_by_ptr[op]['name'] for op in all_objects(ptr) if obj_by_ptr[op].get('surface_curve')]
        collections.append({'name':name,'children':[reader.name(p) for p in children[ptr]],'objects':[obj_by_ptr[p]['name'] for p in direct[ptr]],'meshes':sorted(meshes),'curves':sorted(curves)})
    result={'source':'Startup.blend 3.5; raw SDNA, no script execution','objects':objects,'collections':collections}
    (ROOT/'malhas/z_blend_inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('TOTAL',len(objects),'MESHES',sum(o['type']=='MESH' and o['polygons']>0 for o in objects))
    for c in collections:
        if re.search('heart|pericard|myocardi|cardiac|coronary|valv|chorda|papill|septum|ovalis',c['name'],re.I):print('COLLECTION',c['name'],'MESHES',len(c['meshes']))
    for o in objects:
        if o['type']=='MESH' and re.search('heart|atri|ventri|papill|coronar|pericard|chorda|ovalis|fibrous|sinuatrial|sinoatrial|terminal|sept|valv|cusp',o['name'],re.I):print('MESH',o['name'],o['vertices'],o['polygons'])
    # Export source heart geometry for visual inspection, without generating anatomy.
    heart=next(c for c in collections if c['name']=='Heart')
    names=set(heart['meshes'])
    manifest=[]
    geomdir=ROOT/'malhas/heart_source';geomdir.mkdir(exist_ok=True)
    for o in objects:
        if o['name'] not in names:continue
        vertices,faces=reader.geometry(o['data_pointer'])
        matrix=np.array(o['matrix_world'])
        world=(np.c_[vertices,np.ones(len(vertices))]@matrix.T)[:,:3].astype(np.float32)
        slug=re.sub(r'[^A-Za-z0-9]+','_',o['name']).strip('_')
        np.savez_compressed(geomdir/(slug+'.npz'),vertices=world,faces=faces)
        manifest.append({'name':o['name'],'file':slug+'.npz','vertices':len(vertices),'triangles':len(faces),'min':world.min(0).tolist(),'max':world.max(0).tolist()})
    (geomdir/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('EXPORTED_HEART',len(manifest))

if __name__=='__main__':main()
