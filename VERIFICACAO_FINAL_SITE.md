# Revisão funcional final do atlas

Revisão em 29/09/2026, para apresentação a professores e colegas. Verificações em Chromium, no site publicado e em uma cópia estática das alterações.

## Correções

| Situação reproduzida | Resultado corrigido |
| --- | --- |
| Digitar uma página além do limite, já na última página dos slides | O campo volta ao número válido, de acordo com a imagem e a URL. |
| Avançar uma videoaula antes de carregar seus metadados | Os controles aguardam o carregamento e não causam erro JavaScript. |
| Selecionar um trecho da transcrição antes de o vídeo carregar | O ponto escolhido aguarda o vídeo e é aplicado quando disponível. |
| Progresso de teoria ou posições de aulas com valores nulos ou inválidos | As páginas continuam abrindo; campos válidos são preservados. |
| Contadores e avaliações salvos com tipos inesperados | Dados inválidos são ignorados, evitando contagem incorreta ou falha na revisão. |
| Abrir os cortes complementares sem os arquivos da instalação local | A página apresenta a fonte institucional diretamente, sem buscar arquivos ausentes nem mostrar controles de um modelo indisponível. |

## Verificações realizadas

- Abertura da página inicial, quatro cenas 3D, teoria dos dois sistemas, aulas, peças anatômicas, referência e página sobre o projeto.
- Prática nos quatro conjuntos: iniciar, revelar resposta, avaliar, pausar, recarregar e continuar. Seleção, peças visíveis, paleta e corte restaurados ao voltar à exploração. Nenhum erro JavaScript nesses fluxos.
- Conclusão de rodada do coração, busca no roteiro e controles de câmera por teclado.
- Recuperação de dados de progresso inválidos, preservação da leitura após recarregar, navegação dos slides e controles de vídeo antes e depois do carregamento.
- Dez páginas verificadas em larguras de 320, 390 e 768 pixels, sem rolagem horizontal indevida. Nova página institucional também verificada em 1440 pixels.
- Integridade dos índices: 94 questões, 656 referências de teoria, IDs das estruturas e páginas citadas nos documentos.
- Quatro arquivos GLB, sete transcrições e 354 páginas de slides versionados no repositório. Os sete vídeos e seis PDFs estão na release `aulas-v1` do mesmo GitHub.
- Sintaxe JavaScript e consistência do diff das alterações.

## Disponibilidade pública e limites

O atlas principal é uma aplicação estática distribuída pelo GitHub Pages. Bibliotecas JavaScript e modelos acompanham o repositório; aulas e PDFs usam o GitHub Releases. Nenhum arquivo da máquina do autor é necessário para usar o site público.

Peças humanas incorporadas e cortes institucionais são referências externas explicitamente indicadas. Sua disponibilidade depende dos respectivos serviços. O atlas mantém acesso à fonte oficial.

Esta revisão verifica funcionamento, navegação e consistência dos dados. Não representa uma validação científica integral da anatomia ou das transcrições automáticas. Os vídeos foram verificados quanto ao acesso e controles, sem análise de conteúdo.
