# Aulas gravadas e slides — 29/09/2026

Integração da sala existente com quatro vídeos respiratórios e três circulatórios.
Sem revisão ou análise do conteúdo dos vídeos. Reutilizadas as transcrições automáticas já existentes, apenas para busca e navegação.

Seis documentos da biblioteca local: coração (75 páginas), vasos (44), linfático (56), respiratório (144), roteiro circulatório (5) e mediastino (30). Total: 354 páginas. Imagens preservadas da renderização local; PDFs originais preparados para a release `aulas-v1`.

Verificações realizadas:
- Integridade das 354 imagens e correspondência das contagens com os PDFs.
- Abertura dos seis documentos pelo site estático, sem depender das rotas `/local/page`.
- Avanço de página, limite superior e bloqueio do botão na última página.
- Layout de 390 px sem transbordamento horizontal.
- Metadados de reprodução dos sete vídeos e carregamento das transcrições na instalação local.
- Reprodução e salto pelo resultado da busca no vídeo C1.
- Filtro respiratório: quatro aulas e dois documentos, incluindo mediastino.
- Nenhum erro JavaScript durante esses fluxos; o servidor estático local responde 404 à consulta opcional `/local/status`, como esperado.
- `node --check` e compilação sintática dos scripts Python.

Evidências locais, ignoradas pelo Git: `output/playwright/aula-local-slides-mobile.png` e `output/playwright/aula-local-video.png`.

Victor confirmou explicitamente a publicação pública dos sete vídeos e seis documentos em 29/09/2026. Os arquivos são publicados na release `aulas-v1`; as páginas e os índices integram o GitHub Pages. Os 13 arquivos da release tiveram tamanho e SHA-256 comparados com as cópias locais, sem diferenças. Reprodução da aula R1 a partir do GitHub confirmada no navegador em 1920 × 1080. A implantação do site é conferida após a atualização de main.
