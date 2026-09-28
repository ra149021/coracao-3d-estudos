# Próximas estruturas — etapa prática do coração

## Leitura do estado atual

Snapshot do catálogo: **55 peças**, associadas diretamente a **53 IDs** dos 178 alvos. Os outros **125 IDs** incluem regiões já incorporadas às câmaras, conjuntos vasculares ainda fora da cena e estruturas sem geometria encontrada. Peça, requisito e estrutura anatomicamente validada são contagens diferentes.

Entre os 125 IDs sem associação direta, a matriz anterior lista **21 com geometria nomeada**, **51 parciais** e **53 não localizados**. São estados herdados de disponibilidade, sem promoção para validação nesta tarefa.

**Resultado da inspeção de inventários:** os próximos ganhos realistas podem vir de regiões reconhecíveis da própria malha, cordas já existentes e contexto torácico pronto. Os acervos atuais não permitem prometer completar os 178 alvos realistas apenas renomeando peças.

Nenhuma geometria foi criada, segmentada ou certificada neste levantamento. Não foram pesquisadas novas fontes externas.

## Prioridade 0 — revisar as conexões que já entraram

| Alvos | Fonte atual | O que revisar antes de ampliar |
|---|---|---|
|46a,58a|BodyParts3D `FJ2421`,`FJ2420`, integrados como `bp_FJ2421`/`bp_FJ2420`|Inserção dos folhetos, continuidade com cordas e papilares. A boa transformação global não valida cada inserção.|
|59,60|`FJ2418`/`bp_FJ2418`; Z `Inferior papillary muscle of left ventricle`/`heart_38`|Alvo59 está apenas parcialmente representado por uma cabeça papilar. **Não acrescentar FJ2429 como um músculo novo:** registration.json já o associa à peça inferior esquerda existente, apesar do nome BP lateral.|
|81,83,94–104d|Árvore BP da cena; coronárias Z disponíveis no acervo|Evitar sobrepor árvores de duas fontes ou montar uma anatomia com dominâncias incompatíveis. Confirmar qual árvore se mantém, depois nomear ramos.|
|102|`bp_FMA3835`, posterior ventricular branch of right coronary artery|Equivalência com póstero-lateral depende de origem e trajeto; nome posterior ventricular não basta.|
|30a–h,C15,32–34,54a–d|Câmaras Z e vasos Z/BP|Rever encaixe das veias pulmonares/cavas e seio. Não confundir tubo que toca a parede com desembocadura aberta.|

## Prioridade 1 — reconhecer regiões já presentes, sem inventar tecido

Começar pela identificação dirigida e máscaras da superfície. Abaixo são **candidatos a marcação ancorada**, que precisam de seleção visual na malha. Não são coordenadas prontas ou confirmações de que todos os relevos estejam esculpidos.

| IDs | Regiões | Malha âncora da cena | Revisão concreta |
|---|---|---|
|7,8,9,10|Faces esternocostal, diafragmática e pulmonares|`heart_00` AD; `heart_01` VD; `heart_02` AE; `heart_03` VE|Conferir orientação corporal e delimitar contribuição de cada câmara. Uma face pode exigir máscara em mais de uma malha.|
|11,12,13|Margens direita, esquerda e inferior|AD,VE,VD/VE|Linha sobre o limite reconhecido, com vista inicial correta; não selecionar uma faixa arbitrária do bounding box.|
|14,15|Base e ápice|AE/AD;VE|Ápice no extremo real do VE; base voltada posteriormente, relação com veias. Evitar chamar toda a borda superior da tela de base.|
|17,19|Aurículas direita/esquerda|`heart_00`/`heart_02`|A aurícula é parte da parede atrial disponível. Delimitar prolongamento e abertura de continuidade; não duplicar como câmara separada.|
|25,26,27,28,29|Sulcos e cruz do coração|Paredes das câmaras e vasos vizinhos|Verificar o relevo/limite em vistas anterior/posterior. Se a depressão não existir, a linha será orientação topográfica, não relevo confirmado.|
|51,61|Cordas tendíneas por ventrículo|VD: `heart_26`,`heart_27`,`bp_FJ2421`;VE: `heart_28`,`bp_FJ2420`|Cordas estão incorporadas nos folhetos. Criar seleção por subconjunto de faces ou região, preservando triangulação, em vez de tubos novos. Conferir papilares/folhetos nas duas extremidades.|
|37|Parte posterior lisa do AD|`heart_00`|Separar região lisa da área anterior; ausência de pectíneos esculpidos não prova que toda a parede seja a parte lisa.|
|43,C41|Infundíbulo do VD e vestíbulo aórtico do VE|`heart_01`/`heart_03`|Seguir caminho de saída até a respectiva valva; não conferir apenas em vista externa.|

