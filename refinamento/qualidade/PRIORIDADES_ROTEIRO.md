# Prioridades de qualidade anatômica pelo roteiro

## Decisão proposta

Priorizar identificação por limites, continuidade e relações. A maior parte do ganho imediato está em **regiões bem delimitadas e vistas adequadas das malhas existentes**. As lacunas de mucosa, pericárdio e relevo intracardíaco exigem aquisição ou reconstrução anatômica específica; aumentar polígonos ou adicionar um marcador não resolve essas lacunas.

Esta auditoria propõe **15 melhorias**. Na primeira entrega houve apenas leitura. Depois, por autorização específica, foi corrigida a associação nominal R010, documentada abaixo; UI, malhas e estado de validação visual não foram alterados. A ordem considera utilidade para a prática e viabilidade com o acervo atual; não estima probabilidade de cobrança na prova.

### Base observada

- Coração: 178 alvos no roteiro/matriz, 72 peças no catálogo atual.
- Respiratório: 222 alvos editoriais derivados dos slides, 167 peças Z-Anatomy; detalhe laríngeo independente com 40 peças BodyParts3D.
- Coração possui roteiro docente. O respiratório continua identificado como **roteiro de estudo derivado dos slides**, sem roteiro oficial de Carmem confirmado. Contagem de peças não equivale a alvos atendidos.
- Conferidos catálogos, critérios e notas em `practice-evidence.json`, requisitos, capítulos de teoria, relatórios geométricos e quatro pranchas de inspeção existentes. Também foram vistos os slides cardíacos 27, 31, 34, 37, 45 e 57 e respiratórios 36, 64, 72, 85, 105 e 118 nesta rodada.
- As pranchas mostram montagens e relações gerais. Não foi feita nesta auditoria uma inspeção interativa de todas as superfícies internas; hipóteses geométricas permanecem condicionais.

### Classes e confiança

**Região**: candidato a seleção de faces/âncora na malha; **visualização**: estrutura presente, mas difícil de reconhecer; **simplificação**: forma insuficiente ou agregada; **ausência**: não há representação específica confirmada. Mais de uma classe pode ocorrer no mesmo item.

**Confiança curricular** indica sustentação no roteiro/slides. **Confiança de execução** indica evidência de que a ação possa funcionar no acervo atual, sem certificar a anatomia final. Alta não significa “validado”.

## Quinze melhorias prioritárias

### 1. Separar o reconhecimento de folheto, corda e músculo papilar

- **Alvos:** 46a–c, 47–49, 51, 58a–b, 59–61. **Evidência:** roteiro pp.2–3; Coração pp.37, 39, 42–43. A fotografia da p.37 permite comparar corda, papilar e trabécula.
- **Classe:** visualização + região; simplificação parcial do papilar anterior esquerdo.
- **Cena atual:** `heart_26`, `heart_27`, `heart_28`, `bp_FJ2421`, `bp_FJ2420` incorporam cordas aos folhetos. `heart_35`–`heart_38` representam papilares; `bp_FJ2418` é somente uma porção de cabeça anterolateral, como a própria fonte declara. A prancha `registro_inspecao.png` confirma que os componentes existem, mas também mostra superfícies idealizadas e não certifica cada inserção.
- **Ação concreta:** preparar vistas ventricular e atrial do aparelho AV preservando posição; criar máscaras de faces para **regiões de cordas já existentes**, sem fabricar novos cordões. Selecionar folheto, cordas e papilar separadamente para estudo. Manter “porção” em 59 até obter/conferir o conjunto completo.
- **Validação necessária:** seguir cada corda selecionada até folheto e papilar; conferir ausência de terminações flutuantes e atravessamentos grosseiros; distinguir inserção aparente por proximidade de continuidade real. Uma vista explodida pode explicar o conjunto, mas a vista de referência deve conservar as conexões.
- **Aceitação:** o aluno distingue os três tecidos sem depender da cor e retorna à montagem original. Não liberar coaptação ou movimento valvar como fenômeno validado.
- **Confiança:** curricular alta; execução alta para seleção/vistas, média para inserções, baixa para completar 59 sem nova fonte.

### 2. Identificar faces, margens, ápice, base e sulcos cardíacos na superfície real

