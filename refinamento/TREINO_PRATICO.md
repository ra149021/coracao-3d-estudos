# Módulo de treino prático

O módulo está em `site/study.js` e `site/study.css`. Não contém o curso teórico. Os textos de apoio provêm das notas das peças no catálogo atual.

## Integração

Depois que a cena tiver carregado, importar e chamar:

```js
import { initStudy } from './study.js';
initStudy({ parts: catalog.parts, requirements: matriz.alvos, viewer });
```

O módulo carrega sua própria folha de estilo local, insere os botões **Prática** e **Roteiro** no cabeçalho e insere um cartão de questão antes do canvas. Não faz requisições externas.

### Contrato do visualizador

- `select(id)`, `clear()`, `isolate(id)`, `focus(id)`.
- `show(ids)` mostra exatamente os IDs fornecidos; `showAll()` restaura todas as peças.
- `view(direction)` aceita `anterior`, `posterior`, `superior`.
- `labels(boolean)` liga/desliga nomes nas peças.
- `setExamMode(boolean)` oculta nomes, hover, lista e painel de seleção, inclusive conteúdo acessível que revele respostas. Também deve impedir reativar nomes pelos controles durante a pergunta. Não deve eliminar interações de câmera e seleção necessárias ao treino.
- `onPick(callback)` notifica **somente** clique do usuário em uma peça; retorna função para retirar o listener. Callback recebe ID ou `{id}`. Seleção feita pelo próprio módulo não deve simular resposta do usuário.
- `snapshot()` e `restore(snapshot)` preservam a exploração ao pausar/sair. Sem `restore`, há fallback para visibilidade, seleção e nomes; câmera e outros controles dependem de `restore`.
- Ao iniciar o modo de prova, desativar corte que possa excluir o alvo; ao restaurar, recuperar corte e transparência originais. As peças indicadas pelo quiz precisam continuar selecionáveis.

## Regra de cobertura

O roteiro contém 178 alvos. O módulo diferencia:

1. **Peça associada**: ID de `part.requirement.id` igual ao ID do alvo e pelo menos uma associação sem `correspondence: 'partial'`. Isso não confirma sua anatomia.
2. **Contexto parcial**: associação marcada `correspondence: 'partial'`, ou nome original da peça encontrado nas evidências Z-Anatomy do alvo sem associação direta. A peça relacionada não substitui o detalhe.
3. **Pendente**: sem peça associada/contexto carregado nesta cena. A auditoria pode localizar uma geometria em um acervo que ainda não foi integrada; os dois estados permanecem distintos.

No catálogo inicial de 39 peças: 38 alvos têm peça associada, 52 têm contexto parcial, 88 estão pendentes na cena. Os números são calculados novamente a cada carregamento, sem porcentagem de fidelidade ou aprovação. São separados de desempenho pessoal no treino.

## Rodadas

- **Identificar a peça destacada**: destaca um objeto real, esconde nomes, permite isolar e revelar. O aluno registra se identificou com segurança ou precisa revisar.
- **Encontrar no 3D**: pergunta pelo nome da peça existente e recebe o clique no modelo. Uma tentativa incorreta mantém a questão; revelar não dá crédito automaticamente.
- Somente peças com ID, nome e triângulos no catálogo, e sem `quizEligible: false`, entram nas questões. A nomenclatura e as notas da própria fonte ficam visíveis na resposta. Peças não elegíveis continuam disponíveis como contexto e no roteiro.
- Alvos pendentes não geram questões artificiais. Um músculo, folha ou ramo incorporado à malha maior não vira pergunta independente sem ter sido integrado ao catálogo.
- Partes são exibidas em grupos para permitir inspeção; folhetos e papilares são exibidos juntos. Isso é informado no cartão. A geometria e a posição não são inventadas pelo treino.
- **Deixar para depois** transfere a peça para o fim da fila, sem considerá-la concluída. Não perde itens restantes.
- **Pausar e explorar**, **Escape**, abrir a prática novamente ou abrir o roteiro salvam a fila e restauram a exploração anterior. Retomar reinicia a pergunta ainda não avaliada.
- Após a rodada, é possível repetir apenas as peças marcadas para revisão. Não há inferência de domínio de estruturas ausentes.

## Persistência e privacidade

`localStorage` usa a chave `heart-atlas:practice:v2:${location.pathname}`. Contém fila, peças revistas e autoavaliações. É local à origem/endereço e não é enviado a um servidor. Falha de armazenamento não impede o treino; aparece aviso no dialog. Uma atualização de catálogo elimina IDs que deixaram de existir ou de ser elegíveis da rodada recuperada e recalcula o total.

## Verificação

Concluído: `node --check site/study.js` sem erro. Verificação de dados com o catálogo inicial confirmou 39 peças e a partição 38 + 52 + 88 = 178.

Verificar com o visualizador integrado:

1. Abrir **Prática**, iniciar identificação e confirmar que nenhum nome da resposta aparece em lista, inspector, hover, label ou título da seleção.
2. Girar/aproximar, revelar, avaliar e confirmar avanço de 0 para 1 revisada; todos os IDs restantes devem permanecer na fila.
3. Usar **Deixar para depois**; o total revisado permanece igual. A peça retorna no fim da fila.
4. Pausar e confirmar recuperação de visibilidade, câmera, seleção, corte, transparência e nomes anteriores. Retomar e recarregar a página: a fila permanece.
5. Abrir modo de encontrar e clicar em peça errada/correta; acerto revela a fonte, não encerra silenciosamente a rodada. Escolher autoavaliação avança uma vez.
6. Concluir uma rodada curta de câmaras, repetir somente as marcadas para revisão, abrir nova rodada.
7. No roteiro, filtrar por pendente e buscar `pericardio`; nenhuma peça relacionada deve ser apresentada como o pericárdio fibroso confirmado. Filtros de roteiro e complemento devem produzir 156 e 22 alvos.
8. Em viewport de 390 px, cabeçalho, dialogs e ações devem caber sem rolagem horizontal. Conferir Escape, Tab, Enter e nomes acessíveis.

Diagnóstico de leitura disponível em `window.heartStudy.snapshot()`. Ele não inclui o ID da resposta atual. Os métodos `openPractice()` e `openRoute()` permitem abrir interfaces para inspeção. Os testes do ciclo 3D dependem da implementação do contrato acima.
