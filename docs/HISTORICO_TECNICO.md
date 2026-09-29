# Registro histórico — conteúdo preservado

Este documento registra etapas anteriores e pode descrever estados já superados. Consulte o [README atual](../README.md) para conhecer a versão publicada.

# Atlas cardiorrespiratório — v0.4

Atlas em português para explorar coração e sistema respiratório em 3D, estudar a teoria e consultar o material docente local. A prioridade é fidelidade anatômica, com controles
didáticos. **O modelo ainda não cobre integralmente o roteiro.**

## Acesso público

**[Abrir o atlas por HTTPS](https://ra149021.github.io/coracao-3d-estudos/)**

O GitHub Pages serve os modelos, a teoria e os exercícios.

**Aulas gravadas e slides integrados em 29/09/2026, com publicação autorizada por Victor.** O progresso fica no
navegador de cada pessoa. A sala de aulas reúne sete videoaulas e seis documentos da professora Carmem: 354 páginas de slides e roteiro. As páginas são consultadas no próprio site; vídeos e PDFs originais ficam na release `aulas-v1`. As transcrições são automáticas e pesquisáveis.
Alterações enviadas para `main` atualizam o site pelo workflow `Publicar atlas`.

## Abrir localmente

Requer Python 3 e um navegador com WebGL 2. Bibliotecas e peças já estão no
repositório; não é necessário instalar npm nem acessar a internet para usar os
modelos locais. As três peças humanas no visualizador oficial requerem internet.

```bash
python3 scripts/serve_heart.py --open
```

No Linux, também é possível executar `./Abrir_Coracao_3D.sh`. Deixe o terminal
aberto. Endereço padrão: <http://127.0.0.1:8765>. `Ctrl+C` encerra o servidor.
O serviço atende apenas o computador local. O HTML aberto diretamente como
arquivo não consegue carregar o modelo; use o iniciador.

## Refinamento das estruturas — v0.4

- **Coração principal:** 72 peças e 482.116 triângulos. Foram avaliados os
  modificadores de superfície originais das quatro câmaras, com os parâmetros
  de renderização do autor. As outras 68 malhas permanecem idênticas; não há
  aumento artificial de cobertura anatômica.
- **Respiratório:** 175 peças, com oito vasos pulmonares proximais no registro
  original. A vista **Hilos e vasos pulmonares** permite observar suas relações
  com os brônquios e os lobos translúcidos.
- **HRA independente:** 14 peças, incluindo septo interventricular selecionável.
  As cinco peças papilares com identidade parcial ou conflitante estão fora do treino.
- **Peças anatômicas reais:** três referências oficiais UMN, abertas somente ao
  clicar, com orientações de observação ligadas às aulas. Não são parte da malha
  segmentada nem ampliam sua cobertura. Fixação e plastinação alteram a aparência.
- **Leitura do relevo:** iluminação lateral ou uniforme, sombras suaves opcionais
  e enquadramento melhorado. Cores continuam ilustrativas, sem textura de tecido.

Métodos, fontes e limites em [Qualidade 3D](../refinamento/qualidade/QUALIDADE_3D.md).
Conferências desta versão em [Verificação v0.4](../VERIFICACAO_QUALIDADE_3D.md).

## Estudo dos dois sistemas

A pedido do usuário, o escopo integra prática, teoria e aulas dos dois sistemas.

- **4 cenas interativas:** 72 peças de coração/contexto, 175 do respiratório Z-Anatomy, 40 de laringe BodyParts3D e 14 do coração HRA. Os conjuntos de fontes diferentes mantêm suas montagens independentes.
- **26 unidades de teoria e 94 questões originais:** 14 unidades/36 questões circulatórias; 12/58 respiratórias. Referências com páginas e horários, objetivos, tabelas, busca, revisão e progresso local.
- **Aulas e materiais:** 6 documentos, 354 páginas e 7 vídeos; transcrições pesquisáveis, velocidade e retomada. Vídeos e PDFs ficam na release; páginas renderizadas e transcrições integram o site.
- **Prática:** 178 alvos cardíacos e 222 respiratórios. O respiratório deriva dos slides disponíveis e inclui complemento identificado; não é um roteiro oficial de prova confirmado.
- **Cobertura respiratória na cena principal:** 85 alvos com peça associada, 71 com contexto parcial e 66 pendentes. Esses estados não certificam validação anatômica. Recessos pleurais, superfícies, espaços e microestruturas exigem figuras e teoria.
- **Navegação:** início, atlas, teoria e sala de aula. Rotação, seleção, isolamento, transparência, cortes, treino de identificação e links entre o texto e as peças.

Abra com `python3 scripts/serve_heart.py --open` ou `./Abrir_Atlas_Estudo.sh`. Não requer npm nem internet para estudar a instalação preparada. Para reconstruir a sala de aula a partir dos originais, use o Python com PyMuPDF em `scripts/build_classroom.py`; os caminhos são locais e ficam no manifesto ignorado.

Conferências de navegador e limites em [VERIFICACAO_CARDIORRESPIRATORIO.md](../VERIFICACAO_CARDIORRESPIRATORIO.md). Origem das malhas em [refinamento/respiratorio/geometria/README.md](../refinamento/respiratorio/geometria/README.md); revisão do conteúdo em [refinamento/respiratorio/conteudo/ENTREGA_CONTEUDO.md](../refinamento/respiratorio/conteudo/ENTREGA_CONTEUDO.md).

## Base cardíaca — histórico v0.2



- **72 peças prontas:** 55 cardíacas e 17 vasos de contexto, ocultos inicialmente.
- 152.303 triângulos; GLB principal de 3.771.380 bytes. Não foram geradas formas anatômicas novas.
- Cúspides anteriores mitral e tricúspide integradas; rede coronária e venosa organizada em 23 grupos de seleção.
- Uma porção papilar esquerda e um conjunto vascular com equivalência pendente são identificados como parciais e excluídos das perguntas.
- Rotação, zoom, movimento, seleção, isolamento, transparência, planos de corte e vistas anatômicas.
- **Prática:** identificar a peça destacada ou encontrar pelo clique; revelar resposta, registrar revisão, pausar e retomar. O progresso fica apenas neste navegador.
- **Roteiro:** 156 alvos principais e 22 complementos, pesquisáveis e associados à cena quando possível. Cada alvo apresenta critério de reconhecimento e referências disponíveis.
- Evidências docentes: 89 alvos com trechos localizados nas três transcrições e 33 com figuras/quadros inspecionados. O áudio não foi integralmente reescutado; ASR não é tratada como transcrição revisada.
- **Referência independente:** quatro cortes institucionais UMN em uma página própria, na instalação local. As malhas dessa referência não acompanham o Git porque a redistribuição não foi confirmada; a página oferece a fonte oficial quando os arquivos não estão instalados.

A primeira versão, com 39 peças, está preservada no commit inicial e na tag `v0.1-prototipo`.

### Situação da prática

O roteiro interativo distingue **65 alvos com peça associada, 54 com contexto parcial e 59 pendentes na cena**, somando os 178 alvos principais e complementares. Essas categorias não certificam anatomia. Uma peça nomeada pode omitir detalhes pedidos; referências institucionais separadas não aumentam a cobertura do modelo principal.

Faltam pericárdio e seus seios/reflexões, esqueleto fibroso, condução e vários relevos internos. As cordas integram as malhas dos folhetos. O conjunto papilar anterior esquerdo permanece parcial. Óstios, continuidade de vasos, inserções de cordas, superfícies e sulcos precisam de revisão individual. As malhas do atlas têm simplificações e não possuem textura fotográfica. Cortes visuais não recebem tampas artificiais.

**100% de correlação ainda não foi demonstrado.** O levantamento dos acervos é histórico e distinto da cena: 70 dos 156 alvos principais tinham geometria associada, 47 eram parciais e 39 não localizados. A integração de novas peças não converte esses estados automaticamente em validação anatômica.

### Fontes geométricas e transformações

As câmaras e peças internas Z foram extraídas de `Startup.blend`; os vasos Z vêm de `CardioVascular41.fbx`. A transformação comum preserva a disposição da fonte. Os limites das 17 peças compartilhadas entre esses arquivos foram comparados antes da integração. Na v0.4, as quatro câmaras usam a superfície avaliada com os modificadores originais do autor; os outros 68 conjuntos de posições, normais e índices foram preservados integralmente.

Os complementos BodyParts3D receberam uma única transformação de similaridade, estimada por sete peças homólogas, com escala uniforme 1,0336 e diferença máxima das caixas envolventes de 0,3935 mm nominais. Isso verifica registro técnico, não precisão clínica. A rede vascular BP substitui integralmente a camada correspondente Z para evitar vasos duplicados. Veja `refinamento/geometria/README.md`.

Os 17 vasos de contexto foram extraídos do mesmo GLB Z, sem ajuste por peça ou corte. Os quatro cortes UMN mantêm uma transformação comum própria e não foram fundidos ao atlas.

## Organização

- `site/`: aplicação estática, dependências locais, modelo, créditos e auditoria.
- `scripts/serve_heart.py`: servidor local com biblioteca padrão.
- `scripts/build_heart_site_assets.py`: geração do GLB a partir dos dados de origem.
- `scripts/evaluate_heart_author_surfaces.py`, `prepare_author_heart_candidate.py` e `promote_author_heart.py`: avaliação, comparação e promoção das superfícies cardíacas v0.4 (requerem os acervos originais, Blender Python e NumPy locais). O gerador inicial isoladamente reconstrói a superfície anterior.
- `matriz_coracao.json` / `.csv`: todos os alvos e suas evidências.
- `RELATORIO.md`: método da auditoria.
- `output/playwright/`: evidências de verificação de interface.
- `refinamento/`: evidências das aulas, registro geométrico e próximas estruturas.
- `site/study.js`: treino e roteiro.
- `site/reference.html`: visualizador da referência local independente.

Arquivos de aula originais, credenciais, ambientes Python, dependências npm e
downloads brutos não fazem parte do repositório. A aplicação pronta não depende
deles. Os scripts de extração requerem os acervos locais indicados na auditoria;
`site/assets/` contém o resultado já preparado.

## Créditos e licenças

Geometria: [Z-Anatomy](https://github.com/Z-Anatomy/Models-of-human-anatomy),
Gauthier Kervyn e colaboradores; aplicação por Lluis Vinent; base de
BodyParts3D / Kousaku Okubo / The Database Center for Life Science.
Os complementos do download independente BodyParts3D têm **CC BY 4.0**; a montagem com Z-Anatomy é distribuída sob **CC BY-SA 4.0**.
Avisos históricos da origem são preservados em `site/LICENSES/`.
Three.js 0.186.1 usa licença MIT. Consulte os avisos completos em
[NOTICE](../site/LICENSES/NOTICE.txt). Não há arquivos de ouvido ou rim de outras licenças.

As notas breves usam o roteiro local e
[OpenStax, Heart Anatomy](https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy).

A referência local [UMN / Visible Heart Laboratories](https://www.vhlab.umn.edu/atlas/echocardiography-tutorial/exam-views-models.shtml) tem atribuição própria. Ela é mantida fora do Git; não está incluída na licença da geometria principal.

O [coração HRA](https://3d.nih.gov/entries/3DPX-021000) usa CC BY 4.0, com
[atribuição própria](../site/assets/heart-hra/ATTRIBUTION.md). As três peças UMN
da página `specimens.html` são incorporadas do visualizador oficial, com licença
e condições indicadas junto de cada peça; seus arquivos não são redistribuídos.
