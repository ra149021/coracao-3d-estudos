"""Prepare a separate HRA heart atlas, keeping source topology and relative anatomy.

The only geometric operation is one common translation + positive uniform scale.
No tissue, leaflet, conduction path or anatomical texture is generated.
"""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from inspect_hra import read_glb,ROOT,SOURCE
OUT=ROOT/'site/assets/heart-hra'
OUT.mkdir(parents=True,exist_ok=True)
DOC=Path(__file__).parent
source_url='https://3d.nih.gov/entries/3DPX-021000'
license_url='https://creativecommons.org/licenses/by/4.0/'
# id, label, group, requirements represented as a whole, related requirements, quiz, note
rows=[
 ('hra_mitral','Valva mitral · conjunto','valvas',[],['58a','58b','57','61'],True,'Valva inteira na fonte; os dois folhetos e suas cordas não são peças independentes. Não identificar folhetos específicos apenas pela seleção desta malha.'),
 ('hra_tricuspid','Valva tricúspide · conjunto','valvas',[],['46a','46b','46c','45','51'],True,'Valva inteira na fonte; três folhetos não individualizados. Forma simplificada; cordas e inserções não foram validadas.'),
 ('hra_aortic','Valva aórtica · conjunto','valvas',[],['63a','63b','63c'],True,'Conjunto valvar simplificado. Selecionar esta peça não individualiza as cúspides direita, esquerda e posterior.'),
 ('hra_pulmonary','Valva pulmonar · conjunto','valvas',[],['53a','53b','53c'],True,'Conjunto valvar simplificado. Selecionar esta peça não individualiza as cúspides anterior, direita e esquerda.'),
 ('hra_papillary_anterior','Peça papilar anterior · identificação em revisão','papilares',[],['47','59'],False,'O nome do nó diz anterior, mas o rótulo interno diz ventrículo esquerdo. A localização parece relacionada ao VD; a divergência impede usá-la como resposta de prova até revisão anatômica.'),
 ('hra_papillary_anterolateral','Peça papilar anterolateral do VE · porção','papilares',[],['59'],False,'A fonte descreve uma cabeça anterolateral, não o músculo anterior completo. Os identificadores FMA nos metadados divergem; peça excluída do treino.'),
 ('hra_papillary_septal','Peça papilar septal do VD','papilares',[],['49'],False,'Pequena representação papilar nomeada na fonte. Relação com cordas e completude ainda não conferidas; mantida para exploração e fora do treino.'),
 ('hra_papillary_posterior','Peça papilar posterior do VD','papilares',[],['48'],False,'Nome anatômico da fonte preservado, mas os campos de identificador FMA divergem. Mantida para exploração e fora do treino até revisão.'),
 ('hra_papillary_posteromedial','Peça papilar posteromedial do VE · porção','papilares',[],['60'],False,'A fonte descreve uma cabeça posteromedial. Não corresponde automaticamente ao músculo posterior inteiro; mantida fora do treino.'),
 ('hra_left_atrium','Átrio esquerdo','camaras',['18'],['19','22','54a','54b','54c','54d','55','56'],True,'Parede atrial da fonte HRA. Aurícula e óstios não são peças selecionáveis independentes; relevos finos não foram validados.'),
 ('hra_right_atrium','Átrio direito','camaras',['16'],['17','22','32','33','34','35','36','37','38','39','41','42'],True,'Parede atrial da fonte HRA. Aurícula e relevos internos estão incorporados ou simplificados; não equivalem a alvos confirmados separados.'),
 ('hra_right_ventricle','Ventrículo direito','camaras',['20'],['43','44','45','50','52'],True,'Parede ventricular com interior simplificado. Não demonstra de modo validado toda a trabeculação nem a trabécula septomarginal.'),
 ('hra_interventricular_septum','Septo interventricular','septos',['23'],['C47'],True,'Peça separada da própria fonte, entre os ventrículos. Permite selecionar o septo; sua porção membranácea não está individualizada nem validada.'),
 ('hra_left_ventricle','Ventrículo esquerdo','camaras',['21'],['15','57','62'],True,'Parede ventricular da mesma fonte. Não individualiza camadas de fibras, endocárdio, trabéculas ou detalhes valvares finos.')
]
g,data=read_glb()
assert len(data)==len(rows)==14
original=SOURCE.read_bytes();jlen,jtype=struct.unpack_from('<II',original,12);boff=20+jlen;blen,btype=struct.unpack_from('<II',original,boff)
buf=bytearray(original[boff+8:boff+8+blen])
vertices=np.concatenate([d['vertices'] for d in data]).astype(np.float64)
center=(vertices.min(0)+vertices.max(0))/2
scale=4.0/np.ptp(vertices,axis=0).max()
requirements={r['id']:r for r in json.loads((ROOT/'matriz_coracao.json').read_text())['alvos']}
parts=[];newnodes=[];stats=[]
for i,(d,row) in enumerate(zip(data,rows)):
 pid,label,group,req,related,eligible,note=row
 node=next(n for n in g['nodes'] if n.get('mesh')==i)
 oldname=node['name'];extras=node.get('extras',{})
 positions=((d['vertices'].astype(np.float64)-center)*scale).astype('<f4')
 index=g['meshes'][i]['primitives'][0]['attributes']['POSITION'];a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
 assert v.get('byteStride',12)==12 and a['componentType']==5126
 offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 buf[offset:offset+positions.nbytes]=positions.tobytes()
 a['min']=positions.min(0).tolist();a['max']=positions.max(0).tolist()
 g['meshes'][i]['name']=pid
 newnodes.append({'mesh':i,'name':pid,'extras':dict(extras,partId=pid,sourceName=oldname)})
 part={'id':pid,'label':label,'group':group,'sourceName':oldname,'sourceLabel':extras.get('label'),
       'source':'Human Reference Atlas / NIH 3D · Visible Human Male','sourceFile':'VH_M_Heart.glb','sourceUrl':source_url,
       'license':'CC BY 4.0','licenseUrl':license_url,'note':note,'requirementIds':req,'relatedRequirementIds':related,
       'quizEligible':eligible,'correspondence':'associated' if req else 'partial',
       'vertices':len(positions),'triangles':len(d['faces']),'bounds':[a['min'],a['max']],
       'color':{'camaras':'#b97870','valvas':'#dac8a5','papilares':'#ae7665','septos':'#a86e64'}[group],
       'sourceAliases':[extras.get('label','')],'defaultVisible':True}
 if req:
  r=requirements[req[0]];part['requirement']={'id':r['id'],'label':r['estrutura'],'page':r['pagina'],'source':r['fonte']}
 parts.append(part)
 faces=d['faces'];assert faces.max()<len(positions) and np.isfinite(positions).all()
 # Numerical inspection of source topology. No topological repair is applied.
 twice_area=np.linalg.norm(np.cross(d['vertices'][faces[:,1]]-d['vertices'][faces[:,0]],d['vertices'][faces[:,2]]-d['vertices'][faces[:,0]]),axis=1)
 reconstructed=positions.astype(np.float64)/scale+center
 stats.append({'id':pid,'sourceName':oldname,'triangles':len(faces),'vertices':len(positions),
               'maxReconstructionErrorSourceUnits':float(np.abs(reconstructed-d['vertices']).max()),
               'degenerateFacesAreaZero':int(np.count_nonzero(twice_area==0)),
               'originalLabel':extras.get('label'),'originalOntologyId':extras.get('ontologyid'),
               'originalRepresentationOf':extras.get('representation_of')})