- **Alvos:** 7–15, 17, 19, 25–29. **Evidência:** roteiro p.1; Coração pp.12, 14, 16, 18–19, 21–22.
- **Classe:** região + visualização.
- **Cena atual:** quatro paredes `heart_00`–`heart_03` e rede coronária já permitem investigar orientação e limites. Aurículas estão incorporadas às paredes atriais. Não há prova de que todos os sulcos tenham relevo suficiente.
- **Ação concreta:** elaborar vistas anterior, posterior, inferior e laterais com regiões de superfície delimitadas; começar por ápice/base, faces e aurículas. Depois conferir sulcos e crux com a rede vascular visível e oculta. Usar máscaras de faces ou contornos sobre a superfície para áreas extensas, em vez de um ponto que parece identificar uma peça independente.
- **Validação necessária:** base posterior e ápice ventricular devem ser reconhecidos pelas câmaras/vasos vizinhos. Nos sulcos, demonstrar relevo ou limite entre regiões; se só a topografia estiver identificada, nomear “trajeto topográfico” e não “sulco modelado”.
- **Aceitação:** mesma região reconhecível em duas orientações; âncora acompanha sua malha ao movimentar a peça; sulco não muda de identidade quando o vaso é ocultado.
- **Confiança:** curricular alta; execução alta para regiões amplas, média para sulcos e crux.

### 3. Usar o contexto torácico já existente para sintopia cardíaca

- **Alvos:** 1–2; apoio a 7–10 e 14–15. **Evidência:** roteiro p.1; Coração pp.12, 14, 16–18.
- **Classe:** visualização + associação entre cenas, com contexto ainda incompleto.
- **Cena atual:** o respiratório já contém as quatro câmaras, esterno/costelas, pulmões e diafragma no registro Z original e um preset `torax`. O coração principal usa outra centralização. A limitação “modelo isolado” do catálogo cardíaco não significa ausência de todo contexto local.
- **Ação concreta:** oferecer esse conjunto existente como vista de sintopia vinculada aos dois alvos; conservar o transform original comum. Acrescentar esôfago/aorta apenas após recuperar suas transformações exatas e conferir relações. Se houver integração ao atlas cardíaco, aplicar uma única transformação documentada ao conjunto de contexto.
- **Validação necessária:** comparar posição do coração em relação a esterno, diafragma e pulmões nas vistas frontal/lateral; verificar unidades e eixos das duas cenas. Não alinhar cada órgão manualmente para fazê-lo caber.
- **Aceitação:** orientação corporal coerente, contexto ativável e registro auditável. Ausência de pericárdio continua explícita; não declarar toda a sintopia completa.
- **Confiança:** curricular alta; execução alta para a vista torácica existente, média para integração entre cenas.

### 4. Delimitar acidentes das cartilagens laríngeas

- **Alvos:** R062–R068, R073–R076, R080, R086–R087. **Evidência:** Respiratório pp.56–58, 61, 64; figura64 distingue processos vocal e muscular.
- **Classe:** região + visualização.
- **Cena atual:** tireóidea, cricóidea e aritenóideas existem nos dois acervos; `resp_arytenoid_cartilage_l/r` têm 3.780 triângulos cada. O detalhe BP preserva componentes vocais que ajudam a conferir relações; não deve ser fundido ao Z por causa do registro rejeitado.
- **Ação concreta:** no próprio acervo, marcar arco/lâmina da cricóidea, cornos/incisuras/linha oblíqua da tireóidea e processos aritenóideos por seleção de faces. Priorizar aritenóideas em vista superior/posterior e cricóidea em vista anterior/posterior.
- **Validação necessária:** demonstrar onde o ligamento vocal se dirige e onde os músculos se relacionam com a aritenóidea; conferir a base junto à cricóidea. A articulação exige duas superfícies compatíveis; um ponto entre duas caixas envolventes não basta.
- **Aceitação:** cada região tem pelo menos dois marcos vizinhos verificáveis e uma vista sem rótulo. Não criar uma peça nova para cada acidente ósseo/cartilaginoso.
- **Confiança:** curricular alta; execução alta para acidentes amplos, média para processos pequenos e superfícies articulares.

### 5. Tornar os segmentos brônquicos reconhecíveis sem multiplicar falsas peças