**Implementação de uma região útil:** guardar ID da malha, faces selecionadas e âncora em triângulo/coordenadas baricêntricas, uma vista de estudo e uma vista sem rótulos. A âncora acompanha a peça se houver vista explodida. O critério é que o aluno consiga reconhecer a região; uma bolinha flutuante aproximada não satisfaz esse objetivo.

**4b e6 — epicárdio/endocárdio:** as superfícies externa/interna permitem indicar localização do revestimento. Isso não individualiza suas espessuras nem cria camadas reais. Oferecer como identificação de superfície, mantendo a limitação de camada não segmentada.

## Prioridade 2 — alvos internos condicionados à topologia real

| IDs | Candidato local | Condição para aceitar |
|---|---|---|
|32,33|AD + cavas (`heart_00`,`heart_10`,`heart_11`)|Selecionar contorno de uma abertura efetiva na câmara e demonstrar continuidade vascular.|
|34|AD + seio (`heart_00`,`bp_FMA4706`)|Óstio próximo da VCI e óstio AVD; conferir com slide Vasos 31. Não usar referência à VCS do ASR.|
|45,57|JunçãoAD/VD e AE/VE com aparelhos valvares|Reconhecer abertura AV em relação ao conjunto de folhetos. Distinguir óstio de anel fibroso.|
|54a–d|AE + quatro veias (`heart_02`,`heart_12`–`heart_15`)|Cada veia deve desembocar na abertura correspondente. Vaso presente não prova que o óstio exista.|
|80,82|Aorta ascendente + troncos coronários|Os vasos devem sair do seio correto; não marcar óstio na parede fechada apenas porque o vaso começa perto.|
|22,23,24,C47|Paredes adjacentes das câmaras|Verificar septo compartilhado sem duplicação, espessura e limites. A parte membranácea não é qualquer triângulo liso perto das valvas.|
|41,55|Superfícies septais deAD/AE|Procurar depressão e assoalho reais. Sem relevo identificável, não chamar área plana de fossa oval validada.|
|77,78,79,C45a–c|Raiz aórtica/tronco pulmonar junto aos folhetos|Conferir se as dilatações dos seios foram modeladas. `heart_04` tem138 vértices e `heart_06`61 no catálogo inicial: candidatos pouco detalhados, não prova de ausência nem presença dos seis seios.|
|104b,104c,104d|`bp_FMA3895`: elementos `FJ2649`–`FJ2654`; alternativa Z `Circumflex artery of heart`|Percorrer cada elemento com origem e trajetória. Não existem conceitos individuais confirmados no inventário para nomear automaticamente lateral/marginal/posterior esquerdo.|

Se um óstio estiver ausente, isso vira trabalho de reparo/reconstrução com referência. Um pin não substitui a abertura. Se há duas paredes de câmaras sobrepostas, corte simples pode expor artefato e exige revisão antes de treino.

## Prioridade 3 — geometria pronta fora da cena

