# Complementos de geometria cardíaca pronta

## Entrega e decisão de integração

Nenhuma nova forma anatômica foi gerada. Este pacote reaproveita BodyParts3D 4.0, registra-o à montagem Z-Anatomy e preserva as superfícies originais. Inclui também uma referência local independente da Universidade de Minnesota. Não modifica o construtor principal nem a interface do atlas principal.

| Arquivo | Estrutura da fonte | Uso recomendado |
|---|---|---|
| `meshes/FJ2421.npz` | FMA7238 — cúspide anterior da tricúspide, com cordas incorporadas | Integrar como a cúspide anterior que falta. |
| `meshes/FJ2420.npz` | FMA7242 — cúspide anterior da mitral, com cordas incorporadas | Integrar como a cúspide anterior que falta. |
| `meshes/FJ2418.npz` | FMA7265 — cabeça anterolateral de músculo papilar do VE | Integrar apenas como **porção**; a fonte não autoriza chamar esta peça de grupo papilar completo. |
| `vascular/*.npz` | 23 grupos coronários/venosos; 104 elementos FJ exclusivos | Camada vascular alternativa, substituindo conjuntamente as 10 peças Z descritas em `vascular.json`. |

Os campos `vertices` dos NPZ já estão nas coordenadas finais do site; `faces` contém triângulos. `z_world_mm` guarda o resultado anterior à escala de exibição, para auditoria. Use `numpy.load(..., allow_pickle=False)`. Metadados e hashes estão em `registration.json` e `vascular.json`.

### Duas cúspides

As duas cúspides podem ser acrescentadas com confiança técnica no registro espacial. A inspeção em seis painéis está em `registro_inspecao.png`. Folhetos e cordas se encaixam no conjunto valvar/papilar já existente. Isso não certifica cada inserção de corda nem reproduz mecanicamente abertura/coaptação da valva.

| Peça | Vértices após solda exata | Triângulos | Componentes fechados |
|---|---:|---:|---:|
| FJ2421 | 4.068 | 8.160 | 1 |
| FJ2420 | 3.757 | 7.558 | 1 |
| FJ2418 | 412 | 816 | 2, preservados como na fonte |

Todas são finitas e não apresentam arestas de bordo, arestas não manifold ou triângulos de área zero após unir posições **numericamente idênticas**. Os OBJ originais repetem vértices em costuras de índices. A solda remove apenas essa duplicação: não alisa, preenche buracos, modifica posições ou elimina componentes.

## Registro verificável

Foi ajustada **uma única transformação de similaridade** BodyParts3D → Z-Anatomy, com escala uniforme positiva e rotação própria. Sete peças homólogas foram usadas: três folhetos atrioventriculares existentes e quatro músculos papilares. Pontos só podem corresponder à mesma peça nomeada; não há deformação ou deslocamento específico por estrutura.

- Escala: **1,0336034707503967**.
- Translação após rotação, em mm do mundo Z: **[-0,3501534749; 102,5486820295; 23,2188142519]**.
- Matriz completa: `matrix_bp_mm_to_z_world_mm` em `registration.json`.
- Diferença máxima das caixas envolventes nas sete peças: **0,3935 mm**.
- RMS simétrico de distância entre vértices mais próximos: **0,1844 a 0,9545 mm**, dependendo da peça.
- Ajuste deixando uma peça de fora: RMS **0,1942 a 0,9591 mm** na peça não usada no ajuste.

Essas distâncias comparam vértices, cujas densidades diferem entre as malhas; não são erros ponto-a-superfície. “mm” refere-se à escala nominal dos arquivos. Não demonstra precisão clínica nem anatomia exata de um indivíduo real. A proximidade geométrica e a estabilidade ao excluir peças sustentam a origem compartilhada, sem depender apenas da semelhança dos nomes.

Conversão final aplicada após o registro em mm:

```text
site = ([x, z, -y] * 0.1 - [2, 130.5, 2]) * 0.25
```

## Rede coronária e venosa

`prepare_vascular.py` prepara **23 grupos, 104 FJ distintos e 47.384 triângulos**. Todas as superfícies verificadas são finitas, fechadas e sem arestas não manifold ou faces degeneradas depois da solda exata. A figura `vascular_inspecao.png` compara as duas redes nas mesmas vistas anterior e posterior, junto das paredes Z-Anatomy.

**Não sobrepor as redes completas.** Vários ramos já estão incorporados às peças Z: aproximadamente 98% dos vértices dos ramos ventriculares anteriores não marginais e 99,6% do ramo marginal direito BP ficam a menos de 1 mm de vértices da rede Z. Sobrepor criaria vasos duplicados. A comparação não prova identidade ponto a ponto e não deve ser usada para subtração automática de superfícies.

Recomendação: substituir os seis objetos coronários Z e as quatro veias Z pelos 23 grupos BP de uma vez. A montagem preserva o mesmo registro global usado nas cúspides, sem ajuste independente dos vasos. As malhas BP introduzem ramos já nomeados na fonte e veias que não estavam na montagem inicial, incluindo cardíaca parva, marginais direita/esquerda e anteriores do VD.

### Limites dos nomes e relações