- **Alvos:** R111–R137. **Evidência:** Respiratório pp.89–95; R3 04:11–05:14 reforça o estudo prático. Figuras92/93 são o gabarito visual do agrupamento usado na aula.
- **Classe:** visualização; ausência de volumes segmentares independentes.
- **Cena atual:** principais, lobares e 19 grupos segmentares da convenção docente têm peças nomeadas. Cada grupo segmentar inclui ramificações distais; o preset de árvore já existe. Há uma alternativa anteromedial esquerda oculta e fora do quiz.
- **Ação concreta:** criar vistas sucessivas por lobo, mantendo principal → lobar → segmentar e o lobo translúcido ao redor; reduzir sobreposição de ramos que atrapalha a seleção. Realçar o **ramo de entrada** do território, preservando as ramificações da mesma peça.
- **Validação necessária:** seguir a continuidade do ramo até seu lobar, conferir lado e orientação anterior/posterior contra figuras92/93. Manter apicoposterior esquerdo unido e basais medial/anterior separados conforme a aula; a alternativa anteromedial deve permanecer explicitamente variante.
- **Aceitação:** identificação sem cor e sem contagem universal imposta. Não pintar uma região inteira do pulmão como “segmento validado” apenas pela proximidade ao brônquio: limites volumétricos não foram segmentados.
- **Confiança:** curricular e execução altas para trajetos; baixa para volumes segmentares sem fonte própria.

### 6. Recuperar conchas, meatos e drenagem nasal com corte e relações

- **Alvos:** R010, R014, R016–R029, R034–R041, R221. **Evidência:** Respiratório pp.10, 17–20, 34–36; a figura36 mostra destinos de drenagem.
- **Classe:** região + simplificação agregada + possível desencontro de associação nominal.
- **Cena atual:** `resp_mucosa_of_nasal_cavity`, `resp_ethmoid_bone`, vômer, conchas inferiores e volumes sinusais. Meatos e recesso são candidatos em uma mucosa agregada; não há prova de todos os óstios. **Achado direto:** R010 procura `Greater alar cartilage` e está “não localizado”, enquanto o catálogo tem `resp_major_alar_cartilage_l/r` (`Major alar cartilage.l/r`, 344 triângulos cada), sem requisito associado.
- **Ação concreta:** primeiro conferir o candidato R010 em forma/posição e corrigir a associação quando confirmado. Depois preparar uma parede lateral nasal em vista medial, retirando o septo pela visualização, e uma vista coronal dos níveis das conchas. Delimitar meatos somente após reconhecer conchas correspondentes.
- **Validação necessária:** para R041, demonstrar posição distinta do meato superior; para R040/R221, reconhecer bolha/hiato na região do meato médio; para seios, mostrar um óstio real e sua continuidade antes de traçar drenagem no 3D.
- **Aceitação:** concha é saliência, meato/recesso é espaço; nenhuma linha atravessa uma parede fechada para fingir um ducto. Se faltar o óstio, abrir figura36 e registrar que o volume sinusal não demonstra a abertura.
- **Confiança:** curricular alta; execução alta para conferência do alias R010, média para conchas/meatos, baixa para óstios não inspecionados.

### 7. Conferir óstios cardíacos como aberturas, não como pontos externos

- **Alvos:** 32–34, 45, 54a–d, 57. **Evidência:** roteiro pp.2–3; Coração pp.27–30, 38–39; Vasos p.31 para desembocadura do seio coronário.
- **Classe:** região/abertura + continuidade ainda não demonstrada.
- **Cena atual:** paredes atriais, cavas, quatro veias pulmonares, `bp_FMA4706` e aparelhos AV. Vaso e câmara presentes não provam que exista comunicação entre seus lúmens.
- **Ação concreta:** produzir vistas internas dos dois átrios; inspecionar contornos de borda das malhas e a junção vaso–câmara. Mapear apenas as aberturas efetivamente presentes; registrar uma máscara do contorno e a vista correspondente. Separar óstio AV, tecido valvar e anel fibroso ausente.
- **Validação necessária:** atravessar visualmente a abertura em dois sentidos sem parede obstrutiva; conferir conexão anatômica do vaso, e não uma aresta aberta produzida pelo corte de visualização. Localizar o seio coronário em relação a VCI e óstio AV direito.
- **Aceitação:** cada óstio possui evidência de continuidade. Parede fechada ou junção sobreposta gera tarefa de correção geométrica e permanece pendente.
- **Confiança:** curricular alta; execução média para inspeção, indefinida para reparo até conhecer a topologia.

### 8. Mostrar traqueia posterior e bifurcação interna

