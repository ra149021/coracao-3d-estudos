# Coração 3D local

Protótipo em português para explorar o coração em 3D e acompanhar a relação
com um roteiro de anatomia. A prioridade é fidelidade anatômica, com controles
didáticos. **O modelo ainda não cobre integralmente o roteiro.**

## Abrir

Requer Python 3 e um navegador com WebGL 2. Bibliotecas e peças já estão no
repositório; não é necessário instalar npm nem acessar a internet para usar.

```bash
python3 scripts/serve_heart.py --open
```

No Linux, também é possível executar `./Abrir_Coracao_3D.sh`. Deixe o terminal
aberto. Endereço padrão: <http://127.0.0.1:8765>. `Ctrl+C` encerra o servidor.
O serviço atende apenas o computador local. O HTML aberto diretamente como
arquivo não consegue carregar o modelo; use o iniciador.

## Plano de três etapas

1. **Prática do coração — em andamento.** Representar os alvos do roteiro, conferir relações anatômicas e oferecer exploração e treino. A referência principal são os materiais da professora. Dúvidas exigem Moore, Anatomy Learning ou fontes acadêmicas oficiais; uma fonte apenas localizada não é uma fonte efetivamente conferida.
2. **Teoria — depois da prática.** Organizar a teoria de coração/circulatório a partir dos slides e aulas disponíveis, com referências. Os horários de aula que já aparecem no roteiro são apoio à prática, não um módulo de teoria concluído.
3. **Refinamento e publicação pública.** Revisar anatomia, interface, acessibilidade, atribuição e arquivos redistribuíveis. Por enquanto, o GitHub funciona como backup privado.

## Versão atual — v0.2

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

As câmaras e peças internas Z foram extraídas de `Startup.blend`; os vasos Z vêm de `CardioVascular41.fbx`. A transformação comum preserva a disposição da fonte. Os limites das 17 peças compartilhadas entre esses arquivos foram comparados antes da integração.

Os complementos BodyParts3D receberam uma única transformação de similaridade, estimada por sete peças homólogas, com escala uniforme 1,0336 e diferença máxima das caixas envolventes de 0,3935 mm nominais. Isso verifica registro técnico, não precisão clínica. A rede vascular BP substitui integralmente a camada correspondente Z para evitar vasos duplicados. Veja `refinamento/geometria/README.md`.

Os 17 vasos de contexto foram extraídos do mesmo GLB Z, sem ajuste por peça ou corte. Os quatro cortes UMN mantêm uma transformação comum própria e não foram fundidos ao atlas.

## Organização

- `site/`: aplicação estática, dependências locais, modelo, créditos e auditoria.
- `scripts/serve_heart.py`: servidor local com biblioteca padrão.
- `scripts/build_heart_site_assets.py`: geração do GLB a partir dos dados de origem.
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
[NOTICE](site/LICENSES/NOTICE.txt). Não há arquivos de ouvido ou rim de outras licenças.

As notas breves usam o roteiro local e
[OpenStax, Heart Anatomy](https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy).

A referência local [UMN / Visible Heart Laboratories](https://www.vhlab.umn.edu/atlas/echocardiography-tutorial/exam-views-models.shtml) tem atribuição própria. Ela é mantida fora do Git; não está incluída na licença da geometria principal.
