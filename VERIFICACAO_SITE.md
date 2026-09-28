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
