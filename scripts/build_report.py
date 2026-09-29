from pathlib import Path
import json,csv,html,math
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'site/auditoria'
AUDIT.mkdir(parents=True,exist_ok=True)
d=json.loads((AUDIT/'matriz_coracao.json').read_text())
rows=d['alvos'];p=d['resumo']['principal'];e=d['resumo']['complemento_docente']
counts=Counter(r['status'] for r in rows)
total=len(rows);potential=counts['geometria_disponivel']+counts['parcial_ou_a_conferir']
minimum=math.ceil(total*.9);gap=minimum-potential
labels={'geometria_disponivel':'Geometria localizada','parcial_ou_a_conferir':'Parcial / a conferir','nao_localizado':'Não localizado'}
sources={m['id']:m for m in json.loads((ROOT/'materiais/manifest.json').read_text())}

text=f'''# Coração 3D — auditoria e proposta de modelo próprio

Auditoria de 28/09/2026. Referência principal: **Roteiro de Circulatório 3**, da Prof.ª Carmem Patrícia Barbosa, 125 itens em 5 páginas. As subdivisões expressas no roteiro resultaram em **156 alvos**, preservando os números originais. Os slides de coração e de vasos acrescentam **22 alvos cardíacos** ao levantamento; não se presume que o levantamento documental determine sozinho o conteúdo da avaliação.

## Resultado para o critério de 90%

| Recorte | Geometria localizada | Parcial / a conferir | Não localizado | Potencial identificado, incluindo parciais |
|---|---:|---:|---:|---:|
| Roteiro prático | {p['geometria_disponivel']}/{p['total']} | {p['parcial_ou_a_conferir']} | {p['nao_localizado']} | {p['potencial_incluindo_parciais_percentual']:.1f}% |
| Adições dos slides | {e['geometria_disponivel']}/{e['total']} | {e['parcial_ou_a_conferir']} | {e['nao_localizado']} | {e['potencial_incluindo_parciais_percentual']:.1f}% |
| Conjunto levantado | {counts['geometria_disponivel']}/{total} | {counts['parcial_ou_a_conferir']} | {counts['nao_localizado']} | {potential/total*100:.1f}% |

**Os modelos examinados não satisfazem o critério de 90% confirmado.** A coluna de potencial já concede crédito provisório a todos os parciais. Ela é um limite do mapeamento encontrado, não uma prova de que seja impossível localizar outros detalhes em arquivos ainda não examinados. A conferência anatômica individual completa ainda não foi concluída para cada geometria localizada.

Para 90% do roteiro seriam necessários pelo menos **141 de 156 alvos**. Mesmo validando os 47 parciais, faltariam **24 dos 39 alvos não localizados**. Para o conjunto com os slides seriam necessários **{minimum} de {total}**, ou seja, resolver os {counts['parcial_ou_a_conferir']} parciais e acrescentar pelo menos **{gap} dos {counts['nao_localizado']} não localizados**. Este é um cálculo de cobertura, não uma estimativa de facilidade ou de tempo.

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
'''
(AUDIT/'RELATORIO.md').write_text(text,encoding='utf-8')

groups=[]
for group in dict.fromkeys(r['grupo'] for r in rows):
    rs=[r for r in rows if r['grupo']==group]
    cs=Counter(r['status'] for r in rs)
    groups.append({'grupo':group,'total':len(rs),**{s:cs[s] for s in labels}})
