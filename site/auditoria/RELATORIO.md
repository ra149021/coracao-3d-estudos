# Coração 3D — auditoria e proposta de modelo próprio

Auditoria de 28/09/2026. Referência principal: **Roteiro de Circulatório 3**, da Prof.ª Carmem Patrícia Barbosa, 125 itens em 5 páginas. As subdivisões expressas no roteiro resultaram em **156 alvos**, preservando os números originais. Os slides de coração e de vasos acrescentam **22 alvos cardíacos** ao levantamento; não se presume que o levantamento documental determine sozinho o conteúdo da avaliação.

## Resultado para o critério de 90%

| Recorte | Geometria localizada | Parcial / a conferir | Não localizado | Potencial identificado, incluindo parciais |
|---|---:|---:|---:|---:|
| Roteiro prático | 70/156 | 47 | 39 | 75.0% |
| Adições dos slides | 3/22 | 5 | 14 | 36.4% |
| Conjunto levantado | 73/178 | 52 | 53 | 70.2% |

**Os modelos examinados não satisfazem o critério de 90% confirmado.** A coluna de potencial já concede crédito provisório a todos os parciais. Ela é um limite do mapeamento encontrado, não uma prova de que seja impossível localizar outros detalhes em arquivos ainda não examinados. A conferência anatômica individual completa ainda não foi concluída para cada geometria localizada.

Para 90% do roteiro seriam necessários pelo menos **141 de 156 alvos**. Mesmo validando os 47 parciais, faltariam **24 dos 39 alvos não localizados**. Para o conjunto com os slides seriam necessários **161 de 178**, ou seja, resolver os 52 parciais e acrescentar pelo menos **36 dos 53 não localizados**. Este é um cálculo de cobertura, não uma estimativa de facilidade ou de tempo.

## O que dá para reaproveitar

- Paredes das quatro câmaras, grandes vasos, parte dos ramos coronários e das veias cardíacas.
- Folhetos das quatro valvas, com arquivos complementares no BodyParts3D para os folhetos anteriores que não aparecem como objetos próprios no Z-Anatomy examinado.
- Músculos papilares e cordas tendíneas: as cordas são visíveis na amostra renderizada, incorporadas a malhas de folhetos. A ausência de uma malha chamada “cordas tendíneas” **não significa** ausência visual.
- Superfícies, margens, ápice, base e sulcos podem ser delimitados na geometria existente; a seleção precisa ser conferida.

## Lacunas relevantes

- Pericárdio fibroso, lâmina parietal, reflexões, seios e ligamentos de fixação.
- Camadas miocárdicas e organização das fibras exigidas no roteiro.
- Esqueleto fibroso: quatro anéis e dois trígonos.
- Relevos internos como musculatura pectínea, crista terminal, limbo da fossa oval, trabécula septomarginal e trabéculas cárneas.
- Alguns ramos atriais/nodais coronários, veia oblíqua do átrio esquerdo, vasos pericardicofrênicos e nervo frênico.
- Nos slides: plexos cardíacos, sistema de condução e plexos linfáticos.

O Z-Anatomy inclui coleções chamadas `Pericardium`, `Fibrous skeleton of heart`, `Conducting system of heart` e `Sternopericardial ligaments`, porém as respectivas árvores não contêm malhas ou curvas com volume nos dados examinados. Categorias, descrições e marcadores vazios foram excluídos do crédito por geometria.

## Modelo próprio

É tecnicamente possível montar um modelo próprio combinando as bases abertas, segmentando estruturas agregadas e criando os detalhes faltantes. Isso permite usar o roteiro como especificação e registrar a origem de cada estrutura.

1. **Base anatômica:** reaproveitar e registrar as geometrias com origem conhecida; alinhar escala, eixos e posições antes de combinar os dois acervos.
2. **Estruturas incorporadas:** separar aurículas, faces, bordas, septos, óstios e cordas apenas quando os limites estiverem sustentados pela geometria e pelas figuras.
3. **Geometria criada:** construir anéis, trígonos, pericárdio, reflexões, ligamentos e relevos internos a partir de múltiplas vistas. Um diagrama em uma única vista não determina sozinho sua forma 3D.
4. **Representações didáticas:** camadas/fibras do miocárdio, plexos e condução podem ser esquemas 3D identificados. Cobertura didática e fidelidade realista devem ter registros separados.
5. **Nova auditoria:** para cada item, registrar fonte/página, estrutura selecionável, vistas de conferência, simplificações e resultado. Uma estrutura planejada ou simplesmente rotulada não entra como concluída.

