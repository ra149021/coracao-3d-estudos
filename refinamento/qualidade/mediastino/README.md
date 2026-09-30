# Ampliação geométrica do contexto mediastinal

O atlas respiratório passou de **175 para 190 peças**. Foram acrescentadas superfícies originais de esôfago, seis vasos, quatro peças nervosas bilaterais e quatro conjuntos de linfonodos. O ganho é a exploração de relações e de cinco associações do índice respiratório que ainda não tinham peça na cena; isso não certifica a anatomia integral nem transforma conjuntos em estruturas individuais.

## Peças e relação com o conteúdo

| Fonte posicionada Z-Anatomy | Peças acrescentadas | Material docente e escopo |
| --- | --- | --- |
| `VisceralSystem100` | Esôfago | Respiratório pp.108–109: contexto das relações mediastinais. R156/R157 continuam parciais; os sulcos não foram segmentados. |
| `CardioVascular41` | Aorta ascendente, arco aórtico, aorta torácica, subclávia esquerda, cava superior e ázigos | Respiratório pp.108–109. São contexto respiratório; alguns vasos já estavam no atlas cardíaco. A cava inferior não integra a nova vista direita. |
| `NervousSystem100` | Vagos esquerdo/direito e troncos simpáticos esquerdo/direito | Respiratório p.127; associação nominal a R181/R184. As peças têm trajetos integrais, inclusive fora do tórax. Ramos, gânglios individuais e plexos não foram individualizados ou validados. |
| `LymphoidOrgans100` | Traqueobronquiais inferiores/superiores e paratraqueais cervicais/torácicos | Respiratório pp.87,129; associação nominal a R186–R188. São quatro conjuntos, sem vasos linfáticos ou linfonodos individuais selecionáveis. Cervicais permanecem identificados como cervicais. |

As classificações e o estado de validação dos 222 alvos continuam inalterados. O catálogo passou de 87 para 92 IDs com associação direta; disponibilidade nominal é diferente de aprovação anatômica individual. As 15 novas peças começam ocultas e ficam fora do quiz.

## Quatro vistas de exploração

- `mediastino_direito`: contexto medial direito, associado à p.108.
- `mediastino_esquerdo`: contexto medial esquerdo, associado à p.109.
- `mediastino_nervos`: trajetos nervosos e relações no tórax, associado à p.127.
- `linfonodos_torax`: conjuntos junto da traqueia e brônquios, associado à p.129.

O seletor **Estudar uma região** e os itens relacionados no roteiro abrem essas vistas. `focusPartIds` enquadra os pulmões para estudar o tórax sem reduzir tudo ao tamanho das extensões cervicais/abdominais. Só a câmera muda: as superfícies permanecem inteiras.

As unidades teóricas 9 e 11 agora oferecem links para o novo contexto e para nervos/linfonodos. A regeneração também recuperou links de vasos pulmonares e dos seios frontal/esfenoidal já presentes; os textos, perguntas, respostas e referências permanecem iguais.

## Origem e reprodução

Fonte: [exportações oficiais Z-Anatomy](https://github.com/LluisV/Z-Anatomy/tree/6c7f9016bd5899ac8edafd31b9900c151df42ed6/Resources/Models/FBX), no mesmo commit usado pelas peças anteriores. Licença CC BY-SA 4.0, créditos em [NOTICE](../../../site/LICENSES/NOTICE.txt).

Os dois novos FBX foram conferidos por tamanho, Git blob e SHA-256. Assimp os converteu para GLB; os demais arquivos posicionados já estavam no acervo. Uma reconversão temporária independente dos dois FBX reproduziu os arquivos locais e as oito superfícies selecionadas dessas fontes.

A transformação comum continua `(FBX_world_cm − [0,142,0]) × 0,2`, após aplicar as matrizes mundiais originais. Não houve ajuste por peça, deformação, recorte geométrico, fechamento de bordas ou detalhamento inventado.

Com as fontes locais instaladas, executar a partir da raiz do repositório:

```bash
python scripts/fetch_mediastinal_sources.py
assimp export fontes/z_app/NervousSystem100.fbx malhas/NervousSystem100.glb -fglb2
assimp export fontes/z_app/LymphoidOrgans100.fbx malhas/LymphoidOrgans100.glb -fglb2
python scripts/build_respiratory_assets.py
python scripts/build_study_views.py
python refinamento/respiratorio/conteudo/build_theory.py
python scripts/verify_mediastinal_geometry.py
```

Os geradores e o verificador requerem NumPy e o acervo original não versionado; a execução do site pronto continua sem essas dependências. O verificador usa a baseline fixa `cc95e5f` e grava somente o relatório. Os FBX brutos não são distribuídos neste commit.

## Verificações e limites

[geometry_validation.json](geometry_validation.json) registra os resultados numéricos:

- 175 peças anteriores: **525 arrays de posições, normais e índices idênticos byte a byte**, preservando 23.406.276 bytes de dados.
- 15 novas peças: posições float32 e índices iguais às fontes sob a transformação comum; finitude, índices, bounds e normais conferidos.
- 190 peças e 1.095.593 triângulos; 27.033.052 bytes. Incremento: 3.429.128 bytes, cerca de 14,5%.
- Quatro triângulos degenerados anteriores preservados; nenhum novo. Essa checagem não certifica manifoldness, interseções ou orientação externa das normais.
- SHA-256 do GLB: `cd2ab109267f61f17186c1dccaa2b0a19ce5fa507bd42cb2f1986b6c90aa0a23`.

[browser_validation.json](browser_validation.json) registra Chromium: 13 vistas respiratórias com peças, transparência e fontes esperadas; links do roteiro e URL direta; exclusão das novas peças do treino; restauração de câmera/visibilidade/transparência; telas de 320 e 390 pixels sem transbordamento horizontal; carregamento dos três acervos cardíaco principal/HRA/laríngeo; nenhum erro JavaScript nesse percurso.

A conferência de integração confirmou 12 links de peças na unidade 9 e 19 na unidade 11. Links que combinam `preset` e `part` preservam o enquadramento torácico definido por `focusPartIds` quando a peça pertence à vista.

Capturas inspecionadas: [direita](vistas/mediastino_direito.png), [esquerda](vistas/mediastino_esquerdo.png), [nervos](vistas/mediastino_nervos.png), [linfonodos](vistas/linfonodos_torax.png). A comparação visual verifica orientação regional e presença das peças; não aprova todos os ramos, terminações, gânglios, sulcos ou drenagem.

Referências para conferir relações, além dos slides originais: [UAMS — linfáticos do tórax](https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/lymphatic-tables/lymphatics-of-the-thorax/) e [UAMS — nervos do tórax](https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/nerve-tables/nerves-of-the-thorax/). Pericárdio/reflexões, folhetos e recessos pleurais, volumes segmentares, frênicos e plexos completos permanecem pendentes.
