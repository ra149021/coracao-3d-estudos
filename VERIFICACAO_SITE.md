# Verificação da primeira versão — 28/09/2026

Navegador Chromium real, contexto isolado, WebGL 2, Playwright CLI.
Cena com 39 peças e 129.008 triângulos; GLB de 3.235.248 bytes.

## Verificado por interação no navegador

- Carregamento de todas as 39 peças e renderização sem erro de JavaScript.
- Arrastar modifica a câmera; roda do mouse modifica o zoom.
- Seleção pela lista, isolamento e ocultação de uma peça.
- Recuperação de cena vazia e restauração das 39 peças.
- Busca de estruturas.
- Modo valvas/papilares: 13 peças, com aviso de conjunto incompleto.
- Corte frontal, sagital e transversal; inversão do lado do corte.
- Modo coronário: 14 peças, paredes com transparência de 72%.
- Mudança de paleta, vista posterior e diálogo de fontes.
- Largura de 390 px sem transbordamento horizontal.
- Ausência de solicitações externas durante o funcionamento local.

Capturas em `output/playwright/`: visão geral, valvas, interior e largura móvel.
Visão geral, valvas e interior foram também inspecionados visualmente.

O Chromium emitiu avisos de desempenho de leitura de pixels da GPU durante
a captura de imagens; não houve erro de carregamento ou de JavaScript.
Não foram medidos FPS em outros computadores. O layout móvel foi verificado
por tamanho de janela, sem ensaio de gestos em um aparelho físico.

Essas verificações demonstram funcionamento técnico. A identificação detalhada,
proporções, conexões e cobertura anatômica integral continuam pendentes.


## Refinamento v0.2 — 28/09/2026

### Geometria e material docente

- 72 malhas carregadas: 55 cardíacas, 17 vasos de contexto. GLB: 152.303 triângulos, 3.771.380 bytes.
- 17 vasos de contexto extraídos do mesmo GLB Z, com transformações preservadas, hashes/índices/finitude e contagens conferidos.
- Cúspides e rede BP registradas por uma transformação comum: método, evidências visuais e limites em `refinamento/geometria/README.md`.
- Roteiro: 178 IDs preservados; filtros retornam 156 principais e 22 complementares.
- Situação da cena: 65 IDs com peça associada, 54 com contexto parcial, 59 pendentes. Nenhum número equivale a validação anatômica individual.
- Evidências sanitizadas: 178 critérios, 89 alvos com trechos ASR e 33 com figuras/quadros. Páginas/horários apresentados no diálogo de roteiro; sem publicar PDFs ou vídeos originais.

### Interações verificadas em Chromium / WebGL 2

- Cena inicial mostra 55 de 72 peças; contexto opcional mostra 33 (câmaras, grandes vasos e os 17 vasos adicionais).
- Modo de identificar: revelar, marcar revisão, completar quatro questões e rever somente o item marcado.
- Modo de encontrar: clique real em peça incorreta mantém pergunta; clique real na peça solicitada revela resposta. Os pontos foram recalculados após a altura da mensagem de feedback mudar.
- Treino usa 53 peças: exclui as duas parciais e os 17 contextos ainda em revisão. Nomes laterais/hover ocultos e botão de restauração/tela cheia desativados durante pergunta.
- Câmera, seleção, visibilidade, transparência, vista ativa e controles restaurados ao pausar/concluir.
- Progresso persiste após recarregar no mesmo contexto de navegador.
- Foco transfere do botão de revelar para autoavaliação e volta a Prática ao pausar.
- Abrir peça pelo roteiro limpa corte anterior; conteúdo docente com fonte/página/horário é legível.
- Rotação e zoom por teclado; controles por mouse previamente verificados.
- Layout de 390 px sem transbordamento horizontal; diálogo de roteiro com 356 px sem transbordamento interno.
- Nenhuma solicitação externa durante uso do atlas principal; nenhum erro JavaScript no ciclo final.
- `node --check` passou para app.js, study.js e reference.js; `git diff --check` sem problemas.

### Referência institucional local

- Quatro cortes UMN, 1.457.632 triângulos preservados, GLB de 34.961.936 bytes.
- Renderização, seleção, conjunto completo, transparência, paleta, enquadramento, lado oposto, zoom, teclado e pausa de rotação verificados.
- Layout móvel sem transbordamento. Ausência simulada do catálogo exibiu orientação para obter o arquivo na fonte oficial; nenhum arquivo do usuário foi removido para esse ensaio.
- O HTTP 404 desse ensaio é intencional. Não houve erro JavaScript de aplicação.
- Arquivos e capturas dessa referência estão ignorados no Git; não há licença permissiva de redistribuição confirmada.

Capturas atuais: `11-identificar-valva.png`, `12-roteiro-com-fontes.png`, `13-contexto-vascular.png`, `14-mobile-atual.png`, `15-roteiro-mobile.png` e `18-visao-geral-atual.png`.

Essas verificações comprovam os fluxos observados neste navegador. Não são revisão especializada da anatomia, ensaio em aparelho móvel físico ou demonstração de cobertura integral do roteiro.
