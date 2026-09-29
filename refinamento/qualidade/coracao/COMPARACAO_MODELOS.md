# Modelos cardíacos: qualidade, disponibilidade e uso recomendado

Revisão: 28/09/2026. Escopo: procurar anatomia real e geometrias reutilizáveis para coração, especialmente pericárdio, esqueleto fibroso, condução e relevo interno. Foram reaproveitados os registros anteriores em `refinamento/geometria/fontes_externas.md`; downloads anteriormente impedidos por CAPTCHA não foram repetidos.

## Resultado prático

**Foi preparado um segundo acervo local HRA, com septo interventricular selecionável. Ele acrescenta uma forma de estudar as câmaras e o septo, mas não é superior em realismo ao conjunto principal.** Para aparência de tecido e trabeculação real, as referências UMN 612 e 188 são mais promissoras; recomendamos o player oficial sob clique enquanto o download legítimo não for concluído.

Nenhum candidato obtido resolve, com licença e geometria verificadas, todas as lacunas do roteiro. Quantidade de triângulos e de objetos não mede cobertura anatômica.

## Comparação

| Candidato / origem | Disponibilidade e licença observadas | Ganho possível | Limite para este projeto |
|---|---|---|---|
| [HRA Heart Male v1.2 / NIH 3DPX-021000](https://3d.nih.gov/entries/3DPX-021000) | **GLB obtido** pelo download público oficial; CC BY 4.0 explícita no HTML. 14 malhas; 164.119 triângulos; 4,07 MB. | Septo interventricular individual, quatro câmaras e quatro conjuntos valvares no mesmo sistema espacial. | Superfícies simplificadas; sem textura fotográfica; cinco papilares com limites de identidade/completude. Não substituir a cena principal por expectativa de maior realismo. |
| [UMN Heart0612](https://sketchfab.com/3d-models/perfusion-fixed-human-heart-anatomy-612-f6d63aea48a14d27969067f2754c2d3b) | Página oficial VisibleHeartLabs anuncia download e embed; CC Attribution-NonCommercial. Arquivo não obtido; 500 mil triângulos informados. | Peça fixada por perfusão, com cores próximas às do tecido segundo os autores; superfície e coronárias. | Não é um atlas segmentado dos alvos. Página direta retornou 403 na ferramenta; conferir player no navegador. |
| [UMN Heart0188](https://sketchfab.com/3d-models/plastinated-whole-human-heart-188-d4cc3d373db24d3ca9d08907d620d078) | Download e embed anunciados; CC Attribution-NonCommercial. Arquivo não obtido; 499,5 mil triângulos informados. | Janela de preparação do VD: trabéculas, papilares e parede real, mais úteis para relevo interno. | Plastinação e spray alteram cor. Nenhuma subdivisão fina foi validada localmente. |
| [UMN Heart0064](https://sketchfab.com/3d-models/plastinated-human-hear-valve-view-heart0064-62abe2315c5648a8abc3d48bcced28bb) | Download e embed anunciados; CC Attribution-NonCommercial; 200 mil triângulos informados. | Relação espacial entre as quatro valvas em uma peça preparada. | Estado fixado não representa uma fase fisiológica simultânea. A descrição contém provável erro ao citar trabéculas no átrio direito; esse trecho foi excluído da recomendação. |
| [UMN MC_VALVES](https://www.vhlab.umn.edu/atlas/echocardiography-tutorial/exam-views-models.shtml) | Já local: quatro cortes, 1.457.632 triângulos. Redistribuição pública não confirmada. | Anatomia interna de cortes verdadeiros, referência já utilizável localmente. | Quatro cortes, não estruturas segmentadas. STL sem textura fotográfica; não republicar com uma licença presumida. |
| [APIL/Toronto General Hospital — Heart Base](https://sketchfab.com/3d-models/human-heart-base-fa8eba4530a84f758ac50df3b4e168f0) | Registro anterior: CC BY e download anunciado; não obtido. | Base e relações atrioventriculares de CT. | O próprio autor trata a junção como aproximação do esqueleto fibroso; não confirma anéis e trígonos individualmente. |
| [APIL — Full Patient Heart from CT](https://sketchfab.com/3d-models/full-patient-heart-from-ct-with-texture-ae1c46e7f44547b3aea4d79acdb6e6ab) | Registro anterior: CC BY, 493,5 mil triângulos e download anunciado; não obtido. | Forma derivada de CT com textura aplicada. | Textura produzida em ferramentas gráficas não equivale a fotografia do tecido. Valvas e relevo fino não inspecionados. |
| [KIT — Four-Chamber Heart v1.1](https://zenodo.org/records/10526554) | Arquivos de superfície e malha anunciados. CC BY-NC 4.0 confirmada no metadado da v1.0; API da v1.1 retornou 403, sem download. | Modelo científico de simulação a partir de RM, com câmaras e etiquetas materiais. | A camada pericárdica foi **adicionada como representação fenomenológica concêntrica**; não demonstra reflexões, seios e lâminas reais. Não preencher a lacuna anatômica com ela. |
| [Stephenson et al., condução humana por micro-CT](https://www.nature.com/articles/s41598-017-07694-8) | Artigo CC BY 4.0; dados completos **mediante solicitação aos autores**. Nenhuma malha pública obtida. | Fonte forte para SA, eixo AV e rede de condução, com limites e validação histológica discutidos pelos autores. | Licença do artigo não disponibiliza automaticamente os dados. Não foram enviados pedidos externos. |
| [Sato et al., fotogrametria de coração fixado](https://pmc.ncbi.nlm.nih.gov/articles/PMC10500340/) | Suplementos FBX 9,9 MB e STL 8,5 MB indicados no registro; acesso apresentou CAPTCHA. Arquivos não obtidos; licença dos suplementos não confirmada. | Aparência fotográfica de base cardíaca dissecada. | É uma preparação parcial, não coração completo; o acesso foi interrompido, sem contornar CAPTCHA. |
| [Miyazaki et al., pericárdio dorsal](https://pmc.ncbi.nlm.nih.gov/articles/PMC12667300/) e [Mori et al., espaço pericárdico](https://pmc.ncbi.nlm.nih.gov/articles/PMC8712969/) | Bloqueios e arquivos já documentados anteriormente; não repetidos. | O primeiro é mais próximo do tecido dorsal e suas reflexões. | O segundo representa espaço, não a parede pericárdica. Nenhum arquivo com redistribuição confirmada está disponível localmente. |

## O acervo HRA preparado

Arquivos de integração:

- `site/assets/heart-hra/model.glb`
- `site/assets/heart-hra/catalog.json`
- `site/assets/heart-hra/ATTRIBUTION.md`

O catálogo contém `groups`, `presets`, `model`, `orientation`, `limitations`, `sources` e 14 `parts`. Cada ID corresponde a um único nó/malha GLB. Cada peça tem nome fonte, fonte/licença, nota, `requirementIds`, `relatedRequirementIds`, `quizEligible`, triângulos e limites.

**Cinco correspondências amplas:** quatro câmaras e septo interventricular. As valvas são conjuntos, relacionados aos folhetos do roteiro; selecioná-las não prova cada folheto. As cinco peças papilares estão fora do treino por identificação conflitante, representação de porção ou falta de conferência. Nove identidades amplas permanecem elegíveis. O número de peças não deve ser adicionado como alvos novos confirmados à matriz de 178 requisitos.

Na fonte, o nó papilar `anterior` tem rótulo VE, embora sua localização seja compatível com o lado do VD. Nos nós anterolateral e posterior há divergências entre campos de identificador FMA. Essas inconsistências foram preservadas na auditoria, sem corrigir nomes silenciosamente.

### Transformação e integridade

Aplicou-se **uma única translação e escala positiva uniforme** a todos os vértices, sem rotação, deformação, segmentação artificial ou alteração da topologia. Orientação de exibição: +X esquerda, +Y superior, +Z anterior. A maior dimensão foi normalizada para 4 unidades; não usar a escala exibida como medida clínica. Normais e cores por vértice existentes foram mantidas no GLB.

- Original: SHA-256 `b1237e7e765178e9357fd2ea7ccf19d55d0bf9ca55e187886635febe28244c70`.
- Preparado: SHA-256 `9f21984a76ddaea65b9e21e6a7c6a6005979d4c187f9b18ae0c197b6c498f566`.
- 82.066 vértices / 164.119 triângulos preservados; nenhum índice fora do intervalo ou coordenada não finita.
- Erro máximo ao desfazer a transformação: 1,85 × 10⁻⁹ nas unidades de origem.
- A fonte já contém 820 faces de área zero no átrio direito. Não houve reparo automático, remoção de faces ou alegação de malha perfeita.
- Nenhuma imagem ou textura de imagem embutida. A malha tem um material de cor uniforme e alguns atributos de cor por vértice; isto não é fotografia anatômica.

A inspeção visual em seis vistas consta de `hra_inspecao.png`. A análise numérica e os metadados originais estão em `hra_inspection.json`. Os scripts `inspect_hra.py` e `prepare_hra.py` reproduzem a preparação. Esta etapa não executou o atlas no navegador; a integração e seu comportamento interativo requerem a conferência do agente responsável pela UI.

## Peças reais: integração recomendada

`pecas_reais_recomendadas.json` fornece três IDs, URLs, autores, licença exibida, preparação do espécime e limites. Usar iframe oficial carregado sob clique e mostrar a origem junto ao player. Manter um link para a página original se a incorporação falhar. Esses modelos dependem de rede, não alimentam o quiz local e não contam como cobertura validada do roteiro. Nenhum arquivo foi extraído do player.

## Lacunas e prioridade seguinte

1. **Relevo interno:** priorizar conferência da janela do VD do UMN188 e dos cortes UMN já locais. Aumentar brilho, rugosidade ou triângulos não cria anatomia ausente.
2. **Pericárdio:** buscar disponibilização regular do suplemento de tecido dorsal, com sua licença; manter lâminas/reflexões/seios pendentes até existir geometria correta. Uma cápsula concêntrica de simulação não serve de validação.
3. **Esqueleto fibroso:** a base APIL pode contextualizar a junção; não atribuir anéis ou trígonos sem delimitação sustentada.
4. **Condução:** o estudo micro-CT é uma referência anatômica, mas os dados precisam ser disponibilizados pelos responsáveis. Um traçado didático futuro deve ser marcado como esquema, separado de malha medida.

Também foram encontrados acervos oficiais [Boston Children’s/Mie University](https://sketchfab.com/heartmodels), ligados a [publicação de digitalização de peças](https://doi.org/10.1016/j.carpath.2025.107803), e o [3D Heart Project da University of Alberta](https://www.3dheartproject.com/model-library-collection/normal-teenage-heart). O segundo oferece principalmente volumes de sangue com miocárdio transparente; não é uma melhora direta de textura/relevo para a prova. As licenças individuais e o download dos candidatos adicionais não foram concluídos, portanto não foram integrados.