Os 21 alvos abaixo já têm candidatos nomeados no acervo local. Priorizar continuidade da aorta, vasos do arco e sistema ázigos; depois relação pericárdica e nervos. GeometriasZ em `CURVE` com perfil/bevel positivo são superfícies exportáveis, mas não estão todas no GLB cardiovascular.

| ID | Estrutura | Fonte local exata | Relações a revisar |
|---|---|---|
|30j|Artéria aorta|Z `Ascending aorta` (nó369/malha360); Z `Thoracic aorta` (nó325/malha316); Z `Abdominal aorta` (nó331/malha322); BP `FMA3736`: `FJ3413`; BP `FMA3768`: `FJ3411`; BP `FMA87217`: `FJ1931`; BP `FMA3789`: `FJ1932`|Alvo coletivo da aorta: não criar duplicata. Associar segmentos existentes76/84 e candidatos92/93; vista de conjunto.|
|85|Tronco braquiocefálico|Z `Brachiocephalic trunk` (nó324/malha315)|Emergência no arco e bifurcação em carótida comum/subclávia direitas.|
|86|Artéria carótida comum direita|Z `Right common carotid artery` (nó4/malha0); BP `FMA3941`: `FJ3564`|Continuidade do braquiocefálico até bifurcação carotídea; contexto cervical opcional.|
|87|Artéria subclávia direita|Z `Right subclavian artery` (nó72/malha68); BP `FMA3953`: `FJ3579`|Origem no braquiocefálico e percurso proximal; não carregar membro inteiro.|
|88|Artéria carótida comum esquerda|Z `Left common carotid artery` (nó137/malha133); BP `FMA4058`: `FJ3483`|Origem direta no arco; distinguir de86.|
|89|Artéria subclávia esquerda|Z `Left subclavian artery` (nó195/malha191); BP `FMA4694`: `FJ3479`|Origem no arco e relação com região superior do tórax.|
|90|Artéria carótida interna|Z `Internal carotid artery.l` (nó166/malha162); Z `Internal carotid artery.r` (nó33/malha29)|Identificar ramo interno na bifurcação; raiz cervical suficiente ao reconhecimento inicial, sem encéfalo.|
|91|Artéria carótida externa|Z `External carotid artery.l` (nó138/malha134); Z `External carotid artery.r` (nó5/malha1)|Identificar ramo externo na bifurcação; não importar toda vascularização facial por padrão.|
|92|Aorta descendente torácica|Z `Thoracic aorta` (nó325/malha316); BP `FMA87217`: `FJ1931`|Continuidade com arco, relação posterior com coração/esôfago e passagem pelo diafragma.|
|93|Aorta descendente abdominal|Z `Abdominal aorta` (nó331/malha322); BP `FMA3789`: `FJ1932`|Continuidade ao atravessar diafragma; extensão abdominal em cena contextual isolada.|
|116|Artéria musculofrênica|Z `Musculophrenic artery.l` (nó199/malha195); Z `Musculophrenic artery.r` (nó94/malha90); BP `FMA10645`: `FJ1969`, `FJ1979`|Origem na torácica interna e relação com diafragma; não confundir com pericardicofrênica115.|
|117|Artéria bronquial|BP `FMA68109`: `FJ1933`|Origem e trajeto brônquico/pericárdico; preferir FJ1933 padrão, não substituir automaticamente por variante FJ3418.|
|118|Artéria esofágica|BP `FMA4149`: `FJ1934`|Origem na aorta torácica e relação com esôfago; não interpretar vaso no esôfago como malha do órgão.|
|119|Artéria frênica superior|Z `Superior phrenic arteries` (nó330/malha321)|Território superior do diafragma e origem; não trocar por inferior phrenic artery.|
|122a|Sistema ázigos: veia ázigos|Z `Azygos vein` (nó509/malha445); BP `FMA4838`: `FJ3416`|Arco sobre raiz pulmonar direita e chegada à VCS; geometria disponível não garante por si a rede pericárdica.|
|122b|Sistema ázigos: veia hemiázigos|Z `Hemi-azygos vein` (nó511/malha447); BP `FMA4944`: `FJ3434`|Trajeto esquerdo e cruzamento até ázigos; verificar continuidade do conjunto.|
|122c|Sistema ázigos: veia hemiázigos acessória|Z `Accessory hemi-azygos vein` (nó510/malha446); BP `FMA5011`: `FJ1981`|Distinguir da hemiázigos e revisar seu cruzamento/tributárias.|
|123|Nervo vago|Z `Vagus nerve (X).l` (`Startup.blend` CURVE); Z `Vagus nerve (X).r` (`Startup.blend` CURVE)|Extrair trechos torácicos dos vagos; preservar relações com esôfago e raízes pulmonares. Não equivalem ao plexo cardíaco inteiro.|
|125|Troncos simpáticos|Z `Sympathetic trunk.l` (`Startup.blend` CURVE); Z `Sympathetic trunk.r` (`Startup.blend` CURVE)|Troncos paravertebrais com gânglios como contexto; não chamar essa cadeia de plexo superficial/profundo.|
|V42c|Linfonodos traqueobronquiais inferiores|Z `Inferior tracheobronchial nodes` (`Startup.blend` MESH)|Linfonodos em relação à bifurcação traqueal; não substituir pela malha de todos os linfonodos torácicos.|
|V42d|Linfonodos paratraqueais|Z `Paratracheal cervical nodes` (`Startup.blend` MESH); Z `Paratracheal thoracic nodes` (`Startup.blend` MESH)|Distinguir paratraqueais cervicais/torácicos e relação com traqueia; complementos dos slides, não roteiro nominal.|

