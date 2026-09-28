# Revisão de integração — 28/09/2026

## Escopo e método

Leitura de `site/app.js`, `study.js`, `theory.js`, `classroom.js`, `home.js`, páginas HTML relacionadas e `scripts/serve_heart.py`. Conferência dos catálogos, dos destinos estáticos dos links e da existência dos arquivos declarados no manifesto local. Esta revisão não executou navegador nem reproduziu os fluxos por interação gráfica.

## Achados e correções conferidas no código

| Achado | Correção observada |
| --- | --- |
| Respiratório completo e laringe independente compartilhavam a chave da prática. Ao trocar de acervo, a filtragem pelos IDs presentes descartava os itens restantes da outra rodada. | `storageId` separa persistência e resumo da laringe; `system` continua identificando o sistema respiratório. O início contabiliza também o resumo da laringe. |
| As teclas `+` e `-` aplicavam fatores de zoom com efeito inverso no `OrbitControls` vendorizado. | As chamadas agora usam `1/1.12`, aproximando com `+` e afastando com `-`. |
| Um link de aula com `t=0` era convertido em ausência de horário e retomava a posição salva. | `params.has('t')` preserva o zero explícito. |
| A cópia pública `site/auditoria/verificacao.json` continha três caminhos absolutos da máquina. | Os campos `path` foram reduzidos aos nomes dos PDFs; IDs, páginas e hashes foram preservados. |

As três correções de UI foram realizadas pelo agente responsável pela integração e conferidas por leitura. Nesta etapa, o revisor alterou somente a cópia pública da auditoria e este relatório.

## Conferências de integridade e materiais locais

- Os destinos locais estáticos de `href` e `src` nas páginas HTML existiam no momento da revisão.
- Os 6 documentos, 7 vídeos e 7 transcrições declarados no manifesto local estavam presentes. Também estavam presentes todas as páginas renderizadas declaradas para os documentos.
- A teoria respiratória e seus IDs de peças estavam disponíveis no catálogo correspondente ao final da revisão.
- O servidor vincula-se a `127.0.0.1`. As rotas `/local/` resolvem IDs declarados no manifesto e não aceitam um caminho de arquivo fornecido pelo cliente.
- O manifesto e os arquivos docentes ficam fora de `site`; a listagem de diretórios está desabilitada. A consulta ao índice do Git não encontrou PDFs, vídeos ou arquivos de `materiais/` rastreados.

## Limites

Esta revisão não demonstra comportamento visual, reprodução audiovisual, desempenho, compatibilidade entre navegadores ou validação anatômica completa. As conferências de proteção descrevem o código e os arquivos observados; não constituem uma auditoria completa de segurança. Mudanças posteriores devem ser verificadas novamente. Não houve alteração de Git, publicação ou configuração do sistema.
