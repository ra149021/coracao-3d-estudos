from pathlib import Path
import json,csv,re,zipfile,hashlib

ROOT=Path(__file__).resolve().parents[1]
requirements=json.loads((ROOT/'requisitos.json').read_text())
z=json.loads((ROOT/'malhas/z_blend_inventory.json').read_text())
bp=json.loads((ROOT/'malhas/bp3d_inventory.json').read_text())
zobj={o['name']:o for o in z['objects']}
zgeom={n:o for n,o in zobj.items() if o.get('polygons',0)>0 or o.get('surface_curve')}

# Exact names / anatomical concept IDs are explicitly reviewed mappings.
# Direct geometry is a technical availability result, not specialist validation.
direct = '''16|Right atrium|FMA9457
18|Left atrium|FMA9531
20|Right ventricle|FMA9291
21|Left ventricle|FMA9466
30a|Superior vena cava|FMA4720
30b|Inferior vena cava|FMA10951
30c|Pulmonary trunk|FMA8612
30d|Right pulmonary artery|FMA50872
30e|Left pulmonary artery|FMA50873
30f|Left superior pulmonary vein|FMA49916
30g|Left inferior pulmonary vein|FMA49913
30h|Right superior pulmonary vein|FMA49914
30j|Ascending aorta;Thoracic aorta;Abdominal aorta|FMA3736;FMA3768;FMA87217;FMA3789
30k|Coronary sinus|FMA4706
46a||FMA7238
46b|Inferior leaflet of right atrioventricular valve|FMA7239
46c|Septal leaflet of right atrioventricular valve|FMA7240
47|Anterior papillary muscle of right ventricle|FMA7260
48|Inferior papillary muscle of right ventricle|FMA7261
49|Septal papillary muscle of right ventricle|FMA7262
53a|Anterior semilunar leaflet of pulmonary valve|
53b|Right semilunar leaflet of pulmonary valve|
53c|Left semilunar leaflet of pulmonary valve|
58a||FMA7242
58b|Posterior leaflet of left atrioventricular valve|FMA7243
60|Inferior papillary muscle of left ventricle|
63a|Right coronary leaflet|
63b|Left coronary leaflet|
63c|Non-coronary leaflet|
76|Ascending aorta|FMA3736
81|Right coronary artery|FMA3802
83|Left coronary artery|FMA3855
84||FMA3768
85|Brachiocephalic trunk|
86|Right common carotid artery|FMA3941
87|Right subclavian artery|FMA3953
88|Left common carotid artery|FMA4058
89|Left subclavian artery|FMA4694
90|Internal carotid artery.l;Internal carotid artery.r|
91|External carotid artery.l;External carotid artery.r|
92|Thoracic aorta|FMA87217
93|Abdominal aorta|FMA3789
96||FMA3807
97||FMA3813
98||FMA3818
100||FMA3840
101||FMA3845
102|Right inferolateral branch of right coronary artery|FMA3835
103|Anterior interventricular artery|FMA74912
103a||FMA3868
103b|Septal branches of anterior interventricular artery|FMA3892
103c||FMA3860
104|Circumflex artery of heart|FMA3895
105||FMA66403
106|Great cardiac vein|FMA4707
109||FMA4708
110|Inferior vein of left ventricle (//Posterior '')|FMA4712
111|Middle cardiac vein|FMA4713
112||FMA4716
113||FMA4714
114||FMA76767
116|Musculophrenic artery.l;Musculophrenic artery.r|FMA10645
117||FMA68109
118||FMA4149
119|Superior phrenic arteries|
122a|Azygos vein|FMA4838
122b|Hemi-azygos vein|FMA4944
122c|Accessory hemi-azygos vein|FMA5011
123|Vagus nerve (X).l;Vagus nerve (X).r|
125|Sympathetic trunk.l;Sympathetic trunk.r|
C15|Right inferior pulmonary vein|FMA49911
V42c|Inferior tracheobronchial nodes|
V42d|Paratracheal cervical nodes;Paratracheal thoracic nodes|'''
mapped={}
for line in direct.splitlines():
 rid,zn,bn=line.split('|')
 mapped[rid]={'z_names':[n for n in zn.split(';') if n],'bp_ids':[n for n in bn.split(';') if n]}