**Caminhos:** Z vascular convertido em `malhas/CardioVascular41.glb`, nomes/nós em `malhas/z_fbx_gltf.json`; fonte completa em `fontes/z_anatomy/Startup.blend`. BP em `fontes/bp3d/isa_BP3D_4.0_obj_99.zip`, elementos OBJ internos `isa_BP3D_4.0_obj_99/FJ….obj`; usar a transformação registrada em `refinamento/geometria/registration.json`, conferindo cada região nova. A transformação ajustada ao coração não certifica a posição de todo o tórax.

## Contexto mínimo para 1 e 2: malhas identificadas no Startup.blend

| Marco | Nomes do inventário | Disponibilidade técnica |
|---|---|---|
|Esterno|`Manubrium of sternum`; `Body of sternum`; `Xiphoid process`|2662,4466 e914 polígonos, respectivamente.|
|Diafragma|`Diaphragm`|4921 polígonos; também existe `Diaphragmatic fascia` com 2391, sem confundir com pericárdio.|
|Pulmões|`Superior lobe of right lung`; `Middle lobe of right lung`; `Inferior lobe of right lung`; `Superior lobe of left lung`; `Inferior lobe of left lung`|Cinco malhas com982,940,1076,1190 e1177 polígonos. Usar contexto atenuado, sem capítulo respiratório.|
|Esôfago|`Oesophagus`|CURVE com 8 pontos de controle e perfil; precisa exportação preservando perfil, não mero tubo reconstruído pela caixa envolvente.|
|Traqueia e bifurcação|`Trachea`; `Right main bronchus`; `Left main bronchus`|Traqueia 4516 polígonos; brônquios são CURVE com 2/3 pontos e bevel. Úteis para âzigos e linfonodos.|
|Coluna torácica|`Vertebra T6`,`Vertebra T7`,`Vertebra T8`,`Vertebra T9`|1774,2646,1706 e2968 polígonos. Quantidade mínima para relações posteriores ensinadas.|
|Referência do 5º EIC|`Costal cartilage of fifth rib.l`/`.r`, costelas adjacentes|Cartilagens têm 1082 polígonos cada; não usar só elas para prometer espaço intercostal completo.|

