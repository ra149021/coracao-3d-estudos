# Conteúdo respiratório — entrega

## Arquivos estáveis

- `site/assets/respiratory/requirements.json`: 222 alvos, com IDs editoriais estáveis R001–R222. São 221 alvos sustentados pelo material de Carmem e 1 complementar (margens posteriores). A seleção é **roteiro de estudo derivado dos slides**, não roteiro oficial confirmado da prova.
- `site/assets/respiratory/practice-evidence.json`: 222 entradas; 217 com localização de trechos ASR e 105 com observações de figuras inspecionadas. Os trechos frequentemente sustentam o grupo anatômico, não todos os seus termos individualmente.
- `site/assets/respiratory/theory.json`: 12 capítulos, 49 seções, 58 questões autorais com respostas e explicações. Referências aos slides usam `respiratorio` e páginas físicas 1-based; aulas usam R1–R4.

Integridade conferida: IDs únicos, igualdade entre alvos e evidências, referências existentes, páginas 1–144, colunas de tabelas consistentes, ausência de caminhos pessoais nos três JSONs. Há vínculos a 118 peças do catálogo respiratório. Essa conferência não equivale a validação anatômica integral de malhas.

## Fontes e grau de revisão

Texto de 144 páginas dos slides de Carmem disponível em `slides_pages.json`. Figuras inspecionadas nas páginas 10, 11, 13, 36, 44, 66, 72, 81, 92, 93, 102, 103, 104, 105, 108, 109 e 117.

Transcrições R1–R4 serviram para localizar temas e ênfases. Não houve revisão integral do áudio. A ASR apresenta substituições de termos, inversões e simplificações que não foram copiadas como gabarito.

A lista recuperada do aplicativo respiratório é identificada no próprio material como sendo de Cláudia Regina Pinheiro Lopes. Seus oito grupos e referências originais de itens foram preservados como metadados; não foi promovida a roteiro oficial de Carmem.

## Revisões anatômicas que a interface deve preservar

| Tema | Formulação adotada |
|---|---|
| Tuba auditiva, slide44 | Comunica nasofaringe e orelha média. Não drena perilinfa dos canais semicirculares. |
| Glote | Pregas vocais + rima; rima é a abertura entre elas. |
| Cricotireóideo | Principalmente tensor/alongador das pregas; não memorizar apenas como adutor. |
| Cricoaritenóideo posterior | Único par abdutor das pregas. |
| Laríngeos recorrentes | Direito contorna subclávia direita; esquerdo, arco aórtico. |
| Traqueia | Início C6 e bifurcação usual próxima a T4–T5/ângulo esternal; posição variável. T6 do slide não é limite fixo universal. |
| Hilo e raiz | Região de passagem versus conjunto de estruturas. |
| Ligamento pulmonar | Dupla prega pleural inferior à raiz; interpretar na continuidade dos folhetos, não como cordão sólido. |
| Zona condutora | Termina no bronquíolo terminal; respiratória inicia no bronquíolo respiratório. |
| Surfactante | Reduz tensão superficial; deficiência favorece colapso e baixa complacência, não ruptura como mecanismo básico. |
| Pressões | Expansão reduz pressão alveolar transitoriamente; distinguir alveolar, atmosférica e intrapleural. |
| Segmentação esquerda | Convenção do slide93: apicoposterior combinado, basais medial e anterior separados. Outros atlas podem combinar os basais. |

Fontes institucionais de revisão estão declaradas nos JSONs: UAMS, University of Utah e OpenStax. Elas resolvem conflitos pontuais; não substituem o material docente como origem da seleção.

## Relação com o 3D

Disponibilidade nominal no inventário não significa representação completa. Os requisitos separam estrutura, região, abertura, espaço, camada, articulação, conjunto e microestrutura. Uma pleura agregada não representa automaticamente todos os folhetos/recessos; cartilagem não equivale a mucosa; ligamento vocal não é uma prega vocal completa.

O catálogo laríngeo independente de BodyParts3D foi informado pelo agente de geometria após a elaboração: mantém sua própria orientação e não deve aumentar artificialmente a cobertura integrada do Z-Anatomy. R069, R081, R082, R089, R091 e R096 têm correspondências adicionais nele; R099/R102 recebem apenas associações com ligamentos vocais. A auditoria de conteúdo não validou essas malhas.

## Ordem de regeneração

1. `python3 refinamento/respiratorio/conteudo/build_content.py`
2. `python3 refinamento/respiratorio/conteudo/enrich_evidence.py`
3. `python3 refinamento/respiratorio/conteudo/build_theory.py`

O primeiro script reinicia as evidências; não executá-lo isoladamente depois de enriquecer o arquivo. A teoria resolve peças pelo catálogo presente no momento da geração. Não inserir requisitos no meio da sequência: novos IDs devem ser acrescentados ao fim.

Não foram publicados PDFs, vídeos ou transcrições brutas nestes entregáveis. Não houve modificação do vault, HTML, app, study ou builders de geometria.