# Parent shapes/landmarks plausibly present but requiring isolation, segmentation,
# registration, or further visual checking. All are excluded from confirmed credit.
partial={
 '1':('Right atrium;Right ventricle;Left atrium;Left ventricle','Conferir posição com esterno, diafragma, pulmões e mediastino no modelo corporal.'),
 '2':('Right atrium;Right ventricle;Left atrium;Left ventricle','Sintopia requer a cena torácica; o coração isolado não demonstra todas as relações.'),
 '4b':('Right atrium;Right ventricle;Left atrium;Left ventricle','Superfície externa disponível; lâmina visceral não tem geometria individualizada.'),
 '6':('Right atrium;Right ventricle;Left atrium;Left ventricle','Superfícies internas disponíveis; revestimento endocárdico não está separado.'),
 '7':('Right ventricle;Left ventricle','Face reconhecível no conjunto; falta delimitar e conferir a seleção.'),
 '8':('Right ventricle;Left ventricle','Face reconhecível no conjunto; falta delimitar e conferir a seleção.'),
 '9':('Right atrium','Face depende de delimitação na parede atrial.'),
 '10':('Left ventricle;Left atrium','Face depende de delimitação na superfície.'),
 '11':('Right atrium','Margem é um marco de superfície, não um órgão separado.'),
 '12':('Left ventricle','Margem é um marco de superfície, não um órgão separado.'),
 '13':('Right ventricle;Left ventricle','Margem é um marco de superfície, não um órgão separado.'),
 '14':('Left atrium;Right atrium','Base identificável pela orientação; necessita marcação conferida.'),
 '15':('Left ventricle','Ápice identificável; necessita marcação conferida.'),
 '17':('Right atrium','Aurícula incorporada à parede do átrio; falta conferir e segmentar o limite.'),
 '19':('Left atrium','Aurícula incorporada à parede do átrio; falta conferir e segmentar o limite.'),
 '22':('Right atrium;Left atrium','Septo depende da parede compartilhada; catálogo tem apenas referência.'),
 '23':('Right ventricle;Left ventricle','Parede septal incorporada; falta delimitar e verificar espessura/porções.'),
 '24':('Right atrium;Left ventricle','Região de junção necessita identificação dirigida; sem geometria própria.'),
 '25':('Right atrium;Left atrium','Sulco precisa ser verificado na união das paredes atriais.'),
 '26':('Right ventricle;Left ventricle','Referência do sulco existe; falta validação de marcação na superfície.'),
 '27':('Right ventricle;Left ventricle','Referência do sulco existe; falta validação de marcação na superfície.'),
 '28':('Right atrium;Right ventricle;Left atrium;Left ventricle','Referência do sulco existe; falta validação de marcação na superfície.'),
 '29':('Right atrium;Right ventricle;Left atrium;Left ventricle','Interseção dos sulcos precisa de inspeção posterior e marcação.'),
 '32':('Right atrium','Abertura na parede/tubo disponível; borda não individualizada.'),
 '33':('Right atrium','Abertura na parede/tubo disponível; borda não individualizada.'),
 '34':('Right atrium;Coronary sinus','Continuidade da veia com o átrio precisa ser conferida; não basta a veia existir.'),
 '37':('Right atrium','Parede lisa disponível; limite com a região pectínea não confirmado.'),
 '41':('Right atrium','Possível região septal; a fossa não foi confirmada na amostra de corte.'),
 '43':('Right ventricle','Trato de saída presente na casca; necessita delimitação e inspeção interna.'),
 '45':('Right atrium;Right ventricle','Anel/abertura requer isolamento e conferência do limite.'),
 '51':('Inferior leaflet of right atrioventricular valve;Septal leaflet of right atrioventricular valve','Cordas visíveis, incorporadas aos folhetos. Confirmar a distribuição em cada músculo papilar.'),
 '54a':('Left atrium;Right superior pulmonary vein','Abertura exige conferir a união da veia com a parede do AE.'),
 '54b':('Left atrium;Right inferior pulmonary vein','Abertura exige conferir a união da veia com a parede do AE.'),
 '54c':('Left atrium;Left superior pulmonary vein','Abertura exige conferir a união da veia com a parede do AE.'),
 '54d':('Left atrium;Left inferior pulmonary vein','Abertura exige conferir a união da veia com a parede do AE.'),
 '55':('Left atrium','Região septal disponível; assoalho do forame oval não individualizado.'),
 '57':('Left atrium;Left ventricle','Anel/abertura requer isolamento e conferência do limite.'),
 '59':('','BodyParts3D FMA7265 representa uma cabeça anterolateral; equivalência com o músculo anterior completo precisa de revisão.'),
 '61':('Posterior leaflet of left atrioventricular valve','Cordas visíveis, incorporadas ao folheto. Conferir todas as inserções.'),
 '77':('Ascending aorta','Base da aorta disponível; dilatação correspondente ao seio não individualizada.'),
 '78':('Ascending aorta','Base da aorta disponível; dilatação correspondente ao seio não individualizada.'),
 '79':('Ascending aorta','Base da aorta disponível; dilatação correspondente ao seio não individualizada.'),
 '80':('Ascending aorta;Right coronary artery','Origem dos vasos é indicativa; conexão luminal e óstio não conferidos.'),
 '82':('Ascending aorta;Left coronary artery','Origem dos vasos é indicativa; conexão luminal e óstio não conferidos.'),
 '104b':('Circumflex artery of heart','Ramo lateral da circunflexa não está individualmente nomeado; conferir nomenclatura do roteiro.'),
 '104c':('Circumflex artery of heart','Ramo marginal pode estar incorporado à circunflexa; não individualmente identificado.'),
 '104d':('Circumflex artery of heart','Ramo posterior pode estar incorporado à circunflexa; não individualmente identificado.'),
 'C41':('Left ventricle','Trato de saída exige segmentação e identificação do vestíbulo.'),
 'C45a':('Pulmonary trunk','Raiz do tronco presente; seio pulmonar não individualizado.'),
 'C45b':('Pulmonary trunk','Raiz do tronco presente; seio pulmonar não individualizado.'),
 'C45c':('Pulmonary trunk','Raiz do tronco presente; seio pulmonar não individualizado.'),
 'C47':('Right ventricle;Left ventricle','Parede septal disponível; porção membranácea não individualizada.'),
}