**Limite:** esse contexto resolve orientação e várias relações de 1/2, mas o pericárdio ausente continua impedindo apresentar todas as relações do mediastino como completas. Órgãos contextuais não entram como novos alvos no denominador.

## Lacunas que continuam sem geometria pronta confirmada

| Grupo | IDs | O que os acervos atuais não fornecem |
|---|---|---|
|Pericárdio e fixações|3,4a,70–75|Saco fibroso, lâmina parietal/reflexões, ligamentos e seios coerentes. Coleções nomeadas vazias não são malhas.|
|Fibras/camadas miocárdicas|5a–e|Orientação volumétrica por camada; textura ou cópia da parede não resolve.|
|Pregas/relevos internos|35,36,38–40,42,44,50,52,56,62,C21|Pregas venosas/forame oval, pectíneos, cristas, banda moderadora e trabeculações individualizadas. Pode haver parte incorporada ainda não reconhecida; inventário não comprova.|
|Esqueleto fibroso|64–69|Anéis e trígonos com geometria consistente. Óstios existentes não substituem tecido fibroso.|
|Vasos/nervo ausentes|31,94,95,99,104a,107,115,121,124|Ligamento arterial, ramos nodais/atriais, veia oblíqua AE, pericardicofrênicos e frênico sem malha anatômica específica localizada.|
|Condução/plexos|C61a–b,C66a–f|Sistema nervoso/condução específico. Vago/tronco simpático genéricos não resolvem plexos nem nós.|
|Microvasos/linfáticos|V36,V42a–b,V42e–f|Veias mínimas, plexos linfáticos e ductos sem geometria confirmada. Os linfonodos prontos não provam toda a rede.|

**Armadilhas de nomenclatura:** `Node of ligamentum arteriosum` é um linfonodo e não o ligamento31; estruturas com `auricle` podem pertencer à orelha; `Inferior phrenic artery` não é 119; `Diaphragmatic fascia` não é pericárdio. Referências FONT ou linhas com 2 vértices/0 faces não representam anatomia volumétrica.

## Sequência de execução sugerida

1. Rever inserções das peças adicionadas e conexões dos vasos; registrar limitações por alvo.
2. Marcar e fotografar vistas de faces/margens/base/ápice/aurículas/sulcos; armazenar regiões na malha.
3. Separar seleção das cordas e conferir vias de saída; liberar exercícios apenas onde o alvo esteja individualmente reconhecível.
4. Inspecionar óstios e septos por dentro antes de qualquer pin ou contagem de cobertura.
5. Importar contexto anatômico mínimo e vasos prontos do quadro de 21 alvos; usar módulos de contexto ativáveis.
6. Localizar ramos do circunflexo nos seis elementos reais. Se a identidade não puder ser determinada, manter conjunto sem atribuições individuais falsas.
7. Para as lacunas sem geometria, apresentar figura de referência com estado pendente e preparar reconstrução específica posteriormente. Isso mantém estudo útil, sem alegar 100% em 3D.

## Proveniência da inspeção

- `matriz_coracao.json`: fonte da associação entre requisitos e candidatos, não prova geométrica atual.
- `malhas/z_blend_inventory.json`: objetos MESH e CURVE; somente superfícies não vazias contam como candidatos.
- `malhas/bp3d_inventory.json`: conceitos FMA e elementos OBJ efetivamente presentes.
- `malhas/z_fbx_gltf.json`: nomes e índices de nós exportados; índices pertencem a esse arquivo, não ao GLB final do site.
- `refinamento/geometria/registration.json`: correspondências geométricas já investigadas por outro agente.
- `refinamento/aulas_escopo.json`: exigências e relações docentes; não modificado nesta tarefa.
- Catálogo lido com SHA-256 `056b13edf2acfc066d4e571efa7f9a12ae05cda85823aa86eeb53dda854c5906`; arquivo evolui em paralelo.
