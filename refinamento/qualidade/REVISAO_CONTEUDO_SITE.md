# Melhorias do atlas fundamentadas no conteúdo

A revisão encontrou oportunidades principalmente na integração entre figuras, teoria, roteiro e reconhecimento visual. O conteúdo já oferece **26 unidades, 94 perguntas originais, sete videoaulas, seis documentos e 354 páginas**. Há busca, progresso local, referências por página/horário, prática em 3D, peças humanas UMN e vistas regionais. As propostas abaixo acrescentam usos específicos desses recursos.

Escopo: anatomia circulatória e respiratória, orientada pelos materiais de Carmem. O roteiro cardíaco é docente; os 222 IDs respiratórios são um índice editorial derivado dos slides. Não se estimou incidência na prova. Transcrições são índices de localização; esta revisão não conferiu integralmente o áudio.

## O que foi entregue nesta etapa

[Ampliação mediastinal](mediastino/README.md): 15 superfícies originais acrescentadas, quatro vistas, cinco associações nominais que faltavam da cena e links teóricos atualizados. A preservação geométrica e os testes estão documentados. Pericárdio, detalhes internos, folhetos pleurais, volumes segmentares e microestruturas continuam com seus limites explícitos.

## Continuação de 30/09/2026

As prioridades 1–5 abaixo foram implementadas na etapa [Teoria, figuras e prática](teoria_visual/README.md): 108 seções com figuras escolhidas, dez tarefas visuais separadas das 94 perguntas textuais, alvos e evidências do roteiro na teoria, links para vistas/brônquios e quatro cartões de peças humanas. O relatório registra os testes e os limites. As prioridades 6–10 e o próximo ciclo geométrico continuam como propostas.

## Oportunidades prioritárias

Esforço baixo/médio/alto é uma estimativa de implementação e curadoria, não um cronograma. A ordem considera ganho de estudo e aproveitamento do material existente.

| Ordem | Adição e comportamento concreto | Evidência no conteúdo e na implementação atual | Esforço estimado |
| --- | --- | --- | --- |
| 1 | **Figuras escolhidas por seção.** Mostrar o slide pertinente junto do trecho, com comparação entre duas páginas quando necessário e acesso ao original. | `site/theory.js`, `selectChapter()`, escolhe apenas a primeira referência do capítulo. Pericárdio abre Coração p.51, enquanto a seção dos seios cita pp.57–58. Pleura precisa pp.110,112,118. A unidade alveolar precisa Respiratório pp.131–132, mas sua primeira referência visual é p.125. Os demais slides hoje ficam disponíveis por links. | Baixo a médio |
| 2 | **Questões com imagem e resposta revelável.** Pedir localização ou distinção na figura, depois conferir a referência docente. Começar por laringe e detalhes cardíacos ausentes do modelo. | `renderQuestion()` em `site/theory.js` só usa texto/rascunho. Respiratório pp.72–73: pregas, rima, ventrículo e orientação laríngea, R098–R103. Coração p.31: fossa oval, limbo, crista e óstios; p.37: corda, papilar e trabécula. Os critérios já constam nos arquivos `practice-evidence.json`; falta recuperação diante da figura. | Médio |
| 3 | **Alvos do roteiro dentro da unidade teórica.** Listar nome, referência e situação na cena; abrir o item com seu critério e evidências. | `chapter.requirementIds` já mapeia o conteúdo às matrizes; os 178 alvos cardíacos aparecem nesse campo. `site/theory.js` apresenta `partIds`, mas não renderiza os requisitos. Por exemplo, a unidade de átrios pode ligar diretamente fossa oval e suas pendências ao roteiro. O módulo prático já calcula peça associada/contexto/pendente. | Médio |
| 4 | **Abrir as vistas existentes a partir da teoria.** Oferecer a região/contexto junto dos links individuais; nas tabelas B/S, abrir o brônquio dentro da vista do lobo correspondente. | `site/theory.js` cria links com `part=` e células de tabela em texto. Respiratório pp.92–93 e unidade 8 já têm convenção docente e cinco vistas por lobo. Exemplo: B4 → `preset=arvore_medio_direito&part=resp_lateral_segmental_bronchus_of_right_lung_biv`. As novas vistas também podem ligar a unidade 11 a nervos/linfonodos. O ramo B não demonstra o volume S em 3D. | Baixo a médio |
| 5 | **Comparação com peça humana a partir da seção certa.** Abrir UMN188 em ventrículos/aparelho subvalvar e UMN064 em valvas, com uma tarefa curta de observação. | As peças e tarefas já existem em `site/assets/specimens.json`; `site/specimens.js` aceita `?model=`. A teoria não apresenta esses vínculos diretos. Usar Coração p.37 e figuras valvares como referência comparativa. Preservar os limites de preparação, cortes e fixação de cada peça. | Baixo |
| 6 | **Sequência visual de pleura e recessos.** Comparar superfície pulmonar, fissuras, reflexão junto da raiz e parede, chegando aos recessos. | Respiratório pp.110,112,113–118; R161–R172. A vista `pleura_inspecao` já existe, e o catálogo registra a superfície agregada fora do quiz. A unidade 10 tem `partIds:[]`; cabe um link à vista como contexto e uma sequência das figuras. Isso não individualiza folhetos ou recessos nas oito componentes geométricas da fonte. | Baixo a médio |
| 7 | **Percursos com checkpoints.** Reconstruir o caminho do ar e o circuito sanguíneo por etapas, pedindo a próxima comunicação antes de revelar e oferecendo a peça/figura correspondente. | O percurso do ar é uma lista na unidade respiratória 1, com pp.6–8,42,72,88. O percurso do sangue já está na unidade `circ-circuitos`, com Coração pp.15,20,26,42,71. A home oferece uma sequência geral de uso; ainda não há atividade encadeada desses percursos. No caminho do ar, passar para a ilustração quando a escala deixar o modelo macroscópico. | Médio |
| 8 | **Mudança de escala até a barreira alveolocapilar.** Ordenar bronquíolo/ducto/saco/alvéolo, reconhecer componentes ilustrados e indicar o sentido da troca. | R192–R198; Respiratório pp.8,131–132 e unidade 12. O texto e perguntas sobre pneumócitos/surfactante existem; reconhecimento e ordenação visual ainda não. Essas páginas são ilustrações, não micrografias: chamar de microanatomia esquemática, sem anunciar treino histológico em lâmina. | Médio |
| 9 | **Drenagem nasal como exercício espacial.** Alternar estrutura óssea, espaço e função; depois seguir origem → destino da drenagem. | Respiratório pp.19,20,36; R019–R029/R034–R041/R221. Já há tabela e perguntas de drenagem. Falta relacionar o texto às três figuras. Mucosa e etmoide são agregados; os meatos e óstios não podem receber rótulos 3D específicos sem inspeção. Reutilizar `seios_referencia` como contexto. | Médio |
| 10 | **Topografia linfática torácica ligada aos dois sistemas.** Comparar traqueobronquiais inferiores/superiores, paratraqueais e hilares; diferenciar rede linfática e conjunto nodal. | Linfático pp.46–47, Vasos p.42, Respiratório p.129. A unidade circulatória linfática tem seis perguntas, mas nenhuma pede essa distinção espacial. As quatro novas peças oferecem contexto para alguns conjuntos; hilares, redes e troncos continuam ausentes. Não mapear estações oncológicas às malhas a partir dos nomes. | Baixo a médio |