missing_notes={
 '3':'Pericardium/Pericardial sac são coleções vazias; não há saco fibroso reconhecido no inventário.',
 '4a':'Serous pericardium é coleção vazia; lâmina parietal não localizada.',
 '31':'Foi encontrado um linfonodo do ligamento arterial, que não equivale ao ligamento.',
 '35':'Válvula de Eustáquio não localizada como geometria nem reconhecida no corte amostrado.',
 '36':'Válvula de Thebesius não localizada como geometria.',
 '38':'Paredes atriais muito simplificadas; musculatura pectínea não confirmada.',
 '39':'Crista terminal tem descrição, sem objeto anatômico correspondente localizado.',
 '40':'Sulco terminal tem descrição, sem objeto anatômico correspondente localizado.',
 '42':'Limbo da fossa oval não localizado.',
 '44':'Crista supraventricular não localizada como relevo confirmado.',
 '50':'Septomarginal trabecula é coleção vazia; não há banda confirmada entre septo e músculo papilar.',
 '52':'Corte de inspeção mostra parede simplificada, sem rede de trabéculas confirmada.',
 '56':'Válvula do forame oval não localizada.',
 '62':'Corte de inspeção mostra parede simplificada, sem rede de trabéculas confirmada.',
 '74':'Sem reflexões pericárdicas representadas, o espaço transverso não fica delimitado.',
 '75':'Sem reflexões pericárdicas representadas, o fundo de saco oblíquo não fica delimitado.',
 '94':'Artéria do nó sinoatrial não identificada nos ramos disponíveis.',
 '95':'Ramos atriais direitos não identificados individualmente.',
 '99':'Artéria do nó atrioventricular não identificada nos ramos disponíveis.',
 '104a':'Ramos atriais esquerdos não identificados individualmente.',
 '107':'Veia oblíqua do AE não identificada; objeto sem nome confiável não foi creditado.',
 '115':'Artéria pericardicofrênica aparece em descrição, sem geometria correspondente localizada.',
 '121':'Veias pericardicofrênicas não localizadas.',
 '124':'Nervo frênico não localizado como geometria; nervo subclávio e vago não são equivalentes.',
}
for rid in ['5a','5b','5c','5d','5e']:
 missing_notes[rid]='Paredes miocárdicas gerais existem; a camada e sua orientação de fibras exigidas no roteiro não estão representadas.'
for rid in ['64','65','66','67','68','69']:
 missing_notes[rid]='Fibrous skeleton of heart é coleção vazia; anéis e trígonos não possuem representação correspondente localizada.'
for rid in ['70','71','72','73']:
 missing_notes[rid]='Ligamento pericárdico não localizado; Sternopericardial ligaments é coleção vazia.'
for rid in ['C61a','C61b','C66a','C66b','C66c','C66d','C66e','C66f']:
 missing_notes[rid]='Categoria de inervação/condução existe, mas sem geometria para este componente.'

