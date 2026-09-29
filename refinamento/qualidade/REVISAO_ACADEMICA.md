# Revisão acadêmica das peças reais e referências relacionadas

Data: 29/09/2026. Escopo: textos, metadados, licenças declaradas, referências docentes e alcance das afirmações. Revisão de arquivos e imagens locais, com consulta às páginas institucionais indexadas; nenhum navegador ou player foi executado. Após o relato inicial, foram autorizadas as correções pontuais de conteúdo descritas abaixo. Esta revisão não valida individualmente a anatomia das malhas ou dos modelos externos.

## 1. Correção aplicada: referência ao slide 43 de Coração

**Prioridade alta; confiança alta na divergência de legendas.** A imagem docente da página física 43 de Coração apresenta a legenda “Válvulas AVE” apontando para um conjunto desenhado com três cúspides e “Válvulas AVD” apontando para um conjunto com duas. A figura da página 47 identifica corretamente as relações AVE/mitral e AVD/tricúspide. Para aprender a identificação, a página 43 precisa de uma nota de correção; seu original deve ser preservado.

A nomenclatura institucional da Universidade de Minnesota confirma: mitral é a valva atrioventricular esquerda, com dois folhetos principais; tricúspide é a direita, com os folhetos anterior, posterior e septal. [Visible Heart Laboratories — Cardiac Valve Nomenclature](https://www.vhlab.umn.edu/atlas/anatomy-tutorial/cardiac-valve-nomenclature.shtml).

### Evidência visual local

- `materiais/classroom/coracao/43.jpg`: figura com as legendas em conflito; SHA256 `917145f538320a656c3ef9d5886dc09abc63fe7a06532516ffc1b5492c48f4ff`.
- `materiais/classroom/coracao/47.jpg`: figura de comparação, com AVE à esquerda da imagem e AVD à direita; o número de folhetos e as relações nomeadas são concordantes. SHA256 `29e9917ffd0ef67aa5d801e6391bdf8ce2594665714838ab652aa5a0d230e23e`.
- `requisitos.json`: itens 46a–c (tricúspide anterior/posterior/septal), 58a–b (mitral anterior/posterior). O roteiro é referenciado nas páginas físicas 2 e 3.

### Mudança das referências em `site/assets/specimens.json`

| Peça | Orientação | Referências anteriores | Referências após a correção |
|---|---|---|---|
| UMN 188 | Passe da parede ventricular à saída arterial | Coração 42, 43, 45 | Coração 42, 47, 45 |
| UMN 064 | Construa um mapa das quatro valvas | Coração 43, 47 | Coração 47 |
| UMN 064 | Compare valvas atrioventriculares e semilunares | Coração 42, 43 | Coração 42, 47 |

As referências à página 47 foram deduplicadas. A tabela registra a substituição do slide 43; links adicionais para as páginas do roteiro foram incluídos depois, conforme a seção 2. Não foram alterados os slides, os IDs do roteiro, a identificação das peças, os links oficiais, o mecanismo do player ou as afirmações de cobertura.

### Teoria e sala de aula

`site/assets/circulatory-theory.json`, capítulo `circ-valvas`, já continha a tabela correta em “Quatro valvas: nomes e relações”, mas não havia nota explícita sobre a troca de legendas. Foi acrescentado um parágrafo breve nessa seção, com referência a Coração 47 e à fonte institucional `vhl-valve-nomenclature`, cadastrada em `sources` com a URL da UMN. A tabela foi preservada.

Referências ambíguas foram substituídas: Coração 43 → 47 em “Quatro valvas: nomes e relações”; Coração 43 → 42 em “Folhetos, seios e óstios são estruturas distintas” e na questão `circ-q14`. Duplicatas foram removidas. As seções mantêm também suas outras referências, incluindo as figuras específicas de seios e válvulas semilunares.

`site/classroom.js` não dispõe de notas específicas por documento/página. Há apenas uma legenda genérica recomendando comparação com as notas da teoria. Não foi criada estrutura nova de notas.

**Nota editorial agora publicada na seção de teoria:** “Nota sobre a figura docente: na página física 43 de Coração, as legendas AVE e AVD parecem trocadas. A mitral é a valva atrioventricular esquerda, com dois folhetos principais; a tricúspide é a direita, com três. Para identificar, compare a página 47 e a nomenclatura do Visible Heart Laboratories. A imagem original da aula foi preservada.”

## 2. Outros pontos concretos e encaminhamento

| Prioridade | Local | Achado e encaminhamento | Confiança |
|---|---|---|---|
| Média | UMN 064, `focus` | “Vista superior da base” pode confundir a vista das quatro valvas com a base anatômica posterior do coração, cobrada no item 14. **Corrigido para “vista das quatro valvas”**. A fonte original descreve uma vista das quatro valvas; não exige essa expressão sobre a base. | Alta sobre a ambiguidade; não se trata de afirmar que todo uso clínico de “basal” seja incorreto. |
| Média | UMN 612, orientação sobre sulcos e vasos | Coração 22 confirma os sulcos, mas não nomeia as coronárias e seus ramos relacionados nos IDs 81, 83, 103 e 104. **Acrescentados links** para Vasos 22 (coronária direita), 25 (coronária esquerda e ramos) e 33 (comparação venosa). | Alta após leitura dos textos e inspeção visual das quatro figuras locais. Esses vínculos não equivalem a validar todas as legendas das páginas nem a individualizar vasos na peça UMN. |
| Média | UMN 188, “Observe a transição entre entrada e saída” | A descrição do autor confirma janela no VD, trabéculas, papilares e vista superior aórtica. Ela não confirma exposição adequada do infundíbulo ou da crista supraventricular nessa preparação. A instrução atual contém condicionantes, mas o título pode sugerir disponibilidade já conferida. Preferir “Compare entrada e saída do ventrículo direito” e manter a identificação condicionada às relações efetivamente visíveis. | Alta sobre o limite da evidência textual; visibilidade concreta permanece pendente de inspeção do player. |
| Baixa | Orientações e itens do roteiro | Os IDs são válidos e pertencem ao roteiro, mas eram exibidos sem ligação para suas páginas. **Acrescentados links** em `specimens.json` para `classroom.html?doc=roteiro&page=1`, `2`, `3` ou `4`, conforme o campo `pagina` de cada requisito relacionado. Foi reutilizado o renderizador existente, sem alterar `specimens.js`. | Alta, por leitura do código e de `requisitos.json`. |
| Baixa | `atlas.html`, diálogo “Sobre” | “70 de 156” corresponde ao subconjunto principal do catálogo, enquanto o levantamento completo tem 178 alvos com os complementos. Acrescentar “alvos principais” evita comparar esse denominador com o total ampliado. O texto já distingue associação e validação, portanto não há promessa de cobertura de 90%. | Alta, por `catalog.coverage.principal` e `complemento_docente`. |

## 3. Metadados e limites conferidos

As três páginas originais indexadas identificam **VisibleHeartLabs** como autor e exibem a licença **CC Attribution-NonCommercial**. Os identificadores, títulos originais e URLs de incorporação correspondem aos modelos selecionados. O catálogo público preserva o rótulo da licença sem inferir uma versão. As atribuições CC BY/CC BY-SA do atlas local não foram reaplicadas aos modelos Sketchfab.

- [UMN 612 — fonte original](https://sketchfab.com/3d-models/perfusion-fixed-human-heart-anatomy-612-f6d63aea48a14d27969067f2754c2d3b): descrição de fixação por perfusão, digitalização em até dois dias, doador de 64 anos e destaque de vasos coronários/aurícula direita conferem com os metadados utilizados. A declaração sobre cores é atribuída à fonte e acompanhada do limite de identificação pela cor.
- [UMN 188 — fonte original](https://sketchfab.com/3d-models/plastinated-whole-human-heart-188-d4cc3d373db24d3ca9d08907d620d078): plastinação, janela no VD, doadora de 61 anos, spray de digitalização e observação superior da valva aórtica constam na descrição do autor.
- [UMN 064 — fonte original](https://sketchfab.com/3d-models/plastinated-human-hear-valve-view-heart0064-62abe2315c5648a8abc3d48bcced28bb): preparação plastinada, doadora de 89 anos, spray e posições fixadas das quatro valvas constam na descrição. O lapso original que associa trabéculas cárneas ao átrio direito foi excluído dos textos públicos. A nota de não inferir uma fase fisiológica a partir dessa preparação está mantida.

Os campos `countsTowardLocalCoverage:false` e `quizEligible:false` estão presentes nos três modelos. Os textos não afirmam correspondência segmentada, cobertura integral ou validação individual. Os modelos UMN incorporados são distintos da referência local `MC_VALVES`, cuja licença de redistribuição não foi confirmada e cujo limite está explícito em `reference.html`.

Todos os IDs de requisito mencionados em `specimens.json` existem em `requisitos.json`. As páginas docentes citadas estão dentro do documento Coração, com 75 páginas físicas. A rota gerada em `specimens.js` corresponde ao parâmetro `doc` lido em `classroom.js`. A disponibilidade e a interação dos embeds dependem de conferência no navegador pelo agente responsável; não foram atestadas aqui.