- **Alvos:** R104–R110; apoio a R111–R112. **Evidência:** Respiratório pp.84–86; R3 00:00–02:16. Figura85 distingue bifurcação externa, carina, anéis e parede posterior.
- **Classe:** região + simplificação potencial + visualização.
- **Cena atual:** `resp_trachea` com 4.756 triângulos e principais exportados como superfícies de curvas. O catálogo relaciona a traqueia à carina, mas isso não demonstra uma crista intraluminal. R108 continua sem músculo específico confirmado.
- **Ação concreta:** comparar a traqueia Z com `larynx_fma7394` em seus acervos separados; inspecionar parede posterior, intervalos dos anéis e extremidade inferior. Preparar vista posterior e vista superior para a luz, se ela existir.
- **Validação necessária:** a carina precisa ser um relevo interno entre as entradas brônquicas. A bifurcação externa não basta. Para o músculo traqueal, identificar tecido/relevo próprio; uma faixa posterior arbitrária não equivale à malha muscular.
- **Aceitação:** pelo menos anéis, parede posterior e bifurcação são distinguíveis. Falta de carina/lúmen é relatada como simplificação, sem inserir um pin no encontro externo dos tubos.
- **Confiança:** curricular alta; execução média para regiões externas, baixa para carina e músculo até inspeção interna.

### 9. Acrescentar representação coerente das pregas e cavidades laríngeas

- **Alvos:** R098–R103, R222; relações com R096, R085–R087. **Evidência:** Respiratório pp.64, 70, 72–73; teoria capítulo6.
- **Classe:** ausência/simplificação; componentes parciais já disponíveis.
- **Cena atual:** laringe BP possui ligamentos e músculos vocais, mas não mucosa das pregas vocais completas, pregas vestibulares e cavidades individualizadas. `larynx_fma55245/55246` não devem receber o nome “prega vocal” como equivalência plena.
- **Ação concreta:** buscar/acrescentar uma laringe com revestimento interno coerente ou reconstruí-lo como conjunto a partir de referência anatômica, mantendo vestíbulo, ventrículo, pregas e região infraglótica relacionados. No acervo atual, usar os componentes para explicar a prega e a figura72 para a cavidade, sem inventar superfície.
- **Validação necessária:** conferir duas vistas em corte e uma superior/endoscópica: prega vestibular superior, vocal inferior, ventrículo entre ambas. Glote inclui pregas vocais e rima; rima é a abertura. Esse ponto foi corroborado pela fonte institucional.[1]
- **Aceitação:** a abertura é delimitada por tecidos reais da montagem; marcador espacial só descreve espaço quando seus limites estão presentes. Não fundir tecidos BP e Z com ajustes locais para compensar o registro rejeitado.
- **Confiança:** curricular e diagnóstico altas; execução baixa para completar mucosa com os dados atuais, alta para apresentação honesta dos componentes existentes.

### 10. Recuperar o conjunto de marcos internos do átrio direito

- **Alvos:** 22, 35–42, 55–56. **Evidência:** roteiro pp.1–2; Coração pp.27–31, 38.
- **Classe:** ausência/simplificação de relevos; candidatos de região ainda não confirmados.
- **Cena atual:** `heart_00` e `heart_02` fornecem paredes, mas não há peças específicas confirmadas para pectíneos, crista terminal, limbo ou pregas venosas. Fossa oval não está validada geometricamente.
- **Ação concreta:** inspecionar o lado septal e a aurícula em cortes sem transformar artefatos de corte em relevo. Procurar depressão/limbo, transição entre área lisa e pectíneos e pregas nas entradas. Caso o relevo não exista, priorizar um modelo atrial interno com topologia explícita ou reconstrução referenciada do conjunto.
- **Validação necessária:** fossa e limbo devem ser reconhecidos juntos; crista terminal deve separar territórios coerentes. Conferir uma segunda figura/atlas, porque a posição gráfica de uma seta sobreposta no slide isolado não define uma coordenada 3D. Não declarar uma parede lisa inteira como “parte posterior lisa”.
- **Aceitação:** estruturas distinguíveis em vista interna e correlacionadas às cavas, óstio AV e seio coronário. A área septal genérica pode receber uma nota contextual, mas não o nome “fossa oval validada”.
- **Confiança:** curricular alta; execução média para localizar a região septal, baixa para relevos ausentes na representação atual.

### 11. Reconstruir coerência entre parede ventricular, entrada e saída

