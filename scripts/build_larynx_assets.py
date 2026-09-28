"""Create a coherent, independent BodyParts3D larynx atlas from original OBJ.

No attempt to fuse these fine tissues with the differently edited Z-Anatomy
laryngeal cartilages. All original BP coordinates receive one display transform.
"""
from pathlib import Path
import hashlib
import json
import struct
import zipfile
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/larynx'
DOC = ROOT / 'refinamento/respiratorio/geometria'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'refinamento/geometria'))
from register_bp3d import validate
from build_respiratory_assets import normal_array

GROUPS = {'cartilagens':'Cartilagens da laringe','musculos':'Músculos laríngeos',
          'ligamentos':'Ligamentos','membranas':'Membranas e cone elástico',
          'vocais':'Músculos e ligamentos vocais','hioide':'Osso hioide','contexto':'Traqueia · contexto'}
COLORS = {'cartilagens':'#bdc8bb','musculos':'#b26d69','ligamentos':'#e6d5b4',
          'membranas':'#d4c8a6','vocais':'#dfc3a7','hioide':'#d8cdb8','contexto':'#d4bba1'}
PARTS = []


def add(fma, elements, label, group, requirement_ids=(), note='', related=()):
    PARTS.append(dict(fma=fma,elements=elements,label=label,group=group,requirementIds=list(requirement_ids),
                      relatedRequirementIds=list(related),note=note or 'Peça original BodyParts3D, preservada no conjunto anatômico da própria fonte.'))


add('FMA9615',['FJ2769'],'Cartilagem cricóidea','cartilagens',['R072'],related=['R073','R074','R075','R076'])
add('FMA55099',['FJ2808'],'Cartilagem tireóidea','cartilagens',['R061'],related=['R062','R063','R064','R065','R066','R067','R068','R075'])
add('FMA55130',['FJ2770'],'Epiglote','cartilagens',['R079'],
    'Superfície denominada epiglote na fonte; não individualiza todas as camadas do órgão.',related=['R080','R083','R084','R222'])
add('FMA52749',['FJ2772'],'Osso hioide','hioide',['R217'])
for fma,element,label,group,req in [
    ('FMA55114','FJ2775','Cartilagem aritenóidea · lado esquerdo','cartilagens','R085'),
    ('FMA55113','FJ2792','Cartilagem aritenóidea · lado direito','cartilagens','R085'),
    ('FMA55116','FJ2776','Cartilagem corniculada · lado esquerdo','cartilagens','R088'),
    ('FMA55115','FJ2793','Cartilagem corniculada · lado direito','cartilagens','R088'),
    ('FMA55118','FJ2773','Cartilagem cuneiforme · lado esquerdo','cartilagens','R089'),
    ('FMA55117','FJ2795','Cartilagem cuneiforme · lado direito','cartilagens','R089'),
    ('FMA46581','FJ2778','Músculo cricoaritenóideo lateral · lado esquerdo','musculos','R093'),
    ('FMA46580','FJ2796','Músculo cricoaritenóideo lateral · lado direito','musculos','R093'),
    ('FMA46585','FJ2780','Músculo aritenóideo oblíquo · lado esquerdo','musculos','R091'),
    ('FMA46584','FJ2798','Músculo aritenóideo oblíquo · lado direito','musculos','R091'),
    ('FMA46578','FJ2782','Músculo cricoaritenóideo posterior · lado esquerdo','musculos','R097'),
    ('FMA46577','FJ2800','Músculo cricoaritenóideo posterior · lado direito','musculos','R097'),
    ('FMA46612','FJ2783','Músculo cricotireóideo · parte reta esquerda','musculos','R090'),
    ('FMA46611','FJ2801','Músculo cricotireóideo · parte reta direita','musculos','R090'),
    ('FMA46614','FJ2781','Músculo cricotireóideo · parte oblíqua esquerda','musculos','R090'),
    ('FMA46613','FJ2799','Músculo cricotireóideo · parte oblíqua direita','musculos','R090'),
    ('FMA46593','FJ2788','Músculo vocal · lado esquerdo','vocais','R096'),
    ('FMA46592','FJ2806','Músculo vocal · lado direito','vocais','R096'),
    ('FMA55134','FJ2786','Membrana tireo-hióidea · lado esquerdo','membranas','R069'),
    ('FMA55133','FJ2804','Membrana tireo-hióidea · lado direito','membranas','R069'),
    ('FMA55141','FJ2779','Ligamento tireo-hióideo lateral · lado esquerdo','ligamentos','R071'),
    ('FMA55140','FJ2797','Ligamento tireo-hióideo lateral · lado direito','ligamentos','R071'),
]: add(fma,[element],label,group,[req])
add('FMA46590',['FJ2784','FJ2785'],'Músculo tireoaritenóideo · lado esquerdo','musculos',['R094'],
    'Dois elementos da fonte pertencem ao mesmo conceito tireoaritenóideo; agrupados sem duplicar triângulos.',related=['R095'])
