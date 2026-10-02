# Teoria, figuras e prática — verificação de 30/09/2026

Esta etapa implementa as prioridades 1–5 de [Melhorias fundamentadas no conteúdo](../REVISAO_CONTEUDO_SITE.md). Ao estudar uma seção, agora é possível conferir seus slides, comparar duas páginas e abrir o item pertinente do roteiro, uma vista regional ou uma peça humana.

## Comportamento entregue

- **Figuras por seção:** 108 das 109 seções têm páginas selecionadas entre suas próprias referências, com 205 associações. A seção sobre números de papilares, sem página docente própria, conserva sua referência acadêmica sem uma figura substituta. Cada galeria mostra no máximo duas páginas simultâneas, com troca de página, comparação e acesso ao slide na biblioteca. As páginas originais e suas legendas foram preservadas.
- **Revisão visual:** dez tarefas abertas, quatro circulatórias e seis respiratórias, separadas das 94 perguntas textuais anteriores. Incluem seios pericárdicos, detalhes dos átrios, aparelho subvalvar, cavidades laríngeas, pleura e unidade alveolar. Os enunciados pedem comparação e explicação diante da imagem com legendas, sem anunciar identificação às cegas.
- **Progresso:** a chave de cada sistema continua sendo `atlas:theory:<system>`. Leitura e respostas textuais anteriores são preservadas; tarefas visuais usam `visualAnswers` e IDs próprios. Contadores distinguem os tipos, inclusive no celular. Os registros da prática 3D permanecem separados.
- **Roteiro na teoria:** cada unidade lista seus alvos, fonte/página, critério e referências, com as mesmas classificações da cena base: peça associada, contexto parcial ou pendente. O link `atlas.html?system=...&mode=route&requirement=...` abre o item exato e suas evidências, ajustando os filtros. Um ID ausente recebe aviso.
- **Vistas e tabelas:** vistas existentes aparecem nas unidades/seções pertinentes. Os 19 códigos B das tabelas direita/esquerda abrem o brônquio no lobo correspondente. A câmera mantém o enquadramento da vista quando a peça pertence a ela; links somente para uma peça continuam aproximando essa peça. Códigos S permanecem texto, pois o ramo brônquico não demonstra o volume segmentar.
- **Peças humanas:** quatro cartões contextualizados ligam as seções de ventrículos/aparelho subvalvar e valvas às peças UMN 188/064. Tarefas e limites são derivados do catálogo existente. A teoria não incorpora nem carrega automaticamente os modelos externos.

As imagens de Coração 31, 37, 57 e 58 e Respiratório 72, 73, 110, 112, 118, 131 e 132 foram inspecionadas diretamente durante a curadoria. Não foram criados hotspots, apagadas legendas ou atribuídas fases funcionais aos quadros endoscópicos por sua numeração. As figuras alveolares são esquemas de microanatomia, sem indicação de treino em micrografias.

## Evidência de verificação

| Conferência | Resultado observado |
| --- | --- |
| Preservação editorial | Removendo apenas os novos campos `figures` e `visualRecall`, os dois JSON são estruturalmente idênticos à base `ab68092`. Os 94 IDs e perguntas textuais anteriores foram preservados. |
| Integridade local | JSON, IDs exclusivos, páginas/fontes, JPGs presentes, peças e alvos válidos; `python3 scripts/verify_theory_study.py` passou. |
| Links de integração | 1.714 links gerados conferidos contra arquivos e IDs locais; 19 vínculos B e quatro cartões UMN válidos. |
| Navegação teórica | Os 26 capítulos e 109 seções renderizados no Chromium; 108 galerias com no máximo duas páginas e figuras das referências corretas; sem erro JavaScript no percurso. |
| Progresso | Estado anterior com leitura/resposta textual carregado; resposta visual não alterou respostas textuais; resposta textual não alterou tarefas visuais; persistência confirmada após recarregar. |
| Comparação | Pericárdio, seção dos seios, abre pp.57–58; alternar página, ativar/desativar comparação e trocar seletores não duplica a página. |
| Links exatos do roteiro | `63a` e `R098` abertos com critérios/evidências; `R099` recuperado após filtros incompatíveis; ID inexistente recebe aviso. |
| Classificações | Cena cardíaca: 65 peças associadas / 54 contextos / 59 pendências; respiratória: 92 / 71 / 59, iguais ao módulo prático. Nenhuma cobertura foi promovida. |
| Enquadramento B4 | Link da tabela abriu `arvore_medio_direito` e o ramo B4 direito; câmera e alvo iguais aos da vista sem seleção. |
| Telas pequenas | Átrios, laringe, tabelas B/S e alvéolos testados em 320, 390 e 720 px; nenhum overflow horizontal do documento. Figuras empilhadas, imagens carregadas e contadores móveis visíveis. |
| Recuperação de falhas | 404 de imagem exibe aviso e conserva acesso à fonte. Matriz do roteiro indisponível não impede leitura ou revisão e recebe aviso próprio. |
| Impressão | Controles das galerias ocultos no modo de impressão. |
| Revisão técnica | Revisão independente dos diffs, sintaxe dos cinco módulos JavaScript e `git diff --check`, sem erro encontrado. |

Os dois 404 registrados no console foram injetados nos testes de recuperação. As cenas WebGL emitiram avisos de desempenho de `ReadPixels` no navegador de teste, sem falha de carregamento ou erro JavaScript.

## Reproduzir as conferências locais

```bash
python3 scripts/verify_theory_study.py
node --check site/theory.js
node --check site/theory-figures.js
node --check site/theory-connections.js
node --check site/study.js
node --check site/app.js
git diff --check
python3 scripts/serve_heart.py --port 8895 --open
```

No navegador, conferir `theory.html?system=circulatory&chapter=circ-pericardio`, a revisão visual de `resp_06`, as tabelas de `resp_08` e os alvos `63a`/`R098` no roteiro. Capturas da verificação: [comparação pericárdica](../../../output/playwright/teoria-visual-pericardio.png), [tarefa laríngea](../../../output/playwright/teoria-visual-laringe.png), [figuras no celular](../../../output/playwright/teoria-visual-mobile.png) e [B4 no contexto do lobo](../../../output/playwright/teoria-visual-bronquio.png). São registros da interface, sem criação de novos slides ou materiais de autoria docente.

## Limites e continuação

Esta entrega conecta recursos existentes e tarefas visuais; não acrescenta geometria, validação anatômica individual ou confirmação de incidência na prova. Comparação com peça humana não aumenta a cobertura do atlas. Aulas/transcrições e os visualizadores externos mantêm seus limites prévios.

As prioridades 6–10 do levantamento continuam como atividades específicas a desenvolver: sequências guiadas de pleura, percursos com checkpoints, mudança de escala alveolar, drenagem nasal e topografia linfática. Figuras e conexões já podem apoiar parte dessas atividades, mas não substituem seus futuros exercícios.

A etapa foi preparada sobre `feat/geometria-mediastino`, cuja ampliação está no PR #5. Publicação depende da integração das duas etapas; este relatório documenta testes locais, não uma publicação em GitHub Pages.