- **Alvos:** 23–24, 43–44, 50, 52, 62, C41, C47. **Evidência:** roteiro pp.1–3; Coração pp.20, 34, 36–37, 39–43, 47–48.
- **Classe:** ausência/simplificação de relevo; vias de saída candidatas a região.
- **Cena atual:** `heart_01`/`heart_03`, valvas e papilares; trabéculas e banda moderadora não são peças prontas identificadas. Cortes de paredes independentes podem expor sobreposições, sem demonstrar um septo anatomicamente compartilhado.
- **Ação concreta:** começar pelas vias de saída: seguir do VD à pulmonar e do VE à aórtica; delimitar a região lisa apenas se presente. Auditar septo e espessura antes de investir em trabeculação. Para banda moderadora/crista/trabéculas, exigir fonte explícita e preservar inserções reais.
- **Validação necessária:** contrastar entrada trabeculada e saída lisa da figura34; banda moderadora tem continuidade própria no VD e não deve ser confundida com corda. Não introduzir textura ondulada para simular trabéculas volumétricas. Parte membranácea do septo precisa de relação com os elementos valvares/fibrosos, não apenas uma face lisa.
- **Aceitação:** uma rota ventricular contínua, paredes sem duplicação que falseie o corte e relevos sustentados por referência. Até lá, figuras36–37/41 complementam a prática.
- **Confiança:** curricular alta; execução média para vias de saída, baixa para relevo e septo membranáceo sem fonte adicional.

### 12. Refinar raízes semilunares, seios e origens coronárias

- **Alvos:** 53a–c, 63a–c, 77–80, 82, C45a–c. **Evidência:** roteiro pp.2–3; Coração p.45; Vasos pp.18, 20–21.
- **Classe:** simplificação provável + regiões/aberturas não conferidas.
- **Cena atual:** folhetos semilunares existem; `heart_04` tem 236 triângulos e `heart_06`, 93. Contagem baixa é alerta de detalhe limitado, não prova de que os seios estejam ausentes. Troncos coronários BP estão presentes.
- **Ação concreta:** inspecionar raízes por dentro e em corte longitudinal; comparar dilatação acima de cada folheto, comissuras e saída das coronárias. Se a raiz for apenas um tubo, obter uma raiz pronta detalhada ou reconstruir conjuntamente parede, seios, folhetos e óstios.
- **Validação necessária:** mostrar cada seio junto de sua válvula; os óstios coronários devem atravessar a parede dos seios correspondentes. Não criar os seios como três bolas ao redor do tubo nem desviar a coronária para uma posição escolhida visualmente.
- **Aceitação:** vista longitudinal e superior coerentes, com continuidade dos óstios. Refinamento de normais/subdivisão só pode melhorar a aparência da malha; não conta como nova anatomia.
- **Confiança:** curricular alta; execução média para auditar, baixa para concluir detalhe faltante sem referência própria.

### 13. Delimitar superfícies pulmonares e distinguir hilo de raiz

- **Alvos:** R143–R160, especialmente R148–R157; apoio a R173–R176. **Evidência:** Respiratório pp.101–109, 117.
- **Classe:** região + visualização; conjunto hilar incompleto.
- **Cena atual:** cinco lobos independentes já sustentam investigação de fissuras, faces, língula e incisura. Os requisitos de raiz estão associados sobretudo aos dois brônquios principais; isso não cobre automaticamente artérias, veias, vasos brônquicos, nervos e linfa.
- **Ação concreta:** criar vistas costal, diafragmática e mediastinal por lado. Segmentar regiões na superfície para ápice/base, faces, língula e incisura quando reconhecíveis; traçar fissuras como limites entre lobos, sem espessar uma linha em nova estrutura. Para hilo/raiz, incluir componentes reais do mesmo registro ou indicar precisamente os ausentes.
- **Validação necessária:** comparar fissuras nas figuras103/104 e passagens na105; avaliar impressões/sulcos com figuras108/109. Distinguir área de passagem (hilo) do conjunto que passa (raiz). Uma mancha medial colorida não prova a existência de cada abertura.
- **Aceitação:** reconhecimento do lado sem rótulo, distinção de incisura/ impressão cardíaca e possibilidade de seguir os componentes presentes. Sulcos lisos ou apagados permanecem topografia aproximada.
- **Confiança:** curricular alta; execução alta para faces/fissuras amplas, média para incisura/hilo, baixa para completar raiz sem novos componentes.

### 14. Individualizar partes pleurais e reconhecer recessos reais

