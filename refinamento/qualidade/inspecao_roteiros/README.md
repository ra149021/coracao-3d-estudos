# Inspeção dos modelos e vistas do roteiro — 29/09/2026

Foram implementadas 15 vistas de estudo sobre as peças existentes. O seletor **Estudar uma região**, nos visualizadores principais, ajusta peças visíveis, câmera e transparência. Os itens relacionados no **Roteiro** também oferecem o acesso. Cada vista inclui uma referência aos slides da professora Carmem.

| Modelo | Vistas | Slides |
| --- | --- | --- |
| Coração | Tricúspide; mitral; átrio direito; átrio esquerdo; saída pulmonar; saída aórtica | Coração: 31, 37, 39 e 43 |
| Respiratório | Árvores brônquicas dos cinco lobos; relações dos dois hilos; inspeção da pleura; seios paranasais disponíveis | Respiratório: 34, 92, 93, 105, 106 e 118 |

A vista do roteiro pode mostrar contexto de um alvo ainda pendente. Isso não altera sua classificação nem certifica que seus detalhes estejam modelados. As imagens docentes de referência foram conferidas visualmente. A vista do hilo esquerdo usa a comparação bilateral da página 106.

## Correções de associação

Os seios frontal (R034) e esfenoidal (R036) já constavam nas malhas, mas a busca no acervo usava nomes diferentes. Foram corrigidos o gerador, o catálogo e os requisitos. A geometria passa a constar como disponível; a validação anatômica individual permanece pendente. Não foram acrescentadas malhas.

## Inspeção geométrica

[inspect_meshes.py](inspect_meshes.py) produz [topology.json](topology.json) a partir dos GLBs publicados. A análise une posições exatamente coincidentes e conta componentes conectados, bordas e faces degeneradas. Não reconhece tecidos nem limites anatômicos.

- As paredes de AD, VD e AE têm um componente com faces; o AE também tem dois vértices isolados. O VE tem dois componentes com faces. As quatro paredes apresentam bordas abertas. Fechá-las automaticamente poderia modificar aberturas legítimas.
- As cinco cúspides atrioventriculares inspecionadas têm cordas incorporadas ao componente. Não há separação anatômica validada que permita convertê-las automaticamente em peças independentes.
- O objeto pleural tem oito componentes geométricos fechados. Oito componentes não correspondem a oito membranas anatômicas: a fonte contém operações de espessura. A vista conserva o conjunto sem atribuir folheto visceral, parietal ou recessos a componentes arbitrários.
- Os brônquios segmentares podem ser observados dentro de seus lobos; os volumes dos segmentos broncopulmonares não estão delimitados.

Os arquivos `heart.glb` e `respiratory/model.glb` foram comparados byte a byte com o commit base `0ef95b6`: permanecem idênticos. São 72 peças cardíacas e 175 respiratórias.

## Verificações

- Geração das 15 vistas com checagem de IDs de peças e requisitos; presença dos 15 arquivos de slides referenciados.
- Chromium: seleção das 15 vistas e comparação das peças visíveis com suas definições, sem erros de JavaScript nesse percurso.
- Chromium: restauração de peças, câmera, alvo e transparência após iniciar/revelar/pausar a prática; bloqueio do seletor durante a rodada; acesso pelo roteiro e por URL; retorno à vista exterior.
- Telas de 320 e 390 pixels sem transbordamento horizontal; acervos independentes HRA e laringe carregam sem receber vistas incompatíveis.
- Inspeção visual de seis vistas: [tricúspide](vistas/av_direita.png), [mitral](vistas/av_esquerda.png), [árvore superior esquerda](vistas/arvore_superior_esquerdo.png), [hilo direito](vistas/hilo_direito.png), [pleura](vistas/pleura_inspecao.png), [seios](vistas/seios_referencia.png).

Para regenerar as definições, execute `python3 scripts/build_study_views.py`. A análise de topologia requer NumPy e SciPy; o site não depende dessas ferramentas. Todos os recursos das novas vistas estão no repositório.

## Pendências preservadas

Esta entrega melhora a exploração e corrige associações; não completa toda a anatomia do roteiro. Permanecem pendentes, entre outros, a individualização dos folhetos e recessos pleurais, volumes segmentares pulmonares, pericárdio e detalhes internos cardíacos. Novas peças exigem fonte com licença adequada, correspondência anatômica e inspeção visual antes de integração.