def modeling(row,status):
    n=row['id']
    if status=='geometria_disponivel':return 'Reaproveitar, conferir forma/posição e traduzir a identificação.'
    if status=='parcial_ou_a_conferir':return 'Delimitar ou segmentar a geometria existente e conferir com as figuras docentes.'
    if n.startswith('5'):return 'Criar esquema de camadas/fibras separado; figuras 23–24 não determinam geometria volumétrica realista.'
    if n in ['64','65','66','67','68','69']:return 'Construir o esqueleto fibroso com orientação das valvas; conferir relações nos slides 47–48 e referência adicional.'
    if n in ['3','4a','70','71','72','73','74','75']:return 'Modelar saco, reflexões e/ou fixações com várias vistas; slides 51–58 e fonte adicional para relações ocultas.'
    if n in ['C61a','C61b','C66a','C66b','C66c','C66d','C66e','C66f']:return 'Criar representação didática localizada nos marcos anatômicos; distinguir vias esquemáticas de tecido visível.'
    return 'Buscar referência dirigida; construir apenas quando forma, percurso e relações estiverem sustentados.'

allrows=[]
needed=set()
for row in requirements['alvos']:
    r=dict(row);rid=r['id'];m=mapped.get(rid,{'z_names':[],'bp_ids':[]})
    zn=[n for n in m['z_names'] if n in zgeom]
    bi=[k for k in m['bp_ids'] if k in bp['concepts'] and set(bp['concepts'][k]['elements'])==set(bp['concepts'][k]['available_elements']) and bp['concepts'][k]['elements']]
    for k in bi:needed.update(bp['concepts'][k]['elements'])
    note=''
    if zn or bi:status='geometria_disponivel'
    elif rid in partial:
        status='parcial_ou_a_conferir';names,note=partial[rid];zn=[n for n in names.split(';') if n in zgeom]
        if rid=='59':bi=['FMA7265'];needed.update(bp['concepts']['FMA7265']['elements'])
    else:
        status='nao_localizado';note=missing_notes.get(rid,'Não foi localizada geometria correspondente no acervo examinado.')
    if rid in ['53a','53b','53c','63a','63b','63c']:
        note='Nomes posicionais das cúspides no BodyParts3D diferem do roteiro. Foi priorizada a identificação explícita do Z-Anatomy; conferir orientação antes da integração.'
    if rid in ['46b','48','60','102','110']:
        note='Equivalência terminológica inferior/posterior ou inferolateral/póstero-lateral precisa permanecer documentada.'
    r.update(status=status,z_evidencia=zn,bp_evidencia=bi,observacao=note,validacao_visual='nao_concluida_individualmente',plano_modelo_proprio=modeling(r,status))
    allrows.append(r)

# Inspect exact OBJ files for all mapped concepts, not just names in the tables.
folder=ROOT/'fontes/bp3d/objetos_coracao';folder.mkdir(exist_ok=True)
geometry={}
with zipfile.ZipFile(ROOT/'fontes/bp3d/isa_BP3D_4.0_obj_99.zip') as archive:
    paths={Path(p).stem:p for p in archive.namelist() if p.endswith('.obj')}
    for element in sorted(needed):
        data=archive.read(paths[element]);p=folder/(element+'.obj');p.write_bytes(data)
        lines=data.decode().splitlines();vertices=sum(l.startswith('v ') for l in lines);faces=sum(l.startswith('f ') for l in lines)
        assert vertices>0 and faces>0,(element,vertices,faces)
        geometry[element]={'vertices':vertices,'faces':faces,'sha256':hashlib.sha256(data).hexdigest(),'file':str(p.relative_to(ROOT))}
(ROOT/'malhas/bp3d_mesh_verification.json').write_text(json.dumps(geometry,indent=2))

summary={}
for scope in ['principal','complemento_docente']:
    rows=[r for r in allrows if r['escopo']==scope]
    counts={s:sum(r['status']==s for r in rows) for s in ['geometria_disponivel','parcial_ou_a_conferir','nao_localizado']}
    counts['total']=len(rows)
    counts['disponibilidade_percentual']=round(counts['geometria_disponivel']/len(rows)*100,2)
    counts['potencial_incluindo_parciais_percentual']=round((counts['geometria_disponivel']+counts['parcial_ou_a_conferir'])/len(rows)*100,2)
    summary[scope]=counts
summary['regra_90']='Não satisfeito enquanto a cobertura individual validada não atingir 90%; geometrias disponíveis e parciais ainda exigem conferência anatômica.'
out={'metodo':requirements['metodo'],'resumo':summary,'alvos':allrows}
audit=ROOT/'site/auditoria'
audit.mkdir(parents=True,exist_ok=True)
(audit/'matriz_coracao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
with (audit/'matriz_coracao.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(allrows[0]));writer.writeheader()
    for row in allrows:writer.writerow({k:'; '.join(v) if isinstance(v,list) else v for k,v in row.items()})
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('DIRECT_BUT_MISSING',[(r['id'],mapped[r['id']]) for r in allrows if r['id'] in mapped and r['status']!='geometria_disponivel'])