- **Alvos:** R161–R166, R169–R172. **Evidência:** Respiratório pp.110–118; figura118 mostra relações dos recessos.
- **Classe:** simplificação agregada + regiões e espaços ainda não separados.
- **Cena atual:** `resp_pleura` tem 112.288 triângulos, mas uma peça única. A prancha mostra uma envoltória ao redor dos pulmões; isso não permite afirmar que haja duas superfícies com reflexões corretas.
- **Ação concreta:** decompor a malha apenas para análise topológica inicial: componentes, normais, limites e relação com lobos, mediastino e diafragma. Identificar quais folhetos estão realmente presentes. Separar regiões parietais comprovadas por máscaras; obter/reconstruir o folheto faltante caso a fonte forneça somente uma envoltória.
- **Validação necessária:** visceral acompanha pulmão/fissuras; parietal relaciona-se à parede e reflete-se nas transições. Recessos precisam de limites pleurais reais. O ligamento pulmonar é uma prega inferior à raiz; não substituí-lo por um cabo preso à base.[2]
- **Aceitação:** não promover a malha única a oito alvos completos. Mostrar espaço pleural/recessos com corte e limites; quando a geometria não sustentar isso, usar figura118 com o estado pendente.
- **Confiança:** curricular e diagnóstico altas; execução média para regiões externas, baixa para folhetos/reflexões sem inspeção topológica.

### 15. Construir um pericárdio com reflexões e seios, e não uma casca genérica

- **Alvos:** 3, 4a–b, 70–75; apoio ao endocárdio6 como distinção de revestimento. **Evidência:** roteiro pp.1, 3; Coração pp.51–59.
- **Classe:** ausência de geometria específica confirmada.
- **Cena atual:** catálogo declara pericárdio ausente. Superfície externa do coração pode indicar onde se encontra o epicárdio, sem representar uma lâmina independente; fáscia diafragmática não é pericárdio.
- **Ação concreta:** buscar conjunto pronto com reflexões arteriais/venosas e relação diafragmática, ou preparar reconstrução referenciada dessas relações como uma unidade. Priorizar saco fibroso, continuidade serosa e seios transverso/oblíquo antes de acrescentar ligações menores.
- **Validação necessária:** usar figura57 em vista posterior e demais figuras51–59 para conferir trajetos ao redor da aorta/tronco pulmonar e veias. Os seios são espaços delimitados por reflexões; não peças sólidas independentes. Duplicar e aumentar a escala da parede cardíaca não os cria.
- **Aceitação:** limites e continuidade demonstráveis em duas vistas, com coração e grandes vasos no mesmo registro. Fixações70–73 continuam pendentes se a nova fonte não as identificar; não inventar cordões pelo nome.
- **Confiança:** curricular e ausência declarada altas; execução baixa com o acervo atual, exigindo nova geometria ou reconstrução documentada.

## Protocolo mínimo antes de promover uma região para estudo validado

1. Registrar o alvo, tipo (superfície, relevo, abertura, espaço ou tecido), fonte exata e dois marcos vizinhos. Não iniciar a identificação pela posição de uma bolinha.
2. Inspecionar a malha real nas orientações relevantes e comparar com o material. Um `sourceName` sustenta a identidade da peça inteira, não necessariamente todos os acidentes nela.
3. Para superfície/relevo, guardar conjunto de faces e uma âncora em triângulo com coordenadas baricêntricas; para espaço, guardar os limites participantes. A posição da âncora deve ser derivada dessa inspeção, nunca da caixa envolvente isolada.
4. Para abertura, comprovar lúmen/continuidade. Bordas criadas pelo plano de corte não são óstios anatômicos.
5. Salvar vista com contexto e vista de treino sem nome, junto da captura comparativa da referência. Conferir se a identificação continua possível sem a paleta didática.
6. Revisar nomes e relações separadamente da qualidade gráfica. `quizEligible` e presença em catálogo não significam validação anatômica.
7. Se faltar relevo ou tecido, manter “parcial/pendente” e oferecer a figura de referência. A futura reconstrução deve ter fonte, transformação e modificações documentadas.

## Sequência de execução recomendada

**Primeiro ciclo:** 1–6 e partes reconhecíveis de13. São melhorias com acervo pronto, ganho de orientação e possibilidade de conferência concreta. O ajuste nominal candidato R010 pode ser resolvido no início.

**Segundo ciclo:** inspeções de7–8 e12, que decidem entre região existente e necessidade de reparo. Não avançar diretamente de uma associação nominal para identificação correta.

