# Geometria respiratória e laringe independente

## Entrega

| Modelo | Arquivos públicos derivados | Peças | Triângulos | Tamanho |
|---|---|---:|---:|---:|
| Respiratório Z-Anatomy | `site/assets/respiratory/model.glb` e `catalog.json` | 167 | 955.976 | 23.508.628 bytes |
| Laringe BodyParts3D independente | `site/assets/larynx/model.glb` e `catalog.json` | 40 | 149.758 | 3.633.868 bytes |

Nenhuma estrutura anatômica foi sintetizada. Os dois conjuntos preservam as superfícies prontas de seus respectivos acervos. As cores são ilustrativas; não há textura fotográfica, movimento respiratório ou simulação de fluxo/fonação.

## Respiratório: superfícies Z-Anatomy

O modelo reúne mucosa e cartilagens nasais, etmoide/vômer/conchas inferiores, representações sinusais, nasofaringe/orofaringe/laringofaringe, palato mole/úvula, cartilagens e músculos laríngeos, membranas e ligamentos disponíveis, traqueia, brônquios, cinco lobos pulmonares, pleura agregada, diafragma, intercostais e músculos supra/infra-hióideos. Costelas, esterno, quatro câmaras cardíacas e ossos da cabeça fornecem contexto opcional.

As malhas provêm das exportações oficiais `VisceralSystem100.fbx`, `SkeletalSystem100.fbx`, `MuscularSystem100.fbx`, `Joints100.fbx` e `CardioVascular41.fbx`, na revisão **6c7f9016bd5899ac8edafd31b9900c151df42ed6** do [aplicativo Z-Anatomy](https://github.com/LluisV/Z-Anatomy/tree/6c7f9016bd5899ac8edafd31b9900c151df42ed6/Resources/Models/FBX). As quatro primeiras foram obtidas do repositório oficial nesta etapa, com tamanho e hash Git conferidos antes da conversão por Assimp. Proveniência, URL e SHA256 estão nos arquivos locais `fontes/z_app/*.provenance.json` e no catálogo.

As exportações do autor já contêm a tesselação das curvas brônquicas e a avaliação de superfícies como pleura e lobos. Não foi necessário executar Blender, avaliar scripts incorporados ou criar tubos novos. Marcadores `.j`, coleções vazias, textos e linhas de anotação não foram tratados como estruturas anatômicas.

Todas as peças recebem **a mesma** transformação das coordenadas mundiais FBX em centímetros:

```text
display = (world_fbx_cm - [0, 142, 0]) × 0.2
```

Eixos de exibição: x positivo para esquerda anatômica; y superior; z anterior. Não há ajuste ou deformação por peça. As quatro câmaras cardíacas mantêm o registro do mesmo acervo, independentemente da centralização usada pelo visualizador cardíaco principal.

### Limites essenciais

- **Pleura:** existe uma malha com 112.288 triângulos, mas seus folhetos, regiões e recessos não são objetos separados. A peça não comprova cobertura individual de todos esses alvos.
- **Pulmões:** cinco lobos independentes. Fissuras são relações entre superfícies; regiões, margens, hilo e segmentos broncopulmonares não passam a ser malhas próprias.
- **Brônquios:** trajetos e calibres são os do autor. A peça entre parênteses “Anteromedial basal…” permanece oculta por padrão e fora do quiz; a fonte também mantém B7/B8 separados. Não usar essa peça extra para ensinar uma contagem universal dos segmentos.
- **Vias superiores:** mucosa nasal e partes da faringe são superfícies agregadas; a interface não deve inferir suas camadas ou espaços apenas a partir do nome da malha.
- **Diafragma:** superfície muscular disponível; centro tendíneo, hiatos e pilares não estão individualizados como partes selecionáveis.
- A lista de estruturas da professora e os IDs R### são responsabilidade do arquivo de requisitos; disponibilidade de malha não significa validação completa do conteúdo de prova.

## Laringe BodyParts3D: alternativa coerente

A montagem independente usa **42 elementos FJ únicos em 40 objetos**, pois dois pares pertencentes aos conceitos tireoaritenóideos esquerdo/direito foram agrupados. O duplicado cricóideo FJ2440 não foi repetido junto a FJ2769. Cartilagens, músculos, membranas, ligamentos e hioide preservam as posições originais BodyParts3D; a traqueia é contexto opcional.

Ela acrescenta peças prontas que não estavam individualizadas no conjunto Z: cartilagens cuneiformes, músculos vocais, ligamentos vocais, cone elástico, membrana tireo-hióidea, ligamentos hioepiglótico/tireoepiglótico e músculos aritenóideos oblíquos. **Ligamento vocal e músculo vocal são componentes da prega vocal; não representam seu revestimento ou a prega completa.** Pregas vestibulares e cavidades não foram criadas.

Coordenadas originais BP em milímetros são giradas para `[x,z,-y]`, centralizadas pelo conjunto laríngeo e escaladas uniformemente por 0,1. O centro exato consta no catálogo. Esta transformação é apenas de exibição: **não registra nem sobrepõe a laringe ao modelo Z-Anatomy**.

### Por que a fusão foi rejeitada

`register_larynx_bp3d.py` investigou uma única transformação de similaridade em sete cartilagens homólogas. A distância RMS simétrica entre vértices ficou entre **0,63 e 1,25 mm**; a tireóidea apresentou diferença de caixa de **3,39 mm**, e a epiglote alcançou **2,68 mm RMS** quando excluída do ajuste. Essas discrepâncias são relevantes para ligamentos e membranas finos. O registro experimental e os NPZ candidatos ficam documentados, mas **não são usados em nenhum dos dois GLB publicados**.

O modelo independente evita deslocar, deformar ou adaptar os tecidos BP às cartilagens Z. Também não constitui uma validação anatômica externa do acervo original.

## Verificação

`verify_assets.py` confirmou hashes, tamanhos, correspondência de IDs, contagens, limites geométricos, índices válidos, coordenadas finitas e normais unitárias em todas as **207 peças**. O relatório final é `asset_validation.json`.

Foram preservadas faces de área nula da representação exportada: **4 no esfenoide Z** e **30 na laringe BP** (3 ariepiglótico direito; 2 cricotireóideo mediano; 23 ligamento vocal esquerdo; 2 cone elástico direito). Elas não acrescentam superfície visível; não foram eliminadas, preenchidas ou convertidas em anatomia nova. A análise de topologia após solda exata, feita apenas para inspeção, registra bordas em 58 peças Z e arestas não manifold em 18 peças Z / 4 BP. Curvas ramificadas e superfícies do autor podem ter partes abertas ou desconectadas: não declarar esses arquivos como sólidos prontos para impressão.

`mesh_audit.json` e `larynx_mesh_audit.json` preservam também as medidas na preparação da malha; contagens numéricas de faces quase colineares podem diferir com a precisão usada. Para a representação GLB final, usar `asset_validation.json`.

Inspeções visuais realizadas:

- `inspecao_geometrica.png`: pulmões/brônquios, vias superiores, laringe Z e relação pleura/diafragma.
- `larynx_inspecao.png`: cartilagens/hioide, componentes vocais por cima e musculatura posterior BP.

Essas inspeções avaliam coerência de montagem e apresentação, sem certificar cada inserção muscular, espessura ou variação anatômica.

## Catálogo e requisitos

Os IDs de peças são estáveis: `resp_<nome_original_normalizado>` e `larynx_<FMA>`. Cada nó GLB fornece `extras.partId`. Os catálogos contêm `groups`, `presets`, `defaultVisible`, `quizEligible`, cores, limites, fontes e licenças.

No respiratório, `requirementIds` reúne correspondências nominais explícitas de tipo estrutura; `relatedRequirementIds` conserva regiões e candidatos. `requirementMatches` informa que a validação visual individual permanece pendente. No detalhe BP, IDs R### são associados aos conceitos FMA identificados. Nenhum catálogo transforma automaticamente essas relações em porcentagem de cobertura validada.

## Reproduzir localmente

Com os arquivos oficiais já preparados em `fontes/` e as conversões em `malhas/`:

```bash
/home/victorhugo/.local/share/codex-tools/venv/bin/python scripts/build_respiratory_assets.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python scripts/build_larynx_assets.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/respiratorio/geometria/verify_assets.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/respiratorio/geometria/inspect_respiratory.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/respiratorio/geometria/inspect_larynx.py
```

Os construtores não acessam rede. As fontes brutas, arquivos de aulas e ambientes locais não precisam ser publicados para servir os dois GLB derivados.

## Licença e atribuição

- **Z-Anatomy: CC BY-SA 4.0**, com a proveniência BodyParts3D e os avisos originais já presentes em `site/LICENSES/`. Extração, agrupamento, tradução, transformação comum e materiais de exibição são alterações deste projeto.
- **BodyParts3D, © The Database Center for Life Science — CC Attribution 4.0 International.** [Download oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html) e [licença oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html). A laringe independente mantém esta atribuição e os hashes de cada OBJ.

Estas permissões não abrangem slides, gravações de aulas ou a referência UMN de licenciamento ainda não confirmado.
