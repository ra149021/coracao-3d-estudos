const $=id=>document.getElementById(id);
const params=new URLSearchParams(location.search);
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
const button=(label,cls,handler)=>{const b=el('button',cls,label);b.type='button';b.addEventListener('click',handler);return b;};
let libraries={},data,system,progress,queue=[],questionIndex=0,reviewedNow=0;
const session={},pendingAnswers={};
let progressReadable=false;
function loadProgress(){
 const record=value=>value&&typeof value==='object'&&!Array.isArray(value);
 progressReadable=false;
 let saved;
 try{
  saved=JSON.parse(localStorage.getItem(`atlas:theory:${system}`)||'null');
  progressReadable=true;
 }catch{saved=session[system];}
 if(!record(saved))saved={read:{},answers:{}};
 // Always reread storage, then overlay only unsaved question patches, not a stale snapshot.
 saved={...saved,answers:{...(record(saved.answers)?saved.answers:{}),...pendingAnswers[system]}};
 session[system]=saved;
 $('theory-status').textContent=!progressReadable||Object.keys(pendingAnswers[system]||{}).length
  ?'Autoavaliação somente nesta sessão':'Progresso local';
 return saved;
}
function save(questionId){
 (pendingAnswers[system]??={})[questionId]=progress.answers[questionId];
 progress=loadProgress();
 // A writable store is not safe to replace when its existing contents cannot be read.
 if(!progressReadable)return;
 try{
  localStorage.setItem(`atlas:theory:${system}`,JSON.stringify(progress));
  delete pendingAnswers[system];
  $('theory-status').textContent='Autoavaliação salva neste navegador';
 }catch{$('theory-status').textContent='Autoavaliação somente nesta sessão';}
}
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
function startReview(questions){
 const scores={review:0,undefined:1,known:2};queue=[...questions].sort((a,b)=>(scores[progress.answers[a.id]?.rating]??1)-(scores[progress.answers[b.id]?.rating]??1));questionIndex=0;reviewedNow=0;
 renderQuestion();
}
function renderQuestion(){
 const holder=$('review-body');holder.replaceChildren();
 if(questionIndex>=queue.length){holder.append(el('h2','','Rodada concluída'),el('p','recall-complete',`Você revisou ${reviewedNow} ${reviewedNow===1?'pergunta':'perguntas'}. Volte aos pontos marcados antes de uma nova rodada.`));const review=queue.filter(q=>progress.answers[q.id]?.rating==='review');const actions=el('div','recall-actions');if(review.length)actions.append(button(`Rever ${review.length} ${review.length===1?'pergunta':'perguntas'}`,'action primary',()=>startReview(review)));actions.append(button('Nova rodada','action',()=>closeReview()));holder.append(actions);holder.querySelector('h2').tabIndex=-1;holder.querySelector('h2').focus();return;}
 const q=queue[questionIndex];holder.append(el('p','recall-counter',`${questionIndex+1} de ${queue.length} · questão original de revisão`));const heading=el('h2','',q.question);heading.tabIndex=-1;holder.append(heading);
 const label=el('label','','Explique em voz alta ou escreva um rascunho (opcional)');label.htmlFor='recall-draft';const draft=el('textarea');draft.id='recall-draft';draft.placeholder='Tente recuperar a resposta antes de revelar…';holder.append(label,draft);
 const actions=el('div','recall-actions');actions.append(button('Revelar resposta','action primary',()=>{const answer=el('section','recall-answer');answer.append(el('strong','','Resposta'),el('p','',q.answer));if(q.explanation)answer.append(el('strong','','Por quê?'),el('p','',q.explanation));answer.append(refs(q.references));actions.before(answer);draft.readOnly=true;actions.replaceChildren(button('Expliquei com segurança','action primary',()=>rate(q,'known')),button('Preciso revisar','action',()=>rate(q,'review')));actions.querySelector('button').focus({preventScroll:true});}),button('Deixar para depois','action',()=>{if(questionIndex<queue.length-1){queue.push(queue.splice(questionIndex,1)[0]);renderQuestion();}else closeReview();}));holder.append(actions,el('p','recall-note','A autoavaliação registra sua revisão. Compare seu raciocínio com a explicação e confira as referências.'));heading.focus({preventScroll:true});
}
function rate(q,rating){progress.answers[q.id]={rating,at:Date.now()};save(q.id);questionIndex++;reviewedNow++;renderQuestion();}
function closeReview(){startReview(selectedQuestions());}

function selectedQuestions(){return data.chapters.filter(c=>!$('exercise-chapter').value||c.id===$('exercise-chapter').value).flatMap(c=>c.recall||[]);}
function selectFilters(chapterId=''){
 if(!libraries[$('exercise-system').value])return;
 system=$('exercise-system').value;data=libraries[system];progress=loadProgress();if(!progress.answers||typeof progress.answers!=='object')progress.answers={};
 $('exercise-chapter').replaceChildren(new Option('Todas as unidades',''),...data.chapters.map(c=>new Option(c.title,c.id)));
 if(data.chapters.some(c=>c.id===chapterId))$('exercise-chapter').value=chapterId;
 begin();
}
function begin(){
 if(!data)return;
 const chapter=$('exercise-chapter').value;
 const query=new URLSearchParams({system});if(chapter)query.set('chapter',chapter);
 history.replaceState(null,'',`exercises.html?${query}`);
 $('back-reading').href=`theory.html?${query}`;
 $('recognition-link').href=`atlas.html?system=${system}&mode=practice`;
 const unit=data.chapters.find(c=>c.id===chapter),part=unit?.partIds?.[0];if(part)$('recognition-link').href+=`&part=${encodeURIComponent(part)}`;
 $('exercise-count').textContent=`${selectedQuestions().length} perguntas neste filtro · 105 na base completa`;
 startReview(selectedQuestions());
}
$('exercise-system').addEventListener('change',()=>selectFilters());
$('exercise-chapter').addEventListener('change',begin);
try{
 const results=await Promise.all(['assets/circulatory-theory.json','assets/respiratory/theory.json'].map(async url=>{const r=await fetch(url);if(!r.ok)throw new Error('Não foi possível carregar as perguntas.');return r.json();}));
 libraries={circulatory:results[0],respiratory:results[1]};
 $('exercise-system').value=params.get('system')==='respiratory'?'respiratory':'circulatory';selectFilters(params.get('chapter'));
 $('exercise-system').disabled=false;$('exercise-chapter').disabled=false;
}catch(error){$('review-body').replaceChildren(el('h2','','Exercícios indisponíveis'),el('p','',error.message));$('exercise-count').textContent='Conteúdo não carregado';}