**Terceiro ciclo:** reconstruções de9–11 e14–15, conforme a inspeção confirme ausência. As lacunas permanecem estudáveis por figuras docentes enquanto a representação 3D é preparada.

### Pontos que ficam fora destas quinze prioridades

- Esqueleto fibroso64–69 e conduçãoC66a–f continuam lacunas importantes, mas demandam relações que dependem de septos, valvas e tecidos ainda incompletos. Uma rede tubular esquemática não deve ser anunciada como tecido anatômico realista.
- Circunflexa104 permanece um agregado: ramos104a–d não podem ser nomeados individualmente só pelo agregado. O vínculo de `bp_FMA3835` a102 ainda pede equivalência entre “ramos ventriculares posteriores direitos” e “póstero-lateral direito”. Manter notas existentes e conferir a origem/trajeto antes de ampliar identificação.
- Alvéolos/pneumócitosR192–R198 exigem outra escala; não acrescentar centenas de esferas a uma superfície pulmonar para aumentar cobertura.
- Textura, brilho, suavização e subdivisão podem facilitar leitura, mas nenhum desses recursos recupera anatomia ausente. A contagem de triângulos mede representação, não fidelidade.

## Rastreabilidade

Arquivos de referência locais: `site/auditoria/matriz_coracao.json`, `requisitos.json`, `site/assets/catalog.json`, `site/assets/practice-evidence.json`, `site/assets/circulatory-theory.json`; arquivos homólogos respiratórios; catálogo laríngeo; `refinamento/geometria/README.md`; `refinamento/respiratorio/geometria/README.md`. As páginas citadas são físicas, 1-based, nas fontes `roteiro`, `coracao`, `vasos`, `respiratorio`.

Pranchas conferidas: `refinamento/geometria/registro_inspecao.png`, `vascular_inspecao.png`; `refinamento/respiratorio/geometria/inspecao_geometrica.png`, `larynx_inspecao.png`. A redação das ações distingue observação dessas pranchas de hipóteses que ainda pedem inspeção.

Hashes dos catálogos observados (podem mudar durante a implementação):

| Catálogo | SHA-256 |
|---|---|
| Cardíaco | `2789d01489ac444755f75e8528a6eb7160004be7b373d833eefe887aef5a8fb7` |
| Respiratório | `229f490d7c40ec964bcbccc78ff1ee73f0f17d759223793712803b0b327828f7` |
| Laringe BP | `2db48316ca574452fc1c350946c9ccea805ac9189cdf9f68ca31e3758650c841` |

As fontes institucionais abaixo foram consultadas para as distinções pontuais de glote/rima, limites laríngeos e continuidade pleural. As tentativas de abrir duas páginas do atlas UMN nesta rodada retornaram timeout; não foram usadas como evidência. Não foi localizado Moore local nesta sessão.

## Complemento: investigação de marcos autorais

**Resultado: 27 registros de anotação recuperados, nenhum aprovado como âncora anatômica nesta rodada.** Os nomes do autor ajudam a procurar a região, mas as posições não são automaticamente pontos sobre a anatomia.

`MARCOS_AUTORAIS.json` conserva os dois vértices locais e transformados, a origem do objeto, IDs candidatos, transformações para cada cena, distâncias exploratórias e hashes das fontes. O `Startup.blend` foi lido por SDNA sem executar Blender ou scripts internos. Cada objeto `.j`/`.i` em questão tem dois vértices e zero polígonos: é uma anotação linear, não uma superfície anatômica. A extração usou a matriz mundial registrada, sem deslocar os pontos.