add('FMA46589',['FJ2802','FJ2803'],'Músculo tireoaritenóideo · lado direito','musculos',['R094'],
    'Dois elementos da fonte pertencem ao mesmo conceito tireoaritenóideo; agrupados sem duplicar triângulos.',related=['R095'])
add('FMA46605',['FJ2774'],'Músculo ariepiglótico · lado esquerdo','musculos')
add('FMA46604',['FJ2791'],'Músculo ariepiglótico · lado direito','musculos')
add('FMA46582',['FJ2809'],'Músculo aritenóideo transverso','musculos',['R092'])
add('FMA55138',['FJ2790'],'Ligamento tireo-hióideo mediano','ligamentos',['R070'])
add('FMA55237',['FJ2789'],'Ligamento cricotireóideo mediano','ligamentos',['R077'])
add('FMA55227',['FJ2771'],'Ligamento hioepiglótico','ligamentos',['R082'])
add('FMA55230',['FJ2807'],'Ligamento tireoepiglótico','ligamentos',['R081'])
add('FMA55246',['FJ2787'],'Ligamento vocal · lado esquerdo','vocais',
    note='Componente ligamentar da prega vocal. Não representa a prega inteira nem seu revestimento mucoso.',related=['R099','R102'])
add('FMA55245',['FJ2805'],'Ligamento vocal · lado direito','vocais',
    note='Componente ligamentar da prega vocal. Não representa a prega inteira nem seu revestimento mucoso.',related=['R099','R102'])
add('FMA55252',['FJ2777'],'Cone elástico · lado esquerdo','membranas',
    note='Membrana fibroelástica original da fonte. O cone e o ligamento vocal têm peças próprias; a mucosa não está separada.',related=['R099','R103'])
add('FMA55251',['FJ2794'],'Cone elástico · lado direito','membranas',
    note='Membrana fibroelástica original da fonte. O cone e o ligamento vocal têm peças próprias; a mucosa não está separada.',related=['R099','R103'])
add('FMA7394',['FJ2541'],'Traqueia · contexto','contexto',related=['R104','R105','R106','R107','R108','R109','R110'])


