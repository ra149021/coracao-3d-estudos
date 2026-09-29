"""Generate curriculum-linked views without changing any mesh or anatomical claim."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
heart=json.loads((ROOT/'site/assets/catalog.json').read_text())
resp=json.loads((ROOT/'site/assets/respiratory/catalog.json').read_text())
views={'circulatory':[],'respiratory':[]}
def add(scope,id,label,ids,targets,doc,page,note,direction,transparency=0):
    known={p['id'] for p in (heart if scope=='circulatory' else resp)['parts']}
    assert set(ids)<=known,(id,set(ids)-known)
    assert ids and len(ids)==len(set(ids)),id
    assert (ROOT/f'site/assets/lectures/slides/{doc}/{page}.jpg').is_file(),(doc,page)
    views[scope].append(dict(id=id,label=label,partIds=ids,requirementIds=targets,source={'document':doc,'page':page},note=note,direction=direction,transparency=transparency))
def h(id,label,ids,targets,page,note,direction,transparency=82):
    add('circulatory',id,label,ids,targets,'coracao',page,note,direction,transparency)
h('av_direita','Tricúspide, cordas e papilares',['heart_01','heart_26','heart_27','bp_FJ2421','heart_35','heart_36','heart_37'],['46a','46b','46c','47','48','49','51'],37,'Parede ventricular translúcida. As cordas integram as cúspides; confira suas inserções no slide.',[-.5,.55,1])
h('av_esquerda','Mitral, cordas e papilares',['heart_03','heart_28','bp_FJ2420','heart_38','bp_FJ2418'],['58a','58b','59','60','61'],39,'O papilar anterolateral é uma porção de cabeça. Cordas e folhetos permanecem unidos na geometria.',[.7,.4,1])
h('atrio_direito','Átrio direito e entradas cavas',['heart_00','heart_10','heart_11','heart_26','heart_27','bp_FJ2421'],['16','32','33','34','35','36','37','38','39','40','41','42'],31,'Observe a relação entre cavas, átrio e tricúspide. Pectíneos, fossa oval e pequenos relevos ainda não estão individualizados.',[-1,.25,.6])
h('atrio_esquerdo','Átrio esquerdo e veias pulmonares',['heart_02','heart_12','heart_13','heart_14','heart_15','heart_28','bp_FJ2420'],['18','54a','54b','54c','54d','55','56'],39,'Vista posterior com as quatro veias. As aberturas e seus limites exigem conferência; a seleção do vaso não identifica o óstio.',[.25,.2,-1])
h('saida_direita','VD e via de saída pulmonar',['heart_01','heart_06','heart_07','heart_32','heart_33','heart_34'],['20','43','44','45','53a','53b','53c'],43,'Compare ventrículo, valva e tronco pulmonar. A crista supraventricular permanece pendente.',[-.45,.3,1])
h('saida_esquerda','VE e via de saída aórtica',['heart_03','heart_04','heart_29','heart_30','heart_31'],['21','63a','63b','63c','C41'],43,'Compare ventrículo, valva e aorta. A transparência permite inspecionar a relação sem deslocar as peças.',[.6,.35,1])
parts=resp['parts']
def rids(reqs):
    return [p['id'] for p in parts if set(p.get('requirementIds',[]))&set(reqs)]
for key,label,lobe,parents,segments,page in [
 ('superior_direito','Lobo superior direito','R138',['R111','R113'],range(119,122),92),
 ('medio_direito','Lobo médio direito','R139',['R111','R118','R114'],range(122,124),92),
 ('inferior_direito','Lobo inferior direito','R140',['R111','R118','R115'],range(124,129),92),
 ('superior_esquerdo','Lobo superior esquerdo','R141',['R112','R116'],range(129,133),93),
 ('inferior_esquerdo','Lobo inferior esquerdo','R142',['R112','R117'],range(133,138),93),
]:
    targets=[f'R{i:03}' for i in segments]
    add('respiratory','arvore_'+key,label+' · brônquios',['resp_trachea']+rids([lobe]+parents+targets),[lobe]+targets,'respiratorio',page,'Siga principal → lobar → segmentar dentro do lobo translúcido. Os limites dos volumes segmentares não estão modelados.',[.3 if 'esquerdo' in key else -.3,.15,1],85)
for side,pt,main,lobes,vessels in [('right','direito','R111',['R138','R139','R140'],['R173','R175']),('left','esquerdo','R112',['R141','R142'],['R174','R176'])]:
    add('respiratory','hilo_'+pt,'Hilo '+pt+' · relações',rids([main]+lobes+vessels),['R151','R152']+vessels,'respiratorio',105 if side=='right' else 106,'Brônquio e vasos proximais do mesmo lado. Nervos, linfáticos e vasos brônquicos não completam esta raiz.',[1 if side=='right' else -1,.15,-.4],82)
add('respiratory','pleura_inspecao','Pleura · inspeção do conjunto',['resp_pleura']+[p['id'] for p in parts if p['group']=='pulmoes']+['resp_diaphragm_node'],['R161','R162','R163','R164','R165','R166','R170','R171','R172'],'respiratorio',118,'Superfície agregada da fonte. Os componentes geométricos não identificam folhetos, reflexões ou recessos anatômicos.',[.7,.15,1],75)
add('respiratory','seios_referencia','Seios frontal e esfenoidal',[p['id'] for p in parts if p['group']=='seios']+['resp_ethmoid_bone','resp_vomer'],['R034','R036','R037','R038','R039'],'respiratorio',34,'Superfícies das cavidades e células etmoidais. Os seios maxilares e as vias de drenagem não estão individualizados nesta vista.',[1,.15,.2],0)
# Reject stale curriculum IDs rather than silently adding coverage.
for scope,items in views.items():
    reqpath='site/auditoria/matriz_coracao.json' if scope=='circulatory' else 'site/assets/respiratory/requirements.json'
    known={r['id'] for r in json.loads((ROOT/reqpath).read_text())['alvos']}
    for item in items:assert set(item['requirementIds'])<=known,(item['id'],set(item['requirementIds'])-known)
(ROOT/'site/assets/study-views.json').write_text(json.dumps(views,ensure_ascii=False,indent=2)+'\n')
print({s:len(v) for s,v in views.items()})