| Região candidata | Nomes autorais recuperados | IDs candidatos | Situação observada |
|---|---|---|---|
| Ápice e base cardíacos | `Apex of heart.j`; `Base of heart.j` | 15;14 | Extremidades têm distâncias mínimas exploratórias a vértices de 37,45mm e32,96mm, respectivamente. Pendente. |
| Faces cardíacas | `Anterior surface of heart.j`; `Inferior surface of heart.j`; `Right surface of heart.j`; `Left surface of heart.j` | 7;8;9;10 | Há afastamento relevante; os nomes direita/esquerda aproximam-se de câmaras opostas às esperadas para simples marcação de face. Não converter diretamente em pins. |
| Margens e sulcos | `Inferior border of heart.j`; `Right border of heart.j`; `Coronary sulcus.j`; `Anterior interventricular sulcus.j`; `Inferior interventricular sulcus.j` | 13;11;28;26;27 | A anotação inferior pode orientar busca, mas não demonstra limite. “Inferior”→“posterior” requer relação anatômica, não apenas troca de nome. |
| Ápice/base pulmonares | `Apex of lung.j`; `Base of lung.j` | R143;R144 | Nomes não especificam ambos os lados. O candidato de ápice aproxima-se de vértice do lobo superior direito a9,52mm. Não espelhar para completar o par. |
| Fissuras | `Horizontal fissure of right lung.j`; `Oblique fissure of right lung.j`; `Oblique fissure of left lung.j` | R148;R149;R150 | Menor distância exploratória entre extremidades e vértices dos lobos:31,32–37,04mm. Não oferecem âncoras diretas confiáveis. |
| Língula e incisura | `Lingula of left lung.j`; `Cardiac notch of left lung.j` | R153;R154 | O marcador de incisura fica mais próximo do **lobo médio direito** (2,13mm), incompatível com usar proximidade como prova. Pendente. |
| Faces e hilo pulmonares | `Costal surface of lung.j`; `Diaphragmatic surface of lung.j`; `Medial surface of lung.j`; `Mediastinal surface of lung.j`; `Hilum of lung.j`; `Interlobar surface of lung.j` | R145–R147;R151;relações R148–R150 | Alguns pontos ficam perto de superfícies, mas não delimitam regiões. Não equiparar “face interlobar” a três fissuras completas. |
| Processos aritenóideos | `Vocal process.j`; `Muscular process.j`; `Muscular process.i` | R086;R087 | Candidatos mais promissores: distância a vértice2,12mm (vocal) e3,24mm (musculares), mas posição ainda não confrontada com o acidente na superfície. Manter pendentes. |

As distâncias são **ponto a vértice**, na escala nominal do acervo, e não distâncias exatas à superfície ou medidas clínicas. Não estabelecem um limiar de validação. Valores pequenos não provam identidade, como mostra a incisura do lado errado; valores grandes impedem usar os pontos diretamente sem investigar a convenção das anotações e diferenças entre versões.

O arquivo `References100.fbx` foi convertido somente em `/tmp` para leitura: 57 nós/47 malhas, com direções corporais, movimentos, planos e linhas como esternal e medioclavicular. Não foram encontrados nele nós dos marcos cardíacos/pulmonares listados. Ele pode orientar referências corporais gerais, mas não preenche as anotações anatômicas específicas.

**Próximo passo seguro:** visualizar a linha autoral inteira junto à estrutura, descobrir sua convenção de extremidade por exemplos inequívocos do próprio acervo e confirmar forma/relações no slide. Só então considerar uma âncora em triângulo. Não fazer snap automático da anotação à malha mais próxima, não assumir o vértice0 como ponta e não inverter lateralidade para forçar correspondência.

## Alteração autorizada: R010

Após rever a figura respiratória10, foram confirmados os nomes exatos `Major alar cartilage.l/r` no inventário `Startup.blend` e no catálogo: cada peça tem174 vértices/344 triângulos. O requisito buscava o nome inexistente `Greater alar cartilage`.

- `requirements.json`: R010 passou de não localizado para disponibilidade nominal das duas malhas, mantendo `validacao_visual: pendente_individual` e uma nota explícita de limite.
- `catalog.json`: as duas peças receberam `requirementIds:[R010]`, fonte/página e `source_name_candidate` com `visualValidation: pending_individual`.
- `build_content.py`: nome de busca corrigido para `Major alar cartilage.*` para preservar o resultado em regeneração futura.
- `theory.json`: somente `partIds` do capítulo `resp_02` recebeu as duas peças existentes.
- `model.glb` e `practice-evidence.json` permaneceram byte a byte iguais, conferidos por SHA-256. Não houve alteração de forma, posição, avaliação de realismo ou validação anatômica integral.

O hash do catálogo respiratório logo após essa correção foi `9866a1d00c5d90f65fd29e601152077fa1a1cba55de1547cd7a2c376cb6d7634`. A integração posterior dos vasos pulmonares é trabalho do agente de geometria e pode mudar o hash/contagem. Este auditor não editou o catálogo durante essa regeneração.

## Sources

[1] https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/viscera-tables/visceral-structures-of-the-head-and-neck — UAMS — Visceral Structures of the Head and Neck
[2] https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/viscera-tables/visceral-structures-of-the-thorax — UAMS — Visceral Structures of the Thorax