O roteiro detalhado de aproveitamento/modelagem está na última coluna da matriz. Não se atribuiu crédito a geometrias que ainda precisariam ser criadas. A decisão sobre incluir aproximações didáticas no limiar de 90% permanece uma preferência de fidelidade; ela não foi usada para aumentar o resultado desta auditoria.

## Critérios e exceções

- O item 30i repete literalmente a veia pulmonar direita superior de 30h; foi contado uma vez. A veia inferior direita aparece como complemento dos slides.
- O seio coronário repetido em 108 e as coronárias repetidas em 120 não foram contados novamente.
- Foram separados os folhetos valvares e os ramos explicitamente nomeados. As cinco camadas miocárdicas mantêm os grupos escritos pela professora.
- Peso e diâmetro são informações textuais, fora do denominador geométrico. Localização e sintopia permanecem dois alvos espaciais.
- Óstios das quatro veias pulmonares e três veias principais do sistema ázigos foram desdobrados; essa escolha está explícita para permitir recalcular o escopo.
- Foram preservadas as diferenças terminológicas posterior/inferior e as discrepâncias de orientação das cúspides sem equivalências automáticas.
- Linfonodo do ligamento arterial não foi contado como ligamento arterial. Descrição de nervo ou artéria sem geometria correspondente não recebeu crédito.
- O escopo não foi ampliado para histologia, anatomia respiratória completa, circulação fetal completa ou sistemas porta.

## Arquivos examinados e verificação

- [BodyParts3D 4.0 — arquivo oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html): ZIP de 142.903.898 bytes, 2.234 membros; verificação CRC concluída. Os conceitos foram ligados aos OBJ pelos identificadores FMA/FJ, com checagem de vértices e faces dos arquivos usados no mapeamento.
- [Z-Anatomy — arquivo original](https://github.com/Z-Anatomy/Models-of-human-anatomy): revisão `7cc49aa8749632adcd564c0e75f096dc43f6a4b8`; ZIP e arquivos auxiliares conferidos contra os hashes Git. Leitura do `Startup.blend` 3.5 sem executar scripts incorporados; 7.184 objetos e 1.944 coleções inspecionados. Curvas com seção e pontos também foram consideradas geometria.
- [Z-Anatomy — exportação para o aplicativo](https://github.com/LluisV/Z-Anatomy/tree/PC-Version/Resources/Models): `CardioVascular41.fbx`, revisão `6c7f9016bd5899ac8edafd31b9900c151df42ed6`, importado e convertido com Assimp para inspeção. É outro formato/versão do mesmo projeto, não validação anatômica independente.
- Os três PDFs docentes foram abertos e reextraídos, com hashes e páginas preservados. A extração dos 125 números do roteiro foi conferida. As páginas 1–3 do roteiro e uma amostra de seis vistas do coração foram examinadas visualmente. Isso não equivale a inspeção visual de todos os 178 alvos.
- Não foi possível completar a leitura de cena pelo módulo bpy: ocorreu falha nativa. A geometria foi lida pelos blocos SDNA do arquivo, com checagens dos tamanhos, índices e coordenadas; o inventário e os scripts permitem reproduzir a análise.

Busca complementar encontrou uma base cardíaca do APIL por CT com [limitação declarada para os anéis valvares](https://sketchfab.com/3d-models/human-heart-base-fa8eba4530a84f758ac50df3b4e168f0) e um [esquema de pericárdio com formas simplificadas declaradas pelo autor](https://sketchfab.com/3d-models/pericardium-909899e34f1e4e399d0ae7b7c275fbef). Essas páginas são pistas para referências; seus arquivos não foram incorporados nem contados como cobertura local validada. A busca não é um inventário de todos os modelos existentes na internet.

## Licenças e atribuição

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International, conforme [licença atual do arquivo oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html). Z-Anatomy — The libre 3D atlas of anatomy — CC BY-SA 4.0. O pacote Z-Anatomy contém contribuições de outras regiões com licenças específicas; os avisos originais foram preservados. Nenhum modelo proprietário foi extraído.

## Entregáveis

- [Matriz completa em CSV](matriz_coracao.csv)
- [Matriz e método em JSON](matriz_coracao.json)
- [Requisitos e regras de contagem](requisitos.json)
- [Vistas da geometria original do Z-Anatomy](evidencias/z_coracao_inspecao.png)
- `materiais/`: textos por página e referências aos PDFs originais.
- `fontes/`: arquivos oficiais, licenças e hashes.
- `malhas/`: inventários e geometrias extraídas para inspeção.
- `scripts/`: procedimentos da auditoria.
