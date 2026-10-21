const $ = id => document.getElementById(id);
const el = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
};
const button = (text, handler, cls = 'action') => {
  const node = el('button', cls, text);
  node.type = 'button';
  node.addEventListener('click', handler);
  return node;
};
let library, theories, current;
const params=new URLSearchParams(location.search);
let chapterFilter=params.get('chapter')||'';
const storageKey = 'atlas:applied-cases:v1';
let records = {};
try {
  const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
  if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
    records = Object.fromEntries(Object.entries(saved).filter(([, value]) => value && typeof value === 'object' && typeof value.draft === 'string').map(([id, value]) => [id, {draft: value.draft, rating: ['known', 'review'].includes(value.rating) ? value.rating : null}]));
  }
} catch { /* Study still works with blocked or corrupt storage. */ }
function saveRecord(id, changes) {
  records[id] = {...(records[id] || {draft: '', rating: null}), ...changes};
  try {
    localStorage.setItem(storageKey, JSON.stringify(records));
    $('case-save-status').textContent = 'Rascunhos e autoavaliação salvos neste navegador; sem envio a servidor';
  } catch {
    $('case-save-status').textContent = 'Armazenamento indisponível: rascunhos somente nesta sessão';
  }
  navigation();
}
const filteredCases = () => library.cases.filter(item => ($('case-system').value === 'all' || item.system === $('case-system').value) && (!chapterFilter || item.chapterId===chapterFilter));

function navigation() {
  const cases = filteredCases();
  $('case-list').replaceChildren();
  cases.forEach(item => {
    const node = button(item.title, () => selectCase(item.id, true), '');
    if (item.id === current?.id) node.setAttribute('aria-current', 'page');
    $('case-list').append(node);
  });
  const rated = cases.filter(item => records[item.id]?.rating).length;
  const review = cases.filter(item => records[item.id]?.rating === 'review').length;
  $('case-progress').textContent = `${rated} de ${cases.length} casos autoavaliados · ${review} para retomar. O rascunho não recebe correção automática.`;
}

function references(items, system) {
  const box = el('div', 'source-links');
  for (const ref of items) {
    const source = theories[system].sources.find(item => item.id === ref.source);
    const label = `${source?.label || ref.source}${ref.page ? ' · p. ' + ref.page : ''}`;
    if (['coracao', 'vasos', 'linfatico', 'respiratorio', 'roteiro'].includes(ref.source)) {
      const link = el('a', '', label);
      link.href = `classroom.html?doc=${ref.source}&page=${ref.page || 1}`;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      box.append(link);
    } else if (source?.url?.startsWith('https://')) {
      const link = el('a', '', label);
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      box.append(link);
    } else box.append(el('span', '', label));
  }
  return box;
}

function selectCase(id, focus = false) {
  const cases = filteredCases();
  current = cases.find(item => item.id === id) || cases[0];
  const content = $('case-content');
  content.replaceChildren();
  if (!current) {
    content.append(el('p', 'empty-state', 'Nenhum caso disponível para esta unidade. Há 6 casos na base completa; escolha outro sistema ou mostre todos os casos.'));
    const url=new URL(location.href);url.searchParams.delete('case');url.searchParams.set('system',$('case-system').value);if(chapterFilter)url.searchParams.set('chapter',chapterFilter);else url.searchParams.delete('chapter');history.replaceState(null,'',url);
    navigation();
    return;
  }
  const item = current;
  content.append(el('span', 'overline', item.system === 'circulatory' ? 'CIRCULATÓRIO' : 'RESPIRATÓRIO'));
  const title = el('h2', '', item.title);
  title.id = 'case-title';
  title.tabIndex = -1;
  const scenario = el('p', '', item.scenario);
  scenario.id = 'case-scenario';
  content.append(title, scenario, el('h3', '', item.question));
  const chapter = theories[item.system].chapters.find(c => c.id === item.chapterId);
  const link = el('a', 'action', 'Estudar a base: ' + chapter.title);
  link.href = `theory.html?system=${item.system}&chapter=${encodeURIComponent(item.chapterId)}`;
  content.append(link);
  const label = el('label', 'case-draft-label', 'Explique em voz alta ou escreva seu raciocínio');
  label.htmlFor = 'case-draft';
  const draft = el('textarea');
  draft.id = 'case-draft';
  draft.value = records[item.id]?.draft || '';
  draft.addEventListener('input', () => saveRecord(item.id, {draft: draft.value}));
  content.append(label, draft);
  const actions = el('div', 'case-actions');
  actions.append(button('Conferir raciocínio', () => {
    const answer = el('section');
    answer.id = 'case-answer';
    answer.append(el('h3', '', 'Resposta e mecanismo'), el('p', '', item.answer), el('p', '', item.explanation), el('h3', '', 'Confira os pontos essenciais'));
    const rubric = el('ul');
    item.checkpoints.forEach(point => rubric.append(el('li', '', point)));
    answer.append(rubric, references(item.references, item.system));
    actions.before(answer);
    actions.replaceChildren(
      button('Consegui justificar os pontos', () => saveRecord(item.id, {rating: 'known'}), 'action primary'),
      button('Preciso retomar este caso', () => saveRecord(item.id, {rating: 'review'})),
      button('Próximo caso', () => selectCase(cases[(cases.indexOf(item) + 1) % cases.length].id, true))
    );
    actions.querySelector('button').focus({preventScroll: true});
  }, 'action primary'));
  content.append(actions, el('p', 'case-status', 'Os casos são exercícios originais de anatomia. Não são gabaritos de provas recuperadas nem orientação de diagnóstico ou procedimento.'));
  const url = new URL(location.href);
  url.searchParams.set('case', item.id);
  url.searchParams.set('system',$('case-system').value);
  if(chapterFilter)url.searchParams.set('chapter',chapterFilter);else url.searchParams.delete('chapter');
  $('back-exercises').href=`exercises.html?system=${item.system}${chapterFilter?'&chapter='+encodeURIComponent(chapterFilter):''}`;
  history.replaceState(null, '', url);
  navigation();
  if (focus) title.focus();
}

$('case-system').addEventListener('change', () => {chapterFilter='';selectCase(null);});
$('case-all').addEventListener('click',()=>{chapterFilter='';$('case-system').value='all';selectCase(null);});
try {
  const urls = ['assets/study-cases.json', 'assets/circulatory-theory.json', 'assets/respiratory/theory.json'];
  const [cases, circulatory, respiratory] = await Promise.all(urls.map(async url => {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Não foi possível carregar os casos ou suas referências. Tente recarregar a página.');
    return response.json();
  }));
  library = cases;
  theories = {circulatory, respiratory};
  if (!library.cases?.length) throw new Error('Nenhum caso disponível nesta instalação.');
  $('case-notice').textContent = library.notice;
  if(['circulatory','respiratory'].includes(params.get('system')))$('case-system').value=params.get('system');
  selectCase(new URLSearchParams(location.search).get('case'));
} catch (error) {
  $('case-content').replaceChildren(el('h2', '', 'Treino indisponível'), el('p', '', error.message));
  $('case-progress').textContent = 'Conteúdo não carregado';
  $('case-notice').textContent = 'Os exercícios dependem das fontes de estudo instaladas.';
  $('case-system').disabled = true;
}
