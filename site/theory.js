const $=id=>document.getElementById(id);
const params=new URLSearchParams(location.search);
const system=params.get('system')==='respiratory'?'respiratory':'circulatory';
const key=`atlas:theory:${system}`;
const normalize=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let data,chapter,partsById=new Map(),progress={read:{},answers:{}},queue=[],questionIndex=0,reviewedNow=0;
const record=value=>value&&typeof value==='object'&&!Array.isArray(value);
try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(record(saved)){if(record(saved.read))progress.read=Object.fromEntries(Object.entries(saved.read).filter(([,value])=>value===true));if(record(saved.answers))progress.answers=Object.fromEntries(Object.entries(saved.answers).filter(([,value])=>record(value)&&['known','review'].includes(value.rating)));}}catch{}
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
const button=(label,cls,handler)=>{const b=el('button',cls,label);b.type='button';b.addEventListener('click',handler);return b;};
function save(){try{localStorage.setItem(key,JSON.stringify(progress));$('theory-status').textContent='Progresso salvo neste navegador';}catch{$('theory-status').textContent='Progresso disponível somente nesta sessão';}}
function seconds(time){if(typeof time==='number')return time;const value=String(time||'').match(/\d{1,2}:\d{2}(?::\d{2})?/);return value?value[0].split(':').reduce((v,n)=>v*60+Number(n),0):0;}
const docAliases={coracao:'coracao',vasos:'vasos',linfatico:'linfatico',respiratorio:'respiratorio',roteiro:'roteiro',C:'coracao',V:'vasos',L:'linfatico'};
function sourceInfo(ref){
 const id=typeof ref==='string'?ref:ref.source;
 const source=data.sources?.find(s=>s.id===id)||{id,label:id||'Referência'};
 const page=typeof ref==='object'?ref.page:null,time=typeof ref==='object'?ref.time:null;
 let url=source.url||null;
 if(docAliases[id])url=`classroom.html?doc=${docAliases[id]}${page?'&page='+encodeURIComponent(String(page).match(/\d+/)?.[0]||1):''}`;
 if(/^[CR][1-4]$/.test(id))url=`classroom.html?video=${id}&t=${seconds(time)}`;
 return {source,page,time,url,label:`${source.label||id}${page?' · p. '+(Array.isArray(page)?page.join(', '):page):''}${time?' · '+time:''}`};
}
function refs(list){const box=el('div','source-links');for(const ref of list||[]){const info=sourceInfo(ref);if(info.url){const a=el('a','',info.label);a.href=info.url;if(info.source.note)a.title=info.source.note;if(/^https?:/.test(info.url)){a.target='_blank';a.rel='noopener noreferrer';}box.append(a);}else box.append(el('span','',info.label));}return box;}
function renderNavigation(){
 const term=normalize($('chapter-search').value);$('chapter-list').replaceChildren();
 data.chapters.forEach((c,i)=>{if(term&&!normalize(JSON.stringify(c)).includes(term))return;const b=button('','',()=>selectChapter(c.id,true));b.append(el('span','number',String(i+1).padStart(2,'0')),el('span','',c.title));if(progress.read[c.id])b.append(el('span','read','✓'));if(chapter?.id===c.id)b.setAttribute('aria-current','page');$('chapter-list').append(b);});
 const read=data.chapters.filter(c=>progress.read[c.id]).length;$('reading-count').textContent=`${read} de ${data.chapters.length} unidades lidas`;$('reading-progress').max=data.chapters.length;$('reading-progress').value=read;
 if(!$('chapter-list').children.length)$('chapter-list').append(el('p','inline-note','Nenhuma unidade com esse termo.'));
}
function selectChapter(id,scroll=false){
 chapter=data.chapters.find(c=>c.id===id)||data.chapters[0];if(!chapter)return;
 const index=data.chapters.indexOf(chapter),article=$('chapter');article.replaceChildren();
 article.append(el('span','chapter-label',`${system==='respiratory'?'RESPIRATÓRIO':'CIRCULATÓRIO'} / UNIDADE ${String(index+1).padStart(2,'0')}`),el('h1','chapter-title',chapter.title),el('p','chapter-summary',chapter.summary));
 const notes=[...(data.editorialNotes||[]),...(data.limitations||[])];
 if(notes.length){const details=el('details','editorial-notes');details.append(el('summary','','Como este conteúdo foi preparado'));for(const note of notes)details.append(el('p','inline-note',typeof note==='string'?note:JSON.stringify(note)));article.append(details);}
 if(chapter.objectives?.length){const objectives=el('section','objectives');objectives.append(el('h2','','Ao terminar, você deve conseguir'));const ul=el('ul');chapter.objectives.forEach(o=>ul.append(el('li','',o)));objectives.append(ul);article.append(objectives);}
 if(chapter.partIds?.length){const related=el('details','related-anatomy');related.append(el('summary','',`Explorar as peças relacionadas a esta unidade (${chapter.partIds.length})`));const links=el('div','related-part-links');for(const id of chapter.partIds){const p=partsById.get(id);if(!p)continue;const a=el('a','',p.label);a.href=`atlas.html?system=${system}&part=${encodeURIComponent(id)}`;links.append(a);}related.append(links,el('p','inline-note','Associação para estudo: os detalhes descritos no texto podem não estar individualizados na peça. Consulte o roteiro e as figuras da aula.'));article.append(related);}
 for(const section of chapter.sections||[]){const block=el('section','lesson-section');if(section.heading)block.append(el('h2','',section.heading));for(const p of section.paragraphs||[])block.append(el('p','',p));if(section.bullets?.length){const ul=el('ul');section.bullets.forEach(p=>ul.append(el('li','',p)));block.append(ul);}if(section.table?.rows?.length){const wrap=el('div','lesson-table-wrap'),table=el('table'),thead=el('thead'),header=el('tr');for(const h of section.table.headers||[])header.append(el('th','',h));thead.append(header);table.append(thead);const tbody=el('tbody');for(const row of section.table.rows){const tr=el('tr');for(const value of row)tr.append(el('td','',value));tbody.append(tr);}table.append(tbody);wrap.append(table);block.append(wrap);}block.append(refs(section.references));article.append(block);}
 if(chapter.recall?.length){const box=el('section','chapter-recall');box.append(el('h2','','Consegue explicar sem consultar?'),el('p','',`${chapter.recall.length} perguntas para recuperar o conteúdo e identificar os pontos que precisam de revisão.`),button('Praticar esta unidade','action',()=>startReview(chapter.recall)));article.append(box);}
 const bottom=el('div','chapter-bottom');const mark=button(progress.read[chapter.id]?'✓ Unidade marcada como lida':'Marcar unidade como lida','action mark-read',()=>{progress.read[chapter.id]=!progress.read[chapter.id];save();selectChapter(chapter.id);});mark.setAttribute('aria-pressed',String(Boolean(progress.read[chapter.id])));bottom.append(mark);
 if(index<data.chapters.length-1)bottom.append(button('Próxima unidade →','action',()=>selectChapter(data.chapters[index+1].id,true)));article.append(bottom);
 const url=new URL(location.href);url.searchParams.set('system',system);url.searchParams.set('chapter',chapter.id);history.replaceState(null,'',url);
 const firstPart=chapter.partIds?.[0];$('go-atlas').href=`atlas.html?system=${system}${firstPart?'&part='+encodeURIComponent(firstPart):''}`;
 $('chapter-visual').replaceChildren();
 const firstRef=(chapter.sections||[]).flatMap(s=>s.references||[]).find(r=>docAliases[r.source]&&r.page);
 if(firstRef){const info=sourceInfo(firstRef),page=String(info.page).match(/\d+/)?.[0];if(page){const link=el('a','',`Conferir a figura: ${info.label} ↗`);link.href=info.url;const img=el('img');img.loading='lazy';img.alt=`Página ${page} do material ${info.source.label}`;img.src=`assets/lectures/slides/${docAliases[firstRef.source]}/${page}.jpg`;img.addEventListener('error',()=>img.remove());link.prepend(img);$('chapter-visual').append(link);}}
 renderNavigation();if(scroll)article.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
}
function startReview(questions){
 const scores={review:0,undefined:1,known:2};queue=[...questions].sort((a,b)=>(scores[progress.answers[a.id]?.rating]??1)-(scores[progress.answers[b.id]?.rating]??1));questionIndex=0;reviewedNow=0;
 if(!$('review-dialog').open)$('review-dialog').showModal();renderQuestion();
}
function renderQuestion(){
 const holder=$('review-body');holder.replaceChildren();
 if(questionIndex>=queue.length){holder.append(el('h2','','Rodada concluída'),el('p','recall-complete',`Você revisou ${reviewedNow} ${reviewedNow===1?'pergunta':'perguntas'}. Volte aos pontos marcados antes de uma nova rodada.`));const review=queue.filter(q=>progress.answers[q.id]?.rating==='review');const actions=el('div','recall-actions');if(review.length)actions.append(button(`Rever ${review.length} ${review.length===1?'pergunta':'perguntas'}`,'action primary',()=>startReview(review)));actions.append(button('Voltar à leitura','action',()=>closeReview()));holder.append(actions);holder.querySelector('h2').tabIndex=-1;holder.querySelector('h2').focus();return;}
 const q=queue[questionIndex];holder.append(el('p','recall-counter',`${questionIndex+1} de ${queue.length} · questão original de revisão`));const heading=el('h2','',q.question);heading.tabIndex=-1;holder.append(heading);
 const label=el('label','','Explique em voz alta ou escreva um rascunho (opcional)');label.htmlFor='recall-draft';const draft=el('textarea');draft.id='recall-draft';draft.placeholder='Tente recuperar a resposta antes de revelar…';holder.append(label,draft);
 const actions=el('div','recall-actions');actions.append(button('Revelar resposta','action primary',()=>{const answer=el('section','recall-answer');answer.append(el('strong','','Resposta'),el('p','',q.answer));if(q.explanation)answer.append(el('strong','','Por quê?'),el('p','',q.explanation));answer.append(refs(q.references));actions.before(answer);draft.readOnly=true;actions.replaceChildren(button('Expliquei com segurança','action primary',()=>rate(q,'known')),button('Preciso revisar','action',()=>rate(q,'review')));actions.querySelector('button').focus({preventScroll:true});}),button('Deixar para depois','action',()=>{if(questionIndex<queue.length-1){queue.push(queue.splice(questionIndex,1)[0]);renderQuestion();}else closeReview();}));holder.append(actions,el('p','recall-note','A autoavaliação registra sua revisão. Compare seu raciocínio com a explicação e confira as referências.'));heading.focus({preventScroll:true});
}
function rate(q,rating){progress.answers[q.id]={rating,at:Date.now()};save();questionIndex++;reviewedNow++;renderQuestion();}
function closeReview(){$('review-dialog').close();$('review-all').focus({preventScroll:true});}
$('review-close').addEventListener('click',closeReview);$('chapter-search').addEventListener('input',renderNavigation);$('print-chapter').addEventListener('click',()=>window.print());
for(const a of document.querySelectorAll('[data-system]'))if(a.dataset.system===system)a.setAttribute('aria-current','page');
try{try{const models=await fetch(system==='respiratory'?'assets/respiratory/catalog.json':'assets/catalog.json');if(models.ok)partsById=new Map((await models.json()).parts.map(p=>[p.id,p]));}catch{}const response=await fetch(system==='respiratory'?'assets/respiratory/theory.json':'assets/circulatory-theory.json');if(!response.ok)throw new Error('O conteúdo desta unidade não está disponível nesta instalação.');data=await response.json();if(!data.chapters?.length)throw new Error('Nenhuma unidade de teoria encontrada.');selectChapter(params.get('chapter'));$('review-all').addEventListener('click',()=>startReview(data.chapters.flatMap(c=>c.recall||[])));if(params.get('mode')==='review')startReview(data.chapters.flatMap(c=>c.recall||[]));}catch(error){$('chapter').replaceChildren(el('h1','chapter-title','Teoria indisponível'),el('p','empty-state',error.message));$('reading-count').textContent='Conteúdo não carregado';$('review-all').disabled=true;}
