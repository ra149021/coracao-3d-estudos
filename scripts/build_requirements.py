"""Preserve the lecturer's checklist; expand explicitly compound requirements."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / 'materiais/roteiro_pages.json').read_text())
original = []
for page in pages:
    text = page['text']
    matches = list(re.finditer(r'(?m)^\s*(\d{1,3})\.\s*', text))
    if matches and matches[0].start() > 0 and original and page['page'] == 2:
        original[-1]['texto'] += '\n' + text[:matches[0].start()].strip()
    for i, m in enumerate(matches):
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        original.append({'item': int(m.group(1)), 'pagina': page['page'], 'texto': text[m.end():end].strip()})
assert [r['item'] for r in original] == list(range(1, 126))
(ROOT / 'materiais/roteiro_original.json').write_text(json.dumps(original, ensure_ascii=False, indent=2))

# These labels retain the lecturer's nomenclature. Synonyms are mapped separately.
labels = '''1|Localização do coração in situ
2|Relações de sintopia do coração
3|Pericárdio fibroso
4a|Pericárdio seroso: lâmina parietal
4b|Pericárdio seroso: lâmina visceral (epicárdio)
5a|Miocárdio dos átrios e VD: camada profunda
5b|Miocárdio dos átrios e VD: camada superficial
5c|Miocárdio do VE: camada profunda
5d|Miocárdio do VE: camada média
5e|Miocárdio do VE: camada superficial
6|Endocárdio
7|Face esternocostal
8|Face diafragmática
9|Face pulmonar direita
10|Face pulmonar esquerda
11|Margem direita
12|Margem esquerda
13|Margem inferior
14|Base do coração
15|Ápice do coração
16|Átrio direito
17|Aurícula direita
18|Átrio esquerdo
19|Aurícula esquerda
20|Ventrículo direito
21|Ventrículo esquerdo
22|Septo interatrial
23|Septo interventricular
24|Septo atrioventricular
25|Sulco interatrial
26|Sulco interventricular anterior
27|Sulco interventricular posterior
28|Sulco coronário
29|Cruz do coração (crux cordis)
30a|Veia cava superior
30b|Veia cava inferior
30c|Tronco pulmonar
30d|Artéria pulmonar direita
30e|Artéria pulmonar esquerda
30f|Veia pulmonar esquerda superior
30g|Veia pulmonar esquerda inferior
30h|Veia pulmonar direita superior
30j|Artéria aorta
30k|Seio coronário
31|Ligamento arterial
32|Óstio da veia cava superior
33|Óstio da veia cava inferior
34|Óstio do seio coronário
35|Válvula da veia cava inferior (Eustáquio)
36|Válvula do seio coronário (Thebesius)
37|Parte posterior lisa do átrio direito
38|Músculos pectíneos do átrio direito
39|Crista terminal
40|Sulco terminal
41|Fossa oval
42|Limbo da fossa oval
43|Cone arterial (infundíbulo do VD)
44|Crista supraventricular
45|Óstio atrioventricular direito
46a|Valva tricúspide: válvula anterior
46b|Valva tricúspide: válvula posterior
46c|Valva tricúspide: válvula septal
47|Músculo papilar anterior do VD
48|Músculo papilar posterior do VD
49|Músculo papilar septal do VD
50|Trabécula septomarginal
51|Cordas tendíneas do VD
52|Trabéculas cárneas do VD
53a|Valva pulmonar: válvula semilunar anterior
53b|Valva pulmonar: válvula semilunar direita
53c|Valva pulmonar: válvula semilunar esquerda
54a|Óstio da veia pulmonar direita superior
54b|Óstio da veia pulmonar direita inferior
54c|Óstio da veia pulmonar esquerda superior
54d|Óstio da veia pulmonar esquerda inferior
55|Assoalho do forame oval (vista do AE)
56|Válvula do forame oval
57|Óstio atrioventricular esquerdo
58a|Valva mitral: válvula anterior
58b|Valva mitral: válvula posterior
59|Músculo papilar anterior do VE
60|Músculo papilar posterior do VE
61|Cordas tendíneas do VE
62|Trabéculas cárneas do VE
63a|Valva aórtica: válvula semilunar direita
63b|Valva aórtica: válvula semilunar esquerda
63c|Valva aórtica: válvula semilunar posterior
64|Anel fibroso direito
65|Anel fibroso esquerdo
66|Anel fibroso da valva pulmonar
67|Anel fibroso da valva aórtica
68|Trígono fibroso direito
69|Trígono fibroso esquerdo
70|Ligamento esternopericárdico superior
71|Ligamento esternopericárdico inferior
72|Ligamento pericardicofrênico
73|Ligamento vertebropericárdico
74|Seio transverso do pericárdio
75|Seio oblíquo do pericárdio
76|Parte ascendente da aorta
77|Seio da aorta direito
78|Seio da aorta esquerdo
79|Seio da aorta posterior (não coronário)
80|Óstio da artéria coronária direita
81|Artéria coronária direita
82|Óstio da artéria coronária esquerda
83|Artéria coronária esquerda
84|Arco da aorta
85|Tronco braquiocefálico
86|Artéria carótida comum direita
87|Artéria subclávia direita
88|Artéria carótida comum esquerda
89|Artéria subclávia esquerda
90|Artéria carótida interna
91|Artéria carótida externa
92|Aorta descendente torácica
93|Aorta descendente abdominal
94|Ramo do nó sinoatrial
95|Ramos atriais direitos
96|Ramo do cone arterial da coronária direita
97|Ramo ventricular anterior direito
98|Ramo marginal direito
99|Ramo do nó atrioventricular
100|Ramo interventricular posterior
101|Ramos interventriculares septais da coronária direita
102|Ramo póstero-lateral direito
103|Ramo interventricular anterior
103a|Ramo do cone arterial do ramo interventricular anterior
103b|Ramos interventriculares septais do ramo interventricular anterior
103c|Ramo lateral (diagonal) do ramo interventricular anterior
104|Ramo circunflexo
104a|Ramos atriais esquerdos
104b|Ramo lateral (diagonal) do ramo circunflexo
104c|Ramo marginal esquerdo
104d|Ramo posterior do ventrículo esquerdo
105|Veia interventricular anterior
106|Veia cardíaca magna
107|Veia oblíqua do átrio esquerdo
109|Veia marginal esquerda
110|Veia posterior do ventrículo esquerdo
111|Veia interventricular posterior (cardíaca média)
112|Veia marginal direita
113|Veia cardíaca parva
114|Veias anteriores do ventrículo direito
115|Artéria pericardicofrênica
116|Artéria musculofrênica
117|Artéria bronquial
118|Artéria esofágica
119|Artéria frênica superior
121|Veias pericardicofrênicas
122a|Sistema ázigos: veia ázigos
122b|Sistema ázigos: veia hemiázigos
122c|Sistema ázigos: veia hemiázigos acessória
123|Nervo vago
124|Nervo frênico
125|Troncos simpáticos'''

rows = []
by_number = {r['item']:r for r in original}
for line in labels.splitlines():
    rid, name = line.split('|')
    num = int(re.match(r'\d+', rid)[0])
    page = by_number[num]['pagina']
    if rid.startswith('30') and rid[-1] in 'defghijk': page = 2
    if num <= 31: group = 'Organização, revestimentos e anatomia externa'
    elif num <= 42: group = 'Átrio direito'
    elif num <= 53: group = 'Ventrículo direito'
    elif num <= 56: group = 'Átrio esquerdo'
    elif num <= 63: group = 'Ventrículo esquerdo'
    elif num <= 69: group = 'Esqueleto fibroso'
    elif num <= 75: group = 'Ligamentos e seios pericárdicos'
    elif num <= 93: group = 'Aorta e grandes ramos'
    elif num <= 104: group = 'Artérias coronárias e ramos'
    elif num <= 114: group = 'Veias cardíacas'
    else: group = 'Vasos e nervos do pericárdio'
    rows.append({'id':rid, 'item_original':num, 'estrutura':name, 'fonte':'roteiro', 'pagina':page, 'grupo':group, 'escopo':'principal'})

# Additional explicit cardiac structures in the lecturer's current slides.
# These do not silently change the main checklist denominator.
extras = [
('C15', 'Veia pulmonar direita inferior', 'coracao', 15),
('C21', 'Músculos pectíneos da aurícula esquerda', 'coracao', 38),
('C41', 'Vestíbulo da aorta', 'coracao', 41),
('C45a', 'Seio pulmonar anterior', 'coracao', 45),
('C45b', 'Seio pulmonar direito', 'coracao', 45),
('C45c', 'Seio pulmonar esquerdo', 'coracao', 45),
('C47', 'Parte membranácea do septo interventricular', 'coracao', 47),
('C61a', 'Plexo cardíaco superficial', 'coracao', 61),
('C61b', 'Plexo cardíaco profundo', 'coracao', 61),
('C66a', 'Nó sinoatrial', 'coracao', 66),
('C66b', 'Nó atrioventricular', 'coracao', 66),
('C66c', 'Fascículo atrioventricular (His)', 'coracao', 66),
('C66d', 'Ramo direito do fascículo atrioventricular', 'coracao', 66),
('C66e', 'Ramo esquerdo do fascículo atrioventricular', 'coracao', 66),
('C66f', 'Fibras de Purkinje', 'coracao', 66),
('V36', 'Veias cardíacas mínimas', 'vasos', 36),
('V42a', 'Plexo linfático superficial (subepicárdico)', 'vasos', 42),
('V42b', 'Plexo linfático profundo (subendocárdico)', 'vasos', 42),
('V42c', 'Linfonodos traqueobronquiais inferiores', 'vasos', 42),
('V42d', 'Linfonodos paratraqueais', 'vasos', 42),
('V42e', 'Ducto linfático direito', 'vasos', 42),
('V42f', 'Ducto torácico', 'vasos', 42),
]
for rid,name,source,page in extras:
    rows.append({'id':rid, 'item_original':None, 'estrutura':name, 'fonte':source, 'pagina':page, 'grupo':'Detalhes adicionais dos slides', 'escopo':'complemento_docente'})

rules = {
 'base':'Roteiro de Circulatório 3, autoria Carmem, 125 itens numerados, 5 páginas.',
 'expansao':'Desdobradas lâminas, cinco camadas miocárdicas nomeadas, vasos da base, folhetos valvares, quatro óstios pulmonares, ramos coronários e três veias principais do sistema ázigos. As cinco camadas mantêm os grupos escritos pela professora; camada dos átrios/VD só é completa se ambos estiverem representados.',
 'duplicatas':{'30i':'repete literalmente a veia pulmonar direita superior de 30h; não contado novamente. A inferior direita está no complemento C15.', '108':'repete o seio coronário de 30k', '120':'repete as coronárias de 81 e 83; a relação com o epicárdio fica na observação'},
 'informacao_sem_geometria':'Peso e diâmetro do item 1 são dados de texto, fora do denominador geométrico; localização e sintopia permanecem como dois alvos espaciais.',
 'limiar':'Aprovação exige ao menos 90% de alvos principais demonstrados em 3D. Alvo parcial, nome sem geometria ou associação presumida não é confirmação. Complementos dos slides têm subtotal próprio.',
 'terminologia':'Manter nomes do roteiro e registrar equivalências. Não corrigir silenciosamente a repetição 30i, nem a alegação de parte membranácea do septo interatrial no slide 47; esta última exige revisão e não foi criada como estrutura 3D adicional.',
 'fora_do_escopo':'Não incluir circulação fetal completa, sistemas porta, histologia ou outros órgãos como novos requisitos cardíacos; preservar o contexto dos slides.'
}
(ROOT/'requisitos.json').write_text(json.dumps({'metodo':rules,'alvos':rows},ensure_ascii=False,indent=2))
print(json.dumps({'originais':len(original),'alvos_principais':sum(r['escopo']=='principal' for r in rows),'adicionais_slides':len(extras)},ensure_ascii=False))