g['nodes']=newnodes;g['scenes']=[{'name':'HRA heart · independent source','nodes':list(range(14))}];g['scene']=0
g['asset']['copyright']='Human Reference Atlas / Visible Human Male. NIH 3DPX-021000. CC BY 4.0.'
g['asset']['extras']={'derivedFrom':source_url,'license':license_url,'changes':'Common translation and positive uniform scaling for display; node names translated in separate catalog; source topology and normals preserved.'}
g['buffers'][0]['byteLength']=len(buf)
js=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4);bb=bytes(buf)+b'\0'*((-len(buf))%4)
glb=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(bb))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(bb),0x004E4942)+bb
(OUT/'model.glb').write_bytes(glb)
transform={'formula':'display = (source - center) * scale','center':center.tolist(),'scale':scale,
           'axisMap':'[x,y,z]','sourceUnits':'metres by glTF convention; specimen dimensions not independently calibrated','displayUnits':'normalized; longest extent 4'}
limitations=[
 'Acervo HRA independente: 14 peças desta fonte; não são 14 novas estruturas confirmadas no roteiro principal.',
 'Modelo de referência simplificado, sem textura fotográfica. Sua principal contribuição é o septo interventricular selecionável.',
 'As quatro valvas são conjuntos; seus folhetos e cordas não são peças independentes.',
 'Cinco peças papilares ficam fora do treino por nomenclatura ambígua, representação parcial ou relação com cordas ainda não conferida.',
 'Pericárdio, esqueleto fibroso e sistema de condução não estão presentes.',
 'A porção membranácea do septo, trabeculação fina, crista terminal e outros pequenos relevos não foram validados.',
 'Mesma transformação aplicada a todas as peças; não houve registro, fusão ou substituição do modelo Z-Anatomy/BodyParts3D.'
]
catalog={'version':'heart-hra-1.0-2026-09-28','title':'Câmaras e septo · outro acervo','parts':parts,
 'groups':{'camaras':'Câmaras cardíacas','septos':'Septo interventricular','valvas':'Valvas · conjuntos','papilares':'Peças papilares · em revisão'},
 'labelGroups':['camaras','septos'],
 'model':{'parts':14,'triangles':sum(len(d['faces']) for d in data),'vertices':sum(len(d['vertices']) for d in data),
          'bytes':len(glb),'sha256':hashlib.sha256(glb).hexdigest(),'sourceSha256':hashlib.sha256(original).hexdigest(),
          'sourceEntry':'3DPX-021000','sourceVersion':'1.01','sourceModelVersion':'heart-male/v1.2','individually_anatomically_validated':False,'synthetic_anatomical_parts':0,'photoTexture':False,'quizEligibleParts':sum(p['quizEligible'] for p in parts)},
 'orientation':{'x':'esquerda anatômica','y':'superior','z':'anterior','transform':transform,'preserved':'Uma transformação comum; topologia e relações espaciais originais preservadas.'},
 'presets':[
  {'id':'exterior','label':'Conjunto','groups':['camaras','septos','valvas','papilares'],'direction':[0,0.2,1],'note':'Outro acervo HRA · anatomia simplificada, sem fotografia de tecido.'},
  {'id':'interior','label':'Abrir câmaras','groups':['camaras','septos','valvas','papilares'],'direction':[0,0.1,1],'clipping':True,'note':'Corte visual das câmaras. O septo tem seleção própria.'},
  {'id':'septo','label':'Septo','groups':['septos'],'direction':[0.9,0.1,0.7],'note':'Septo interventricular isolado. A parte membranácea não está individualizada.'},
  {'id':'valvas','label':'Valvas','groups':['valvas','papilares'],'direction':[0.1,1,0.3],'note':'Valvas inteiras e peças papilares da fonte; nomenclatura papilar em revisão.'}
 ],'limitations':limitations,
 'sources':[{'label':'Human Reference Atlas · NIH 3DPX-021000','url':source_url},
            {'label':'HRA · heart-male v1.2','url':'https://purl.humanatlas.io/ref-organ/heart-male/v1.2'},
            {'label':'Licença CC BY 4.0','url':license_url},
            {'label':'NLM · Visible Human Project','url':'https://www.nlm.nih.gov/research/visible/visible_human.html'}]}
(OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
inspection={'source':{'entry':source_url,'download':'https://3d.nih.gov/api/download?submissionId=29114&fileIds=741932','license':license_url,'sourceBytes':len(original),'sourceSha256':hashlib.sha256(original).hexdigest()},'transform':transform,'topologyPreserved':True,'verticesMovedOnlyByCommonTransform':True,'meshes':stats,'images':len(g.get('images',[])),'textures':len(g.get('textures',[])),'visualInspection':'Six matplotlib views reviewed; simplified chambers/valves and separate interventricular septum; no browser validation in this preparation.'}
(DOC/'hra_inspection.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2)+'\n')
(OUT/'ATTRIBUTION.md').write_text('''# Heart HRA — fonte e atribuição\n\nHuman Reference Atlas (HRA), modelo heart-male v1.2, baseado no Visible Human Male/National Library of Medicine, distribuído pela entrada NIH 3DPX-021000, versão 1.01.\n\n- Fonte: https://3d.nih.gov/entries/3DPX-021000\n- Referência: https://purl.humanatlas.io/ref-organ/heart-male/v1.2\n- Licença da entrada: Creative Commons Attribution 4.0 — https://creativecommons.org/licenses/by/4.0/\n- Créditos do projeto HRA: https://humanatlas.io/3d-reference-library\n\nAlterações nesta cópia: uma translação e uma escala uniforme comuns a todas as malhas para exibição; nomes de seleção e catálogo em português; metadados de correspondência e limitações. Topologia, normais e relações espaciais preservadas. Nenhuma estrutura anatômica criada, deformada ou fundida ao acervo principal. Cores do visualizador são didáticas, sem textura fotográfica. Sem endosso do NIH ou da HRA.\n\nO rótulo interno da peça papilar anterior conflita com sua posição/nome. Outras porções papilares têm identificação parcial ou metadados FMA divergentes. As cinco peças papilares estão fora do treino nesta edição.\n''')
print(json.dumps(catalog['model'],indent=2));print('output',OUT)
