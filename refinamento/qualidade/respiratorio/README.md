# Qualidade anatômica respiratória — 28/09/2026

## Melhoria incorporada

O atlas respiratório passou de 167 para **175 peças**, com oito vasos pulmonares
proximais do mesmo `CardioVascular41.fbx` que fornece o contexto cardíaco. Nenhuma
peça foi deformada, alinhada individualmente ou substituída por forma procedural.

| Peça da fonte | Triângulos | Requisito associado |
|---|---:|---|
| Pulmonary trunk | 93 | contexto |
| Bifurcation of pulmonary trunk | 472 | contexto |
| Right pulmonary artery | 236 | R173 |
| Left pulmonary artery | 826 | R174 |
| Right superior pulmonary vein | 708 | R175 |
| Right inferior pulmonary vein | 236 | R175 |
| Left superior pulmonary vein | 354 | R176 |
| Left inferior pulmonary vein | 354 | R176 |

O grupo `vascular_pulmonar` e o preset `hilo` permitem comparar vasos e brônquios
com lobos translúcidos. R151/R152 representam relações regionais parciais, sem
declarar hilo/raiz como peça independente ou completa. Tronco e bifurcação não
entram no quiz. As artérias estão azuis e as veias vermelhas por convenção didática
de oxigenação; não são texturas de tecido.

Fonte: [exportação oficial Z-Anatomy, commit fixado](https://github.com/LluisV/Z-Anatomy/tree/6c7f9016bd5899ac8edafd31b9900c151df42ed6/Resources/Models/FBX),
CC BY-SA 4.0, Gauthier Kervyn, Lluis Vinent e colaboradores; origem BodyParts3D.
A transformação comum continua `(FBX_world_cm − [0,142,0]) × 0,2`.

O GLB contém 959.255 triângulos e 23.603.924 bytes; SHA-256
`986b8490cf76a2f0cb9b96a8f6637e3e4a6322acae55ede75ea8c4d6c6c8738a`.
Finito, índices, bounds, normais e hash conferidos por
`refinamento/respiratorio/geometria/verify_assets.py`.
Os vasos são abertos nas extremidades da fonte. Não foram fechados artificialmente.
Inspeção visual: `proximal_vessels_inspection.png`.

**Ganho real:** relações espaciais proximais anteriormente ausentes. A malha dos
vasos permanece relativamente grosseira e não contém rede segmentar. Os 85 IDs
com associação direta no catálogo não significam 85 estruturas validadas
individualmente; R010 foi preservado após a correção nominal das cartilagens alares.

## Referência independente de CT disponível

`rijnstate_reference/model.glb` e seu catálogo preservam os 312.856 triângulos
do STL suplementar de Meershoek, Loonen, Maal, Hekma e Hugen (2023), publicado
pela Springer. O artigo descreve segmentação de CT contrastada, suavização manual,
cortes periféricos e entalhes para ímãs. A licença **do modelo é CC BY-NC-SA 4.0**;
a licença CC BY 4.0 do artigo não substitui essa condição específica.
[Artigo e suplemento oficial](https://doi.org/10.1007/s40670-023-01807-x).

Inspeção do arquivo: 156.279 posições únicas, sem valores inválidos ou faces de
área zero após conversão; um componente contém 155.568 vértices e existem 58
fragmentos pequenos preservados. O STL possui um nome de sólido, sem cores ou
rótulos semânticos. Não separa vasos, brônquios e territórios em peças selecionáveis.
Não se inferiram fronteiras anatômicas a partir desses componentes.

O GLB aplica somente uma transformação comum, indexação de posições coincidentes,
normais para exibição e cor neutra. Não há deformação, decimação nem registro ao
Z-Anatomy. Lateralidade absoluta dos eixos da fonte não foi certificada. A geometria
é útil como referência visual de ramificação e relações, com essas limitações;
não acrescenta cobertura ao roteiro nem serve como padrão universal de anatomia.

`export_rijnstate.py` reproduz o GLB a partir do STL oficial cujo hash é conferido.
`audit.json` registra contagens, hashes e componentes; `inspection.png` mostra
duas vistas do arquivo completo. Créditos e licença em `rijnstate_reference/NOTICE.md`.

## Comparação com alternativas consultadas

| Fonte primária | Resultado desta etapa | Decisão |
|---|---|---|
| [Right Nasal Cavity Dataset, Sinha/Mendeley](https://doi.org/10.17632/73dzjb538x.1) | Metadados CC BY 4.0; cavidades direitas extraídas de CT de coleções TCIA de cabeça/pescoço oncológicas. Arquivo não inspecionado; acesso ao bundle público retornou 403. | Não presumir anatomia normal nem substituir conchas/meatos. Não incorporado. |
| [Dundee, Anatomy of the Larynx](https://sketchfab.com/3d-models/anatomy-of-the-larynx-a00bc73a303c46248db6a13a88b23404) | Edição/textura de Annie Campbell sobre BodyParts3D, declarada CC BY-SA 4.0; 34,7 mil triângulos no catálogo. | Mesma origem do modelo atual; sem evidência de ganho anatômico ou arquivo obtido nesta etapa. |
| [UBC HIVE, Human Larynx](https://sketchfab.com/3d-models/human-larynx-9cb56f0a20654072810a12959b812632) | Prosecção acadêmica; metadados consultados, sem licença de download identificada e marcada NoAI. | Link de estudo apenas. Malha e texturas não extraídas. |
| [NIH/HRA, Larynx Female](https://3d.nih.gov/entries/20972) | Referência associada ao Visible Human, distinta da origem BP; detalhe interno e licença do arquivo não conferidos nesta etapa. | Não incorporada e não tratada como melhoria demonstrada. |
| [BodyParts3D, download oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html) | A tabela pública consultada oferece a redução de 99% já disponível localmente. | Não foi encontrada nessa página uma versão mais densa para substituir a laringe atual. |

Não foi obtida uma nova malha pronta e licenciada que resolvesse folhetos/recessos
pleurais, mucosa/pregas vestibulares laríngeas ou parênquima segmentar individualizado.
Essas lacunas permanecem explícitas.

## Modificadores existentes no autor

`author_modifiers.json` registra 42 modificadores em 138 malhas respiratórias
correspondentes no `Startup.blend`, lidos por SDNA sem executar Blender. Pleura:
Subsurf e dois Solidify; mucosa/faringe: Subsurf, Mirror e Solidify; lobos: Subsurf.
As exportações FBX em uso já incorporam superfícies avaliadas — por exemplo,
pleura de 3.580 polígonos raw para 112.288 triângulos exportados e mucosa de
308 polígonos para 9.808 triângulos. Não se acrescentou subdivisão própria.

`heart_author_export_comparison.json` registra a comparação solicitada das quatro
câmaras cardíacas. O FBX tem mais triângulos em AD/VD/VE, mas menos no AE; não é
equivalente direto ao render Subsurf nível 2. Distâncias entre vértices de
tesselações diferentes não medem erro anatômico nem distância de superfície.