## Implementação comum sugerida

O primeiro ciclo pode resolver as prioridades 1–5 com um componente de figuras por seção, metadados de tarefas visuais e links que reutilizem vistas/peças oficiais. Depois, o mesmo mecanismo atende pleura, microanatomia e drenagem nasal. Evitar outra busca, outra biblioteca de slides ou outro acervo de peças que duplique o que já funciona.

Reutilizar o mecanismo de progresso, com IDs estáveis e identificação do tipo de atividade. Diferenciar leitura, pergunta textual, reconhecimento em figura e identificação no modelo. Uma contagem única não deve sugerir que esses desempenhos medem a mesma habilidade ou aprovam a cobertura anatômica.

Para uma questão visual, usar primeiro páginas comparativas e instruções abertas, sem apagar legendas originais ou inventar coordenadas de estruturas. Um hotspot ou uma imagem derivada exige conferência da posição, resposta e referência. Nos seis quadros endoscópicos da p.73, não atribuir automaticamente uma fase de respiração/fonação só pelo número do quadro.

Os links da teoria podem abrir uma vista e selecionar uma peça. Nesta entrega, o link combinado de uma vista com `focusPartIds` mantém o enquadramento regional; links somente com `part=` continuam permitindo inspecionar a peça inteira.

## Próximo ciclo geométrico

1. **Aparelho atrioventricular:** conferir inserções e possibilidade de delimitar folheto/corda/papilar nas superfícies reais; Coração pp.37,39,42–43. As cordas incorporadas aos folhetos não autorizam separação automática por componentes. O papilar anterolateral parcial permanece parcial.
2. **Regiões de superfície:** orientação externa cardíaca, faces/fissuras e relações pulmonares. Conferir em duas vistas contra Coração pp.12–22 e Respiratório pp.103–109. Vasos vizinhos ajudam a orientar; não provam um sulco modelado.
3. **Pleura/pericárdio:** continuar inspeção e aquisição de geometria de tecido/reflexões com origem e licença adequadas. Respiratório p.118 e Coração pp.51–59 governam as relações exigidas. Uma casca genérica ou componentes arbitrários não completa os folhetos, espaços ou seios.

Não foi localizada nesta etapa uma nova malha licenciada que resolvesse todas essas lacunas. A nova montagem mediastinal ajuda a estudar relações; seu relatório mantém a validação individual pendente.

## Rastreabilidade da revisão

- Teoria: [circulatória](../../site/assets/circulatory-theory.json), [respiratória](../../site/assets/respiratory/theory.json), [renderização e revisão](../../site/theory.js).
- Escopo e evidências: [matriz cardíaca](../../site/auditoria/matriz_coracao.json), [índice respiratório](../../site/assets/respiratory/requirements.json), [evidências cardíacas](../../site/assets/practice-evidence.json), [respiratórias](../../site/assets/respiratory/practice-evidence.json).
- Recursos existentes: [vistas](../../site/assets/study-views.json), [peças humanas](../../site/assets/specimens.json), [sala de aulas](../../site/classroom.js), [home](../../site/home.js), [prática/roteiro](../../site/study.js).
- Geometria e limites: [inspeção anterior](inspecao_roteiros/README.md), [prioridades anatômicas](PRIORIDADES_ROTEIRO.md), [nova ampliação mediastinal](mediastino/README.md).

As propostas de interface derivam dos dados e do código atuais. As referências exatas dos slides acompanham cada proposta. Para relações dos grupos linfáticos e nervos, também foram consultadas [UAMS — linfáticos do tórax](https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/lymphatic-tables/lymphatics-of-the-thorax/) e [UAMS — nervos do tórax](https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/nerve-tables/nerves-of-the-thorax/). Essas fontes apoiam a conferência regional; não certificam a montagem digital.