(ROOT/'resumo_por_grupo.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))

body=[]
for r in rows:
    s=r['status'];name=html.escape(r['estrutura']);source=html.escape(f"{r['fonte']}, p. {r['pagina']}")
    evidence='; '.join(r['z_evidencia']) + (' | BodyParts3D: '+', '.join(r['bp_evidencia']) if r['bp_evidencia'] else '')
    body.append(f'<tr data-status="{s}" data-scope="{r["escopo"]}"><td>{r["id"]}</td><td><strong>{name}</strong><small>{source}</small></td><td><span class="status {s}">{labels[s]}</span></td><td>{html.escape(evidence) or "—"}<small>{html.escape(r["observacao"])}</small></td><td>{html.escape(r["plano_modelo_proprio"])}</td></tr>')
htmltext='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Auditoria — coração 3D</title>
<style>body{font:16px/1.5 system-ui,sans-serif;color:#253040;background:#f5f6f8;margin:0}main{max-width:1300px;margin:auto;padding:35px 24px}h1{font-size:34px;margin:.2em 0}h2{font-size:22px;margin-top:2em}p{max-width:950px}a{color:#174b91}.cards{display:flex;gap:15px;flex-wrap:wrap}.card{background:#fff;padding:18px 24px;border-radius:12px;border:1px solid #d9dde4;min-width:180px}.card b{display:block;font-size:32px}.filters{display:flex;gap:12px;margin:20px 0;flex-wrap:wrap}input,select{padding:12px;font:inherit;border:1px solid #bbb;border-radius:7px}input{flex:1;min-width:240px}.table{overflow:auto;background:#fff;border-radius:10px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:13px;text-align:left;border-bottom:1px solid #e0e4e9;vertical-align:top}th{background:#e6ebf0;position:sticky;top:0}td:nth-child(2){min-width:220px}td:nth-child(4),td:nth-child(5){min-width:250px}small{display:block;color:#566273;margin-top:6px}.status{display:inline-block;border-radius:5px;padding:4px 7px;font-size:12px;min-width:90px}.geometria_disponivel{background:#dbece5}.parcial_ou_a_conferir{background:#fff0cc}.nao_localizado{background:#f6dedb}img{max-width:100%;background:white;border-radius:12px}.note{border-left:4px solid #98592b;background:#fff6e9;padding:16px 20px}.muted{color:#576577}button{font:inherit;padding:10px 18px;cursor:pointer}</style>
<main><p class="muted">28/09/2026 · Referência: roteiro e slides da Carmem</p><h1>Coração 3D — auditoria de cobertura</h1>
<p>156 alvos do roteiro prático e 22 detalhes adicionais dos slides. Os números abaixo descrevem a disponibilidade encontrada nos arquivos, antes da construção de um modelo próprio.</p>
<div class="cards"><div class="card"><b>70 / 156</b>Com geometria associada no roteiro</div><div class="card"><b>47</b>Parciais ou a conferir</div><div class="card"><b>39</b>Sem geometria localizada</div><div class="card"><b>75%</b>Potencial, incluindo os parciais</div></div>
<p class="note"><strong>O critério de 90% confirmado ainda não foi atingido.</strong> Geometria localizada não significa validação anatômica completa. Mesmo concedendo crédito aos 47 parciais, faltam pelo menos 24 alvos do roteiro. Incluindo os slides: 73 localizados, 52 parciais e 53 não localizados; potencial de 70,2%.</p>
<p>Um modelo próprio pode reaproveitar as estruturas existentes e acrescentar as lacunas com referências. Cada acréscimo precisa registrar origem, vistas de conferência e simplificações. Detalhes apenas planejados não aumentam a cobertura.</p>
<p><a href="RELATORIO.md">Relatório completo e critérios</a> · <a href="matriz_coracao.csv">Baixar matriz CSV</a> · <a href="matriz_coracao.json">Dados e referências</a></p>
<h2>Inspeção da base disponível</h2><p>Geometria original do Z-Anatomy, renderizada sem acrescentar estruturas. As cordas aparecem incorporadas aos folhetos. Os cortes servem para inspecionar o interior; não são reconstruções de dissecções.</p><img src="evidencias/z_coracao_inspecao.png" alt="Seis vistas renderizadas das câmaras, folhetos e músculos papilares do modelo original">
<h2>Matriz de estruturas</h2><div class="filters"><input id="q" placeholder="Buscar estrutura, fonte ou identificação"><select id="status"><option value="">Todos os resultados</option value="geometria_disponivel">Geometria localizada</option><option value="parcial_ou_a_conferir">Parcial / a conferir</option><option value="nao_localizado">Não localizado</option></select><select id="scope"><option value="">Roteiro e slides</option value="principal">Roteiro prático</option><option value="complemento_docente">Adições dos slides</option></select></div><p id="count" class="muted"></p><div class="table"><table><thead><tr><th>Item</th><th>Estrutura / fonte</th><th>Resultado</th><th>Evidência e limites</th><th>Trabalho no modelo próprio</th></tr></thead><tbody>'''+''.join(body)+'''</tbody></table></div><p class="muted">Fontes: BodyParts3D / DBCLS (CC BY 4.0) e Z-Anatomy (CC BY-SA 4.0). Ver arquivos de licença e detalhes no relatório.</p></main>
<script>const q=document.querySelector('#q'),s=document.querySelector('#status'),c=document.querySelector('#scope'),rows=[...document.querySelectorAll('tbody tr')];const norm=t=>t.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();function filter(){let n=0;for(const r of rows){const show=norm(r.textContent).includes(norm(q.value))&&(!s.value||r.dataset.status===s.value)&&(!c.value||r.dataset.scope===c.value);r.hidden=!show;if(show)n++}document.querySelector('#count').textContent=n+' de '+rows.length+' alvos exibidos'}[q,s,c].forEach(x=>x.addEventListener('input',filter));filter();</script></html>'''
(AUDIT/'auditoria.html').write_text(htmltext,encoding='utf-8')
print(json.dumps({'principal':p,'total':total,'minimum_90':minimum,'potential':potential,'remaining_if_partials_pass':gap},ensure_ascii=False))
