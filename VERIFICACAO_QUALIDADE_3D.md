# Verificação da qualidade 3D — v0.4

29/09/2026. Conferência técnica e funcional; não certifica cobertura integral
do roteiro, precisão clínica nem identificação individual de todos os relevos.

## Geometria

- Coração: 72 peças, 482.116 triângulos, 11.708.588 bytes. Apenas as quatro
  câmaras mudaram após avaliar os modificadores originais do autor. Posições,
  normais e índices das outras 68 malhas são idênticos à v0.3.
- Coordenadas finitas, índices válidos e normais unitárias conferidos nas 72 peças.
  Hashes e comparação em `refinamento/qualidade/heart_author_validation.json`.
- Respiratório: 175 peças, 959.255 triângulos; verificação geométrica documentada
  em `refinamento/respiratorio/geometria/asset_validation.json`.
- HRA: 14 peças independentes; cinco conjuntos papilares excluídos das perguntas.
  As 820 faces degeneradas do átrio direito já existentes na fonte são preservadas.

## Navegador local

Chromium 153, WebGL 2, janela de 1440 × 1000; nenhuma exceção JavaScript de página
nos fluxos abaixo. Não foi medido desempenho em celulares físicos.

- Coração principal carrega o GLB refinado. Rotação e zoom por teclado alteram
  a câmera. Interior e corte sagital funcionam; sombras de profundidade pausam
  quando há corte ou transparência, preservando a leitura das superfícies.
- Vista Hilos: 42 peças visíveis, lobos a 85% de transparência; oito vasos novos
  aparecem com a árvore brônquica. Roteiro: 85 associados, 71 parciais, 66 pendentes.
  Treino respiratório: 131 peças elegíveis.
- HRA: 14 peças carregadas, 9 elegíveis; botão Créditos abre o diálogo correto.
  Rodada de septo: revelar identifica o septo interventricular, revisão registra
  1 de 1, voltar restaura luz uniforme, sombras desligadas e nomes fora do modo prova.
- Tela de 390 × 844: início, coração, respiratório, HRA e peças reais sem
  transbordamento horizontal do documento (largura medida: 390 px).

## Peças reais incorporadas

- Abertura da página: zero iframes e zero requisições externas. O clique cria
  somente o iframe oficial. Troca de peça e Encerrar removem o player anterior.
- UMN 612, 188 e 064 concluíram o carregamento. A peça 064 foi arrastada no player
  e sua renderização conferida visualmente; a 188 também teve captura inspecionada.
- Durante o carregamento externo apareceram avisos transitórios do provedor.
  Eles desapareceram após a conclusão. A interface informa a espera e oferece
  Abrir na fonte; o evento de carga do iframe não é tratado como prova de carga 3D.
- Capturas desses players permanecem fora do Git. Fontes, preparação e licenças
  acompanham cada peça; nenhuma correspondência segmentada é afirmada.

## Conteúdo e arquivos

- JSONs do site lidos sem erro; sintaxe dos módulos alterados conferida.
- `git diff --check` passou para o código próprio. Os arquivos Three.js novos
  são cópias integrais da dependência; espaços originais foram preservados.
- Divergência do slide 43 e correções de referências documentadas em
  `refinamento/qualidade/REVISAO_ACADEMICA.md`.
- Preparação da publicação: `refinamento/qualidade/PUBLICACAO.md`.

Capturas do atlas local: `output/playwright/36-heart-quality.png`,
`37-hilo-quality.png` e `38-hra-quality.png`.

Verificações anteriores de teoria, aulas locais, retomada e servidor permanecem
registradas em `VERIFICACAO_CARDIORRESPIRATORIO.md`.