def main():
    concepts = json.loads((ROOT/'malhas/bp3d_inventory.json').read_text())['concepts']
    requirements = {r['id']:r for r in json.loads((ROOT/'site/assets/respiratory/requirements.json').read_text())['alvos']}
    archive = zipfile.ZipFile(ROOT/'fontes/bp3d/isa_BP3D_4.0_obj_99.zip')
    members = {Path(name).stem:name for name in archive.namelist() if name.endswith('.obj')}
    expected_elements = [element for p in PARTS for element in p['elements']]
    assert len(set(expected_elements)) == len(expected_elements), 'Duplicated source anatomy.'
    raw_geometry = []
    for spec in PARTS:
        points,indices,offset,hashes=[],[],0,{}
        for element in spec['elements']:
            assert element in concepts[spec['fma']]['available_elements'], (element,spec['fma'])
            raw=archive.read(members[element]); hashes[element]=hashlib.sha256(raw).hexdigest()
            v,f=[],[]
            for line in raw.decode().splitlines():
                fields=line.split()
                if fields and fields[0]=='v': v.append([float(n) for n in fields[1:4]])
                elif fields and fields[0]=='f':
                    face=[int(n.split('/')[0])-1 for n in fields[1:]]
                    for j in range(1,len(face)-1): f.append([face[0],face[j],face[j+1]])
            v,inverse=np.unique(np.array(v),axis=0,return_inverse=True)
            f=inverse[np.array(f)].astype('<u4')
            points.append(v);indices.append(f+offset);offset+=len(v)
        raw_geometry.append((spec,np.concatenate(points),np.concatenate(indices),hashes))
    # Centre the laryngeal assembly only; the optional trachea retains its place.
    anatomy=np.concatenate([v for spec,v,f,h in raw_geometry if spec['group']!='contexto'])
    rotated=anatomy[:,[0,2,1]]*[1,1,-1]
    center=(rotated.min(0)+rotated.max(0))/2;scale=.1
    geometry,audit=[],[]
    for spec,original,faces,hashes in raw_geometry:
        vertices=((original[:,[0,2,1]]*[1,1,-1]-center)*scale).astype('<f4')
        normals,fallbacks=normal_array(vertices,faces)
        assert np.isfinite(vertices).all() and np.isfinite(normals).all()
        assert faces.max()<len(vertices) and np.allclose(np.linalg.norm(normals,axis=1),1,atol=1e-6)
        report=validate(original,faces)
        assert report['finite']
        exact_areas=np.linalg.norm(np.cross(original[faces[:,1]]-original[faces[:,0]], original[faces[:,2]]-original[faces[:,0]]),axis=1)
        report['exact_zero_area_triangles']=int((exact_areas==0).sum())
        # Preserve even the author's zero-area faces. They do not add visible
        # surface and are recorded explicitly instead of silently repairing anatomy.
        meta=dict(spec,id='larynx_'+spec['fma'].lower(),sourceName=concepts[spec['fma']]['name'],
                  source='BodyParts3D 4.0',license='CC BY 4.0',sourceFile='isa_BP3D_4.0_obj_99.zip',
                  color=COLORS[spec['group']],tissueColor=COLORS[spec['group']],
                  defaultVisible=spec['group'] in ['cartilagens','hioide'],quizEligible=spec['group']!='contexto',
                  vertices=len(vertices),triangles=len(faces),bounds=[vertices.min(0).tolist(),vertices.max(0).tolist()],
                  sourceHashes=hashes,requirement=None)
        if 'vocalis' in meta['sourceName']:
            meta['color']=meta['tissueColor']='#b97c75'
        elif 'vocal ligament' in meta['sourceName']:
            meta['color']=meta['tissueColor']='#eedfbc'
        if spec['requirementIds']:
            req=requirements[spec['requirementIds'][0]]
            meta['requirement']={'id':req['id'],'label':req['estrutura'],'page':req['pagina'],'source':req['fonte']}
        geometry.append((meta,vertices,normals,faces))
        audit.append({'id':meta['id'],'elements':spec['elements'],'source_hashes':hashes,'validation':report,'normal_fallbacks':fallbacks})
    g={'asset':{'version':'2.0','generator':'Coherent original BodyParts3D larynx; no fusion with Z-Anatomy',
                'copyright':'BodyParts3D, © The Database Center for Life Science, CC BY 4.0'},
       'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'accessors':[],'bufferViews':[],'buffers':[]}
    binary=bytearray()
    def put(array,kind,component,target):
        while len(binary)%4:binary.append(0)
        start=len(binary);binary.extend(array.tobytes());view=len(g['bufferViews'])
        g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':array.nbytes,'target':target})
        index=len(g['accessors']);entry={'bufferView':view,'componentType':component,'count':len(array),'type':kind}
        if kind=='VEC3':entry.update(min=array.min(0).tolist(),max=array.max(0).tolist())
        g['accessors'].append(entry);return index
    for i,(meta,v,n,f) in enumerate(geometry):
        pos=put(v,'VEC3',5126,34962);nor=put(n,'VEC3',5126,34962);ind=put(f.flatten(),'SCALAR',5125,34963)
        color=[int(meta['color'][j:j+2],16)/255 for j in (1,3,5)]
        g['materials'].append({'name':meta['label'],'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':color+[1],'metallicFactor':0,'roughnessFactor':.8}})
        g['nodes'].append({'name':meta['id'],'mesh':i,'extras':{'partId':meta['id']}})
        g['meshes'].append({'name':meta['sourceName'],'primitives':[{'attributes':{'POSITION':pos,'NORMAL':nor},'indices':ind,'material':i,'mode':4}]})
        g['scenes'][0]['nodes'].append(i)
    g['buffers'].append({'byteLength':len(binary)})
    encoded=json.dumps(g,ensure_ascii=False,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
    blob=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
    (OUT/'model.glb').write_bytes(blob)
    catalog=dict(version=1,system='larynx',parentSystem='respiratory',title='Laringe em detalhe',
                 description='Alternativa anatômica BodyParts3D; modelo independente.',
                 parts=[x[0] for x in geometry],groups=GROUPS,
                 model={'file':'model.glb','bytes':len(blob),'parts':len(geometry),'triangles':sum(len(x[3]) for x in geometry),'sha256':hashlib.sha256(blob).hexdigest()},
                 translucencyGroups=['cartilagens','membranas'],labelGroups=['cartilagens','vocais'],mainGroups=['cartilagens','musculos','ligamentos','membranas','vocais','hioide'],
                 presets=[
                     {'id':'exterior','label':'Cartilagens','groups':['cartilagens','hioide'],'direction':[.5,.1,1],'transparency':0,'note':'Orientação pelas cartilagens e osso hioide, no conjunto original BodyParts3D.'},
                     {'id':'profunda','label':'Estruturas internas','groups':['cartilagens','musculos','ligamentos','membranas','vocais','hioide'],'direction':[.7,.35,1],'transparency':72,'note':'Componentes internos da mesma fonte, sem adaptação às cartilagens Z-Anatomy.'},
                     {'id':'vocais','label':'Componentes vocais','groups':['cartilagens','vocais','membranas'],'direction':[0,1,.3],'transparency':86,'note':'Músculos e ligamentos vocais são componentes; o revestimento da prega vocal completa não está segmentado.'},
                     {'id':'posterior','label':'Músculos · vista posterior','groups':['cartilagens','musculos','vocais'],'direction':[0,.1,-1],'transparency':65,'note':'Observe o conjunto muscular pelas relações posteriores preservadas na fonte.'},
                     {'id':'ligamentos','label':'Membranas e ligamentos','groups':['cartilagens','hioide','ligamentos','membranas','vocais'],'direction':[.8,.2,1],'transparency':68,'note':'Tireo-hióidea, cone elástico e ligamentos são peças distintas quando nomeados assim na fonte.'},
                 ],
                 orientation={'x':'esquerda anatômica','y':'superior','z':'anterior','transform':{'axisMap':'[x,z,-y]','sourceUnits':'mm','center':center.tolist(),'scale':scale},'preserved':'Uma transformação comum de exibição; sem registro ao Z-Anatomy.'},
                 limitations=[
                     'Alternativa anatômica BodyParts3D; modelo independente. Não sobrepor aos tecidos Z-Anatomy.',
                     'Cores didáticas; superfícies idealizadas da distribuição original BP3D 4.0 com redução de polígonos.',
                     'Ligamento vocal e músculo vocal não equivalem sozinhos à prega vocal completa.',
                     'Não há pregas vestibulares, mucosa ou cavidades laríngeas individualizadas como superfícies próprias.',
                     'Registro experimental ao Z apresentou divergências milimétricas e foi rejeitado para fusão das peças finas.',
                 ],
                 sources=[{'name':'BodyParts3D, © The Database Center for Life Science','license':'CC BY 4.0','url':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html'},
                          {'name':'Licença oficial BodyParts3D','license':'CC BY 4.0','url':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html'}])
    (OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
    (DOC/'larynx_mesh_audit.json').write_text(json.dumps({'source_elements_unique':len(expected_elements),'parts':audit,'display_transform':catalog['orientation']},ensure_ascii=False,indent=2))
    print(json.dumps(catalog['model'],indent=2))


if __name__=='__main__':main()