- O conceito pai FMA3813 inclui os ramos não marginais FMA3815 **e** o ramo marginal FMA3818. O pacote exporta os dois filhos sem repetir FJ. Para o item geral 97 do roteiro, considerar a união desses grupos.
- A fonte separa um segmento chamado veia cardíaca magna (FMA4707) de sua continuação interventricular anterior (FMA66403). A interface deve mostrar a continuidade e não ensinar duas veias sem relação.
- A circunflexa permanece um agregado. Seus ramos atriais, marginais e posteriores **não** passam a ser identificados individualmente só porque o agregado foi importado.
- O conjunto de ramos ventriculares posteriores direitos ainda exige correlacionar a nomenclatura exata do roteiro “póstero-lateral”.
- Ramos nodais, veia oblíqua do AE e vasos pericardicofrênicos continuam sem solução neste pacote.
- As inserções distais, óstios e cada trajeto fino não receberam validação anatômica independente. A comparação visual avaliou o registro e a distribuição do conjunto. Variações individuais de circulação coronária permanecem relevantes.

## Reproduzir

No diretório raiz do projeto, com o Python preparado que contém NumPy, SciPy e Matplotlib:

```bash
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/geometria/register_bp3d.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/geometria/render_registration.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/geometria/prepare_vascular.py
/home/victorhugo/.local/share/codex-tools/venv/bin/python refinamento/geometria/render_vascular.py
```

Os scripts leem somente arquivos já disponíveis em `fontes/bp3d`, `malhas/heart_source` e `malhas/CardioVascular41.glb`. Não executam o conteúdo do Blender nem acessam rede.

## Realismo e fontes externas

O registro resolve a integração; não aumenta o detalhe intrínseco das malhas. BodyParts3D é um atlas anatômico idealizado e sua distribuição utilizada tem redução de polígonos de 99%, conforme o [download oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html). Os limites e as alternativas estão em `fontes_externas.md`.

### Quatro cortes institucionais UMN — referência local separada

O [tutorial institucional do Visible Heart Laboratories](https://www.vhlab.umn.edu/atlas/echocardiography-tutorial/exam-views-models.shtml) oferece `MC_VALVES.zip` para impressão. O arquivo foi obtido diretamente do domínio da universidade, com CRC do ZIP e SHA256 registrados. Os quatro STL foram convertidos sem decimação ou modificação da forma; não foi executado conteúdo do 3MF ou suas configurações de impressão.

| Nome original | Vértices únicos | Triângulos preservados |
|---|---:|---:|
| `MC-VALVES_1-1_4` | 537.369 | 1.075.750 |
| `MC-VALVES_1-2_4` | 66.397 | 133.284 |
| `MC-VALVES_2-1_4` | 108.562 | 217.680 |
| `MC-VALVES_2-2_4` | 15.435 | 30.918 |

Todos os vértices são finitos. A inspeção visual inicial documentada contempla os três cortes menores. O GLB independente tem **34.961.936 bytes e 1.457.632 triângulos**. A centralização, rotação dos eixos e escala uniforme são comuns às quatro peças; suas relações originais ficam preservadas. Transformação, caixas envolventes, hashes e limitações estão nos JSON locais. Não há correspondência espacial com o modelo BP3D.

`verify_umn_glb.py` confirma o cabeçalho/hash do GLB, a igualdade de todos os índices de triângulos com a fonte, a igualdade das posições com a transformação declarada e a ausência de faces de área zero, índices fora do limite e normais nulas. Um vértice no corte maior recebeu a normal de sua maior face incidente porque a soma das normais se cancelava; isso altera apenas a iluminação, sem mudar posições ou triângulos.

**Reprodução local:** os scripts `inspect_umn_reference.py` e `export_umn_glb.py` leem o ZIP/NPZ em `referencias_locais/`, sem acesso à rede. Depois da exportação, `umn_reference.glb` e `umn_reference_catalog.json` devem ser copiados para `site/assets/local-references/`. Abra `reference.html` pelo servidor local do projeto. O visualizador permite selecionar cada corte ou o conjunto, girar, deslocar, ampliar e reenquadrar; o catálogo é separado do atlas. Se os arquivos não estiverem presentes, a página oferece o link oficial e o retorno ao atlas.

O conjunto é uma **referência institucional de cortes didáticos**, não uma nova lista de estruturas segmentadas. Não foi estabelecido o espécime/doador ou a técnica de aquisição desse ZIP específico; os nomes originais permanecem visíveis. As cores são ilustrativas, pois o STL não contém textura. Não contabilizar essas peças como solução das lacunas práticas de trabéculas, pectíneos, pericárdio ou condução.

**Distribuição:** a permissão de disponibilização pública das malhas não foi confirmada. Manter `referencias_locais/`, `fontes_publicas/` e `site/assets/local-references/` fora do GitHub público, incluindo imagens derivadas. Os scripts, este registro e os links oficiais podem documentar o processo sem redistribuir os arquivos institucionais. As licenças BodyParts3D/Z-Anatomy abaixo não se aplicam ao material UMN.

## Licença e proveniência

**BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.**

Fonte: [download oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html), [licença atual](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html). O download independente de BodyParts3D e seus complementos permanecem identificados como CC BY 4.0. A montagem Z-Anatomy possui avisos próprios CC BY-SA 4.0, que devem ser preservados. Para uma distribuição conjunta, manter ambas as proveniências e os avisos do conjunto derivado.

Alterações: extração de peças, transformação global de coordenadas, solda de posições duplicadas, agrupamento de elementos sem repetição e rótulos didáticos em português. Nenhuma estrutura anatômica nova foi sintetizada. Hashes SHA256 por OBJ e NPZ constam nos JSON. Os identificadores FMA/FJ são da tabela `isa_element_parts.txt` distribuída pelo autor.
