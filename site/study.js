/** Practical study tools. All questions use parts loaded by the viewer. */
export function initStudy({ parts, requirements = [], evidence = null, viewer, system = 'circulatory', storageId = system, groupNames = null, scopeNote = null }) {
  if (!viewer || !Array.isArray(parts)) throw new TypeError('Prática: catálogo ou visualizador indisponível.');
  const present = parts.filter(p => p.id && p.label && p.triangles > 0);
  const byId = new Map(present.map(p => [p.id, p]));
  const eligible = present.filter(p => p.quizEligible !== false);
  const eligibleIds = new Set(eligible.map(p => p.id));
  const evidenceTargets = new Map((Array.isArray(evidence?.targets) ? evidence.targets : []).map(row => [String(row.id), row]));
  const evidenceSources = new Map((Array.isArray(evidence?.sources) ? evidence.sources : []).map(source => [source.id, source.label]));
  const groups = groupNames || { camaras: 'Câmaras', grandes: 'Grandes vasos', coronarias: 'Artérias coronárias', veias: 'Veias cardíacas', valvas: 'Folhetos valvares', papilares: 'Músculos papilares', contexto: 'Vasos e linfáticos de contexto' };
  const cardiacEligible = eligible.filter(p => !p.group.startsWith('contexto'));
  const storageKey = `atlas:practice:v3:${storageId}`;
  const systemLabel = system === 'respiratory' ? 'Respiratório' : 'Coração';
  let storageAvailable = true, active = false, revealed = false, savedView = null, misses = 0;
  let progress = { version: 2, ratings: {}, session: null };
  try {
    const legacy = system === 'circulatory' ? localStorage.getItem('heart-atlas:practice:v2:/') || localStorage.getItem('heart-atlas:practice:v2:/index.html') : null;
    const saved = JSON.parse(localStorage.getItem(storageKey) || legacy || 'null');
    if (saved?.version === 2 && saved.ratings && typeof saved.ratings === 'object') progress = saved;
  } catch { storageAvailable = false; }
  const validSession = progress.session;
  if (validSession && Array.isArray(validSession.queue) && Array.isArray(validSession.done) && ['identify','find'].includes(validSession.mode)) {
    if (validSession.group !== 'all' && !eligible.some(p => p.group === validSession.group)) validSession.group = 'all';
    const belongs = id => eligibleIds.has(id) && (validSession.group === 'all' ? byId.get(id).group !== 'contexto' : byId.get(id).group === validSession.group);
    validSession.queue = [...new Set(validSession.queue)].filter(belongs);
    validSession.done = [...new Set(validSession.done)].filter(id => belongs(id) && !validSession.queue.includes(id));
    validSession.total = validSession.queue.length + validSession.done.length;
  } else progress.session = null;

  const css = document.createElement('link');
  css.rel = 'stylesheet'; css.href = new URL('./study.css', import.meta.url).href;
  css.dataset.heartStudy = 'true'; document.head.append(css);
  const el = (tag, className, content) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = content;
    return node;
  };
  function button(text, className, handler) {
    const node = el('button', className, text); node.type = 'button';
    if (handler) node.addEventListener('click', handler);
    return node;
  }
  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify(progress));localStorage.setItem(`atlas:practice-summary:${storageId}`,JSON.stringify({reviewed:Object.keys(progress.ratings).filter(id=>eligibleIds.has(id)).length,review:Object.entries(progress.ratings).filter(([id,r])=>eligibleIds.has(id)&&r.rating==='review').length,total:eligible.length})); }
    catch { storageAvailable = false; }
  }
  function shuffle(ids) {
    const order = [...ids];
    for (let i = order.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1)); [order[i], order[j]] = [order[j], order[i]];
    }
    return order;
  }
  const toolbar = el('nav', 'study-nav'); toolbar.setAttribute('aria-label', 'Estudo prático');
  const practiceButton = button('Prática', 'button study-launch', () => openSetup());
  const routeButton = button('Roteiro', 'button subtle', () => { pause(); renderRoute(); route.showModal(); });
  toolbar.append(practiceButton, routeButton);
  (document.querySelector('.header-actions') || document.querySelector('.header') || document.body).prepend(toolbar);

  function makeDialog(id, title, eyebrow) {
    const dialog = el('dialog', 'study-dialog'); dialog.id = id; dialog.setAttribute('aria-labelledby', `${id}-title`);
    const heading = el('div', 'study-dialog-heading');
    heading.append(el('span', 'eyebrow', eyebrow), button('×', 'icon-button', () => dialog.close()));
    heading.lastChild.setAttribute('aria-label', `Fechar ${title.toLowerCase()}`);
    const h2 = el('h2', '', title); h2.id = `${id}-title`;
    dialog.append(heading, h2); document.body.append(dialog);
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });
    return dialog;
  }
  const setup = makeDialog('study-setup', 'Treine a identificação', 'PRÁTICA NO MODELO');
  setup.append(el('p', 'study-intro', 'Observe a forma, a posição e as relações entre as peças. Gire o modelo e mude a vista antes de responder.'));
  const setupForm = el('form', 'study-setup-form');
  const modeLabel = el('label', 'study-field', 'Como você quer treinar?');
  const mode = el('select'); mode.id = 'study-mode'; modeLabel.htmlFor = mode.id;
  mode.setAttribute('aria-label','Como você quer treinar?');
  for (const [value, text] of [['identify','Identificar a peça destacada'],['find','Encontrar uma estrutura no 3D']]) {
    const option = el('option', '', text); option.value = value; mode.append(option);
  }
  modeLabel.append(mode);
  const groupLabel = el('label', 'study-field', 'Estruturas desta rodada');
  const group = el('select'); group.id = 'study-group'; groupLabel.htmlFor = group.id;
  group.setAttribute('aria-label','Estruturas desta rodada');
  for (const [value, text] of [['all',`${systemLabel} · todas as peças do treino (${cardiacEligible.length})`], ...Object.entries(groups).filter(([key]) => eligible.some(p => p.group === key)).map(([key,name]) => [key, `${name} (${eligible.filter(p => p.group === key).length})`])]) {
    const option = el('option', '', text); option.value = value; group.append(option);
  }
  groupLabel.append(group); setupForm.append(modeLabel, groupLabel);
  const setupStatus = el('p', 'study-storage-note');
  const setupActions = el('div', 'study-setup-actions');
  const resumeButton = button('Continuar rodada', 'button primary', () => { setup.close(); start(); });
  const newButton = button('Começar rodada', 'button primary'); newButton.type = 'submit';
  setupActions.append(resumeButton, newButton); setupForm.append(setupActions);
  setupForm.addEventListener('submit', event => {
    event.preventDefault();
    const selected = group.value === 'all' ? cardiacEligible : eligible.filter(p => p.group === group.value);
    progress.session = { mode: mode.value, group: group.value, queue: shuffle(selected.map(p => p.id)), done: [], total: selected.length };
    save(); setup.close(); start();
  });
  setup.append(setupForm, setupStatus, el('p', 'study-boundary', 'O treino usa somente peças presentes nesta cena com identificação liberada para as perguntas. Peças parciais ou com equivalência pendente podem aparecer como contexto. O desempenho mede sua revisão; não mede a cobertura nem valida a anatomia do modelo. Consulte o roteiro para ver os detalhes ainda pendentes.'));

  const sessionPanel = el('section', 'study-session'); sessionPanel.hidden = true;
  sessionPanel.setAttribute('aria-labelledby', 'study-question');
  const sessionTop = el('div', 'study-session-top');
  const sessionTitle = el('span', 'eyebrow', 'TREINO PRÁTICO');
  const sessionCount = el('span', 'study-session-count');
  sessionTop.append(sessionTitle, sessionCount, button('Pausar e explorar', 'text-button', () => pause()));
  const sessionProgress = el('progress', 'study-progress'); sessionProgress.setAttribute('aria-label', 'Peças revisadas nesta rodada');
  const question = el('h2'); question.id = 'study-question'; question.tabIndex = -1;
  const hint = el('p', 'study-question-hint');
  const feedback = el('div', 'study-feedback'); feedback.setAttribute('role','status'); feedback.setAttribute('aria-live','polite');
  const actions = el('div','study-question-actions');
  sessionPanel.append(sessionTop, sessionProgress, question, hint, feedback, actions);
  const viewerSection = document.querySelector('.viewer-section');
  viewerSection?.insertBefore(sessionPanel, document.querySelector('#viewer'));
  if (!viewerSection) document.body.append(sessionPanel);

  function openSetup() {
    pause();
    const session = progress.session;
    const remaining = session?.queue?.length || 0;
    resumeButton.hidden = !remaining;
    resumeButton.textContent = remaining ? `Continuar · ${remaining} ${remaining === 1 ? 'restante' : 'restantes'}` : 'Continuar rodada';
    newButton.textContent = remaining ? 'Iniciar outra rodada' : 'Começar rodada';
    newButton.className = remaining ? 'button' : 'button primary';
    if (session) { mode.value = session.mode; group.value = session.group; }
    setupStatus.textContent = storageAvailable ? 'O progresso fica salvo apenas neste navegador e neste endereço local.' : 'O navegador não permitiu salvar. O progresso fica disponível enquanto esta página estiver aberta.';
    setup.showModal();
  }
  function currentPart() { return byId.get(progress.session?.queue?.[0]); }
  function start(focus = true) {
    if (!progress.session) return;
    savedView = viewer.snapshot(); active = true;
    document.body.classList.add('study-in-session'); sessionPanel.hidden = false;
    practiceButton.textContent = 'Rodada atual';
    viewer.setExamMode(true); viewer.labels(false);
    showQuestion(focus);
  }
  function restoreView() {
    viewer.setExamMode(false);
    if (savedView && typeof viewer.restore === 'function') viewer.restore(savedView);
    else if (savedView) {
      if (savedView.visibleParts) viewer.show(savedView.visibleParts); else viewer.showAll();
      if (savedView.selected && byId.has(savedView.selected)) viewer.select(savedView.selected); else viewer.clear();
      viewer.labels(Boolean(savedView.labels));
    }
    savedView = null;
  }
  function pause() {
    if (!active) return;
    save(); active = false; revealed = false; restoreView();
    document.body.classList.remove('study-in-session'); sessionPanel.hidden = true;
    practiceButton.textContent = 'Prática';
    practiceButton.focus({preventScroll:true});
  }
  function contextIds(part) {
    if (['valvas', 'papilares'].includes(part.group)) return present.filter(p => ['valvas', 'papilares'].includes(p.group)).map(p => p.id);
    return present.filter(p => p.group === part.group).map(p => p.id);
  }
  function showQuestion(focus = true) {
    revealed = false; misses = 0; actions.replaceChildren(); feedback.replaceChildren();
    feedback.className = 'study-feedback';
    const session = progress.session, part = currentPart();
    sessionProgress.max = session.total || 1; sessionProgress.value = session.done.length;
    sessionCount.textContent = `${session.done.length} de ${session.total} revisadas`;
    if (!part) { finish(); return; }
    viewer.setExamMode(true); viewer.labels(false); viewer.clear();
    viewer.show(contextIds(part));
    viewer.view(['veias'].includes(part.group) ? 'posterior' : ['valvas', 'papilares'].includes(part.group) ? 'superior' : 'anterior');
    if (session.mode === 'identify') {
      viewer.select(part.id); viewer.focus(part.id);
      question.textContent = 'Qual estrutura está destacada?';
      hint.textContent = `Observe entre ${groups[part.group]?.toLowerCase() || 'as peças'}; diga o nome antes de revelar. As demais regiões estão ocultas para permitir a inspeção.`;
      actions.append(button('Revelar resposta', 'button primary', () => reveal()), button('Isolar destaque', 'button', () => { viewer.isolate(part.id); viewer.focus(part.id); }));
    } else {
      question.textContent = `Encontre: ${part.label}`;
      hint.textContent = 'Gire o conjunto e clique na peça correspondente. Só as peças deste grupo estão visíveis; os nomes ficam ocultos durante a questão.';
      actions.append(button('Mostrar resposta', 'button', () => { viewer.select(part.id); viewer.focus(part.id); reveal('A peça correspondente está destacada.'); }));
    }
    const skip = button('Deixar para depois', 'text-button', () => {
      if (session.queue.length < 2) { feedback.textContent = 'Esta é a última peça. Revele a resposta para revisá-la ou pause a rodada.'; return; }
      session.queue.push(session.queue.shift()); save(); showQuestion();
    });
    actions.append(skip);
    if (focus) question.focus({ preventScroll: true });
  }
  function reveal(message = '') {
    if (!active || !currentPart()) return;
    revealed = true; const part = currentPart();
    feedback.replaceChildren(); feedback.className = 'study-feedback is-revealed';
    if (message) feedback.append(el('p', 'study-answer-status', message));
    feedback.append(el('h3', '', part.label), el('p', '', part.note || 'Observe a forma e a relação com as peças próximas.'));
    const origin = `${part.source || 'Acervo anatômico'} · ${part.sourceName || part.label}`;
    const reference = part.requirement ? `${part.requirement.source === 'roteiro' ? 'Roteiro' : system === 'respiratory' ? 'Slides de respiratório' : 'Slides de coração'}, p. ${part.requirement.page} · item ${part.requirement.id}` : 'Peça complementar do acervo; sem item individual associado no roteiro.';
    feedback.append(el('p', 'study-answer-reference', `${reference} — Fonte 3D: ${origin}`));
    actions.replaceChildren(
      button('Identifiquei com segurança', 'button primary', () => rate('known')),
      button('Preciso revisar', 'button', () => rate('review')),
      button('Ver isolada', 'text-button', () => { viewer.isolate(part.id); viewer.focus(part.id); })
    );
    actions.querySelector('button')?.focus({preventScroll:true});
  }
  function rate(rating) {
    if (!active || !revealed) return;
    const part = currentPart(); if (!part) return;
    progress.ratings[part.id] = { rating, at: Date.now(), attempts: (progress.ratings[part.id]?.attempts || 0) + 1 };
    progress.session.done.push(progress.session.queue.shift()); save(); showQuestion();
  }
  function finish() {
    viewer.setExamMode(false);
    if(savedView) viewer.restore(savedView);
    question.textContent = 'Rodada concluída';
    hint.textContent = 'Você percorreu todas as peças desta rodada. Revise as que ainda precisam de atenção e depois retome o roteiro completo.';
    const reviewIds = progress.session.done.filter(id => progress.ratings[id]?.rating === 'review');
    feedback.textContent = `${progress.session.done.length} peças revisadas · ${reviewIds.length} marcadas para rever. Esta contagem não inclui estruturas ausentes do modelo.`;
    if (reviewIds.length) actions.append(button(`Rever ${reviewIds.length} ${reviewIds.length === 1 ? 'peça' : 'peças'}`, 'button primary', () => {
      progress.session.queue = shuffle(reviewIds); progress.session.done = []; progress.session.total = reviewIds.length;
      save(); showQuestion();
    }));
    actions.append(button('Nova rodada', 'button', () => openSetup()), button('Voltar a explorar', 'text-button', () => pause()));
    question.focus({ preventScroll: true });
  }
  const unsubscribePick = viewer.onPick(picked => {
    if (!active || revealed || progress.session?.mode !== 'find' || !currentPart()) return;
    const id = typeof picked === 'string' ? picked : picked?.id;
    if (!id || !byId.has(id)) return;
    if (id === currentPart().id) { viewer.select(id); reveal(misses ? 'Você encontrou. Revise a relação que ajudou a reconhecer a peça.' : 'Você encontrou a peça correspondente.'); }
    else { misses++; feedback.textContent = 'Ainda não é essa peça. Observe a posição e as conexões; você pode girar o conjunto e tentar novamente.'; }
  });
  const onEscape = event => {
    if (event.key === 'Escape' && active && !document.querySelector('dialog[open]')) { event.preventDefault(); pause(); practiceButton.focus(); }
  };
  document.addEventListener('keydown', onEscape);

  // Association to an available mesh is deliberately distinct from anatomy validation.
  const rows = requirements.map(item => {
    const direct = present.filter(p => String(p.requirement?.id) === String(item.id) || (p.requirementIds || []).map(String).includes(String(item.id)));
    const evidence = new Set(Array.isArray(item.z_evidencia) ? item.z_evidencia : []);
    const related = present.filter(p => ((p.relatedRequirementIds || []).map(String).includes(String(item.id)) || [p.sourceName, ...(Array.isArray(p.sourceAliases) ? p.sourceAliases : [])].some(name => evidence.has(name))) && !direct.includes(p));
    const hasWholeAssociation = direct.some(p => p.correspondence !== 'partial');
    return { item, direct, related, status: hasWholeAssociation ? 'present' : direct.length || related.length ? 'related' : 'pending' };
  });
  const route = makeDialog('study-route', 'Seu roteiro, estrutura por estrutura', 'MAPA DA PRÁTICA');
  route.classList.add('study-route-dialog');
  if(scopeNote)route.append(el('p','study-boundary',scopeNote));
  route.append(el('p', 'study-intro', 'Encontre cada alvo do roteiro e dos slides. Uma peça associada permite explorar o modelo, mas não confirma todos os detalhes exigidos. As pendências continuam visíveis aqui.'));
  const metrics = el('div', 'study-route-metrics');
  for (const [status,label] of [['present','com peça associada'],['related','com contexto parcial'],['pending','pendentes na cena']]) {
    const metric = el('div', `study-metric ${status}`);
    metric.append(el('strong','', rows.filter(r => r.status === status).length), el('span','',label)); metrics.append(metric);
  }
  route.append(metrics);
  const routeFilters = el('div', 'study-route-filters');
  const searchLabel = el('label', 'study-field', 'Buscar no roteiro');
  const search = el('input'); search.type = 'search'; search.placeholder = 'Estrutura, item ou grupo…'; search.id = 'study-route-search'; searchLabel.htmlFor = search.id; searchLabel.append(search);
  search.setAttribute('aria-label','Buscar no roteiro');
  const statusLabel = el('label','study-field','Situação nesta cena');
  const statusFilter = el('select'); statusFilter.id = 'study-route-status'; statusLabel.htmlFor = statusFilter.id;
  statusFilter.setAttribute('aria-label','Situação nesta cena');
  for (const [value,text] of [['all','Todas'],['present','Com peça associada'],['related','Contexto parcial'],['pending','Pendentes na cena']]) {
    const option = el('option','',text); option.value=value; statusFilter.append(option);
  }
  statusLabel.append(statusFilter);
  const sourceLabel = el('label','study-field','Material'); const sourceFilter = el('select'); sourceFilter.id = 'study-route-source'; sourceLabel.htmlFor = sourceFilter.id;
  sourceFilter.setAttribute('aria-label','Material');
  for (const [value,text] of [['all','Roteiro e slides'],['principal',system==='respiratory'?'Slides da professora':'Roteiro prático'],['complemento_docente','Complementos dos slides'],['complementar','Material complementar']]) {
    const option = el('option','',text); option.value=value; sourceFilter.append(option);
  }
  sourceLabel.append(sourceFilter); routeFilters.append(searchLabel,statusLabel,sourceLabel); route.append(routeFilters);
  const routeCount = el('p','study-route-count'); routeCount.setAttribute('role','status');
  const routeList = el('div','study-route-list'); route.append(routeCount,routeList);
  const normal = text => String(text || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const sourceText = item => `${({roteiro:'Roteiro',coracao:'Slides de coração',respiratorio:'Slides de respiratório',complementar:'Roteiro complementar',roteiro_complementar:'Roteiro complementar',vasos:'Slides de vasos'})[item.fonte] || 'Material de apoio'}${item.pagina ? ' · p. '+item.pagina : ''} · item ${item.id}`;
  const evidenceSource = id => evidenceSources.get(id) || ({roteiro:'Roteiro',coracao:'Slides de coração',vasos:'Slides de vasos',C1:'Aula C1',C2:'Aula C2',C3:'Aula C3'}[id]) || 'Material de aula';
  function materialLink(ref){
    let href=null;
    if(['roteiro','coracao','vasos','respiratorio','linfatico','mediastino'].includes(ref.source))href=`classroom.html?doc=${ref.source}&page=${Number(ref.page)||1}`;
    else if(/^[CR][1-4]$/.test(ref.source)){const time=String(ref.time||'').match(/\d{1,2}:\d{2}(?::\d{2})?/);const seconds=time?time[0].split(':').reduce((n,v)=>n*60+Number(v),0):0;href=`classroom.html?video=${ref.source}&t=${seconds}`;}
    if(!href)return null;
    const link=el('a','button',`${evidenceSource(ref.source)}${ref.page?' · p. '+ref.page:''}${ref.time?' · '+ref.time:''} ↗`);link.href=href;link.target='_blank';link.rel='noopener';return link;
  }
  function appendEvidence(body, id) {
    const academic = evidenceTargets.get(String(id));
    if (!academic) return;
    const block = el('section','study-evidence');
    if (academic.criterion) {
      block.append(el('h4','study-evidence-heading','O que conferir na prática'), el('p','study-evidence-criterion',academic.criterion));
    }
    const pages = Array.isArray(academic.pages) ? academic.pages : [];
    const lecture = Array.isArray(academic.lecture) ? academic.lecture : [];
    const visuals = Array.isArray(academic.visuals) ? academic.visuals : [];
    const readingNotes = Array.isArray(academic.readingNotes) ? academic.readingNotes : [];
    const references = el('details','study-evidence-details');
    const referenceSummary = el('summary','','Materiais que sustentam este alvo'); references.append(referenceSummary);
    const contents = el('div','study-evidence-contents');
    const sourceLinks=el('div','study-route-links');const seen=new Set();
    for(const ref of [...pages,...lecture]){const link=materialLink(ref);if(link&&!seen.has(link.href)){seen.add(link.href);sourceLinks.append(link);}}
    if(sourceLinks.children.length)contents.append(sourceLinks);
    if (academic.scopeSource) {
      const ref = academic.scopeSource;
      contents.append(el('p','study-evidence-scope',`Exigência: ${evidenceSource(ref.source)}${ref.page ? ` · p. ${ref.page}` : ''}.`));
    }
    if (pages.length) {
      const pageGroups = new Map();
      for (const ref of pages) {
        if (!ref.source || !ref.page) continue;
        if (!pageGroups.has(ref.source)) pageGroups.set(ref.source,new Set());
        pageGroups.get(ref.source).add(ref.page);
      }
      const pageText = [...pageGroups].map(([source, numbers]) => `${evidenceSource(source)} · p. ${[...numbers].join(', ')}`).join(' / ');
      contents.append(el('p','study-evidence-pages',`Páginas relacionadas: ${pageText}.`));
    }
    if (visuals.length) {
      contents.append(el('h5','study-evidence-subheading','Figuras e quadros inspecionados'));
      for (const visual of visuals) {
        const card = el('div','study-evidence-card visual');
        const place = [evidenceSource(visual.source), visual.page ? `p. ${visual.page}` : '', visual.time || ''].filter(Boolean).join(' · ');
        card.append(el('span','study-evidence-label',visual.kind === 'frame' ? 'Quadro de aula' : 'Figura do material'),el('strong','',place),el('p','',visual.summary));
        contents.append(card);
      }
      contents.append(el('p','study-evidence-limit', evidence?.limits?.visual || 'A conferência da figura não valida a geometria do modelo 3D.'));
    }
    if (lecture.length) {
      contents.append(el('h5','study-evidence-subheading','Localização nas aulas'));
      const relations = {
        mencao_individual_em_asr_e_material_docente:'Menção identificada',
        relacao_de_fluxo_grupo:'Relação de fluxo · menção coletiva',
        relacao_anatomica_citada:'Relação anatômica citada',
        variacao_didatica:'Variação discutida',
        conflito_localizado_resolvido_pelo_slide_e_referencia:'Divergência entre transcrição e figura'
      };
      for (const segment of lecture) {
        const card = el('div','study-evidence-card asr');
        const status = segment.audioReviewed === true ? 'Transcrição · áudio conferido' : 'Transcrição automática · áudio não reescutado';
        card.append(el('span','study-evidence-label',status),el('strong','',`${evidenceSource(segment.source)}${segment.time ? ` · cerca de ${segment.time}` : ''}`));
        card.append(el('p','study-evidence-relation',relations[segment.relation] || 'Apoio localizado na transcrição'));
        card.append(el('p','',`Síntese do trecho: ${segment.summary}`)); contents.append(card);
      }
      contents.append(el('p','study-evidence-limit', evidence?.limits?.lecture || 'Horários aproximados e termos sujeitos a erro de transcrição.'));
    } else contents.append(el('p','study-evidence-limit','Sem trecho localizado nas transcrições consultadas. Isso não retira o alvo do roteiro.'));
    for (const note of readingNotes) {
      const card = el('p','study-evidence-reading-note');
      card.append(el('strong','',`${note.id} · Nota de leitura: `), document.createTextNode(note.text)); contents.append(card);
    }
    references.append(contents); block.append(references); body.append(block);
  }
  function renderRoute() {
    routeList.replaceChildren();
    const term = normal(search.value);
    const shown = rows.filter(({item,status}) => (statusFilter.value === 'all' || status === statusFilter.value) && (sourceFilter.value === 'all' || item.escopo === sourceFilter.value) && normal(`${item.id} ${item.estrutura} ${item.grupo}`).includes(term));
    routeCount.textContent = `${shown.length} de ${rows.length} alvos · a situação se refere à cena carregada`;
    let lastGroup = '';
    for (const row of shown) {
      const {item,direct,related,status} = row;
      if (item.grupo !== lastGroup) { routeList.append(el('h3','study-route-group',item.grupo)); lastGroup=item.grupo; }
      const details = el('details',`study-route-item ${status}`);
      const summary = el('summary');
      const text = el('span','study-route-title'); text.append(el('strong','',item.estrutura),el('small','',sourceText(item)));
      const tag = el('span',`study-status ${status}`,status === 'present' ? 'Peça associada' : status === 'related' ? 'Contexto parcial' : 'Pendente');
      summary.append(text,tag); details.append(summary);
      const body = el('div','study-route-body');
      body.append(el('p','',status === 'present' ? 'Há uma peça com associação a este item. Confira sua forma, posição e os limites descritos antes de considerar o alvo estudado.' : status === 'related' && direct.length ? 'A peça associada representa apenas parte do alvo ou tem equivalência ainda em revisão. Ela não demonstra o requisito completo.' : status === 'related' ? 'Há peças relacionadas na cena, mas este detalhe não está individualizado nem confirmado em 3D.' : 'Não há peça associada a este alvo na cena atual. Ele continua necessário para o estudo e não entra no treino de identificação.'));
      for (const part of direct) if (part.note) body.append(el('p','',`${part.label}: ${part.note}`));
      if (item.observacao) body.append(el('p','',`Observação da auditoria dos acervos: ${item.observacao}`));
      const candidates = direct.length ? direct : related;
      if (candidates.length) {
        const buttons = el('div','study-route-links');
        for (const part of candidates) buttons.append(button(`${status === 'present' ? 'Explorar' : 'Ver contexto'}: ${part.label}`,'button',() => {
          route.close(); pause(); viewer.setExamMode(false);
          if(part.group.startsWith('contexto') && viewer.showContext) viewer.showContext();
          else if(viewer.showHeart) viewer.showHeart();
          else viewer.show(present.filter(p=>p.defaultVisible !== false).map(p=>p.id));
          viewer.select(part.id); viewer.focus(part.id);
          document.querySelector('#heart-canvas')?.focus({preventScroll:true});
        }));
        body.append(buttons);
      }
      const audit = {geometria_disponivel:'geometria encontrada no acervo',parcial_ou_a_conferir:'parcial ou a conferir no acervo',nao_localizado:'geometria não localizada no acervo'}[item.status] || item.status;
      body.append(el('p','study-answer-reference',`Auditoria dos acervos: ${audit}. Validação anatômica individual: ${item.validacao_visual === 'nao_concluida_individualmente' ? 'ainda não concluída' : item.validacao_visual || 'a conferir'}.`));
      appendEvidence(body, item.id);
      details.append(body); routeList.append(details);
    }
    if (!shown.length) routeList.append(el('p','study-route-empty','Nenhum alvo corresponde a estes filtros. Tente outra palavra ou selecione “Todas”.'));
  }
  search.addEventListener('input',renderRoute); statusFilter.addEventListener('change',renderRoute); sourceFilter.addEventListener('change',renderRoute);
  const diagnostics = Object.freeze({
    snapshot: () => ({ active, mode: progress.session?.mode || null, remaining: progress.session?.queue.length || 0, reviewed: progress.session?.done.length || 0, total: progress.session?.total || 0, revealed, storageAvailable, loadedParts:present.length, eligibleParts:eligible.length, cardiacEligibleParts:cardiacEligible.length, contextEligibleParts:eligible.filter(p=>p.group==='contexto').length, requirementCount:rows.length, evidenceTargets:evidenceTargets.size, route: {present:rows.filter(r=>r.status==='present').length,related:rows.filter(r=>r.status==='related').length,pending:rows.filter(r=>r.status==='pending').length} }),
    openPractice: openSetup,
    openRoute: () => {pause(); renderRoute(); route.showModal();},
    destroy: () => { pause(); unsubscribePick?.(); document.removeEventListener('keydown',onEscape); toolbar.remove(); setup.remove(); route.remove(); sessionPanel.remove(); css.remove(); }
  });
  window.heartStudy = diagnostics;
  return diagnostics;
}
