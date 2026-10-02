# Atlas 3D com nomes, fotografias e tutor

Atualização de 01–02/10/2026 conforme o pedido de Victor. `site/specimens.html` reúne identificação anatômica, reconstruções de exames e fotografias por sistema. A navegação tem cinco entradas; catálogo e orientações extensas ficam em blocos recolhíveis.

## Identificar estruturas em 3D

Os modelos com nomes são as referências iniciais de cada sistema:

- **Coração HRA / Visible Human Male:** nove peças selecionáveis — quatro câmaras, quatro conjuntos valvares e septo interventricular. Nomes seguem as malhas da fonte; cinco representações papilares em revisão ficam fora dessa seleção. Modelo de referência simplificado, sem textura fotográfica; licença CC BY 4.0.
- **Pulmões e árvore brônquica Z-Anatomy:** 34 peças — cinco lobos e 29 peças da árvore brônquica. Nomes seguem a fonte; licença CC BY-SA 4.0. Curvas e superfícies do autor preservadas, com cores ilustrativas.

Rótulos visíveis por padrão, linhas até a peça, seleção pelo nome, pela superfície ou pela lista, explicação com origem, contexto translúcido e isolamento com enquadramento da seleção. Rótulos de peças encobertas deixam de aparecer na visão geral; a lista revela estruturas internas. Girar e ampliar atualiza as posições dos nomes. A cena anterior também inicia com nomes e mostra o nome da peça selecionada.

## Reconstruções e peças digitalizadas

| Referência | Procedência e limites |
| --- | --- |
| Coração de CT | Matthew Bramlet, [NIH 3DPX-002636](https://3d.nih.gov/entries/3DPX-002636), versão 2; 630.640 triângulos. CC0/domínio público. GLB oficial preservado. Material fosco apenas para exibição, pois a fonte não inclui material. |
| Conjunto broncovascular de CT | [Meershoek et al. (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10403471/), suplemento científico; 312.856 triângulos preservados na conversão STL→GLB. Modelo CC BY-NC-SA 4.0, distinto da licença do artigo. Artefatos de impressão e suavização da fonte permanecem. |

As duas reconstruções não possuem segmentações individuais verificadas; não recebem pontos anatômicos inferidos. O estudante pode selecionar os modelos **com nomes** no mesmo ambiente para estudar identificação. Dez referências UMN / UBC-HIVE continuam nos visualizadores oficiais, sem redistribuição de seus arquivos. São 14 opções ao todo, oito disponíveis no filtro de cada sistema.

## Fotografias públicas e instalação pessoal

O site público usa quatro imagens de peças humanas por Anatomist90 / Wikimedia Commons, CC BY-SA 3.0: coronárias, valva aórtica, pulmão esquerdo e pulmão direito. Os JPEGs originais foram preservados, com créditos, fonte e licença na ampliação e em [atribuição](../../../site/assets/public-specimens/ATTRIBUTION.md).

A instalação pessoal preserva **213 entradas**, divididas em circulatório (110) e respiratório (103): 60 imagens-base dos Ankis, 152 recortes e o esquema de coronárias de Victor. Há 164 fotos individuais, 48 pranchas e um esquema. Essas imagens, manifesto, registros de extração e capturas que os expõem estão ignorados pelo Git e não fazem parte da atualização pública. A autorização de redistribuição das fotos pessoais não foi documentada. Os registros da extração ficam localmente em `refinamento/qualidade/pecas_apkg/`.

Cada seção tem expansão própria, busca, filtros, ampliação em resolução original e acesso às pranchas. No servidor local é possível alternar os dois acervos; no site público o acervo pessoal fica indisponível e seus arquivos não são requisitados.

## Tutor gratuito

**Dúvidas?** abre o tutor no canto inferior. **Biblioteca do atlas**, modo inicial, recupera trechos de 109 seções e oferece links às unidades, sem geração nem envio a provedor.

**IA gratuita · experimental** usa, por escolha explícita, a rota `default` de `https://api.llm7.io/v1/chat/completions`. A pergunta, até seis mensagens anteriores de IA e até três trechos de teoria já públicos são enviados à LLM7 e aos provedores roteados por ela. Nenhuma foto, Anki ou arquivo pessoal é anexado. O índice é gerado a partir de dois JSONs públicos com hashes conferidos: [evidência de publicação](fontes-publicas-chat.json). Fontes alteradas exigem nova conferência; contexto sem indicação de publicação é recusado antes de envio.

A rota respondeu sem conta ou chave em teste direto e no navegador simulando hospedagem estática. O modelo efetivo pode mudar e aparece na resposta. Pergunta verificada: quais câmaras a valva mitral separa — resposta identificou átrio esquerdo e ventrículo esquerdo e apontou unidades da teoria. Isso comprova a integração, **não validação médica**. Uma pergunta exploratória sobre fase cardíaca com contexto curto recebeu uma relação de fluxo incorreta; as respostas precisam de conferência nas fontes. O tutor limita a evidência ao material recuperado e mantém a biblioteca como alternativa quando há falha, quota ou timeout. A conversa fica na memória da página.

Pesquisa de alternativas: Pollinations respondeu 500/ENOSPC em dois ensaios; OVH respondeu 429 em ensaios anônimos. Modelos específicos da LLM7 pediram chave; apenas a rota anônima `default` usada aqui foi confirmada. Não foi criada conta nem usado plano pago. Groq permanece opcional com chave própria no servidor local, fora de `site/` e do Git; não foi executada geração real pela Groq.

## Evidências

- [Nomes 3D: 14 verificações](verificacao-nomes.json): nomes por padrão, seleção, valva interna, isolamento, restauração, filtro respiratório, brônquio, celular, ausência de rótulos inferidos nas CT e cena anterior. Sem erros JavaScript.
- [Fluxo integrado: 36 verificações](verificacao-navegador.json): modelos de CT, galerias pessoais, filtros, pranchas, chat, falhas e texto seguro, largura móvel, início e navegação. Contratos de resposta/falha da IA neste roteiro usam respostas simuladas.
- [Hospedagem pública: 11 verificações](verificacao-publicacao.json): quatro fotos licenciadas, ausência de requisições pessoais, créditos, celular, API estática, **geração real** e alternância local de acervos.
- [Teste real direto LLM7](verificacao-llm7-real.json), [servidor HTTP](verificacao-servidor.json), [estrutura dos GLB](verificacao-modelos.json) e [hashes dos arquivos](verificacao-hashes.json).
- [Cancelamento e timeout: quatro verificações](verificacao-cancelamento.json), com índice retido e callbacks controlados; cancelamento não interfere na próxima pergunta.
- Testes unitários do proxy, verificações sintáticas de JavaScript, compilação Python, Ruff e `git diff --check`. Resultado final da revisão independente e testes do chat em `verificacao-revisao.json`.

A incorporação institucional foi conferida, mas todos os dez modelos externos não tiveram seu carregamento completo revalidado. A integração de nomenclatura não amplia a cobertura anatômica certificada do roteiro.

Abra localmente com `./Abrir_Pecas_Reais.sh`. Atualização preparada para o [PR de rascunho #6](https://github.com/ra149021/coracao-3d-estudos/pull/6), baseado no PR #5. O envio ao ramo de trabalho não publica `main` nem altera o site principal.
