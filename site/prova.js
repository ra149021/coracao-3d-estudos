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
const params = new URLSearchParams(location.search);
$('topic-toggle').addEventListener('click', () => {
  const open = $('topic-toggle').getAttribute('aria-expanded') !== 'true';
  $('topic-toggle').setAttribute('aria-expanded', String(open));
});
let guide, theories, current, questionIndex = 0;
const storageKey = 'atlas:exam-path:v1';
let answers = {};
const pendingAnswers = {};
const record = value => value && typeof value === 'object' && !Array.isArray(value);
const sessionWarning = 'Armazenamento indisponível: registros somente nesta sessão; recarregar ou fechar perde alterações não salvas';
try {
  const stored = JSON.parse(localStorage.getItem(storageKey) ?? '{}');
  if (!record(stored)) throw new Error('Invalid answer record');
  answers = Object.fromEntries(Object.entries(stored).filter(([, value]) => ['known', 'review'].includes(value)));
} catch { $('save-status').textContent = sessionWarning; }
const answerKey = ([system, id]) => `${system}:${id}`;

function recordAnswer(ref, rating) {
  answers[answerKey(ref)] = rating;
  pendingAnswers[answerKey(ref)] = rating;
  try {
    // Do not replace unreadable storage or replay the entire stale answer map.
    const stored = JSON.parse(localStorage.getItem(storageKey) ?? '{}');
    if (!record(stored)) throw new Error('Invalid answer record');
    const merged = {...stored, ...pendingAnswers};
    localStorage.setItem(storageKey, JSON.stringify(merged));
    answers = Object.fromEntries(Object.entries(merged).filter(([, value]) => ['known', 'review'].includes(value)));
    for (const id of Object.keys(pendingAnswers)) delete pendingAnswers[id];
    $('save-status').textContent = 'Autoavaliação salva neste navegador';
  } catch {
    $('save-status').textContent = sessionWarning;
  }
  renderNavigation();
  updateTopicProgress();
}

function updateTopicProgress() {
  const count = current.questions.filter(ref => answers[answerKey(ref)]).length;
  $('topic-progress').textContent = `${count} de ${current.questions.length} perguntas autoavaliadas neste tema. Isso não comprova domínio.`;
}

function renderQuestion() {
  const holder = $('topic-question');
  holder.replaceChildren(el('h3', '', 'Agora explique sem consultar'));
  const ref = current.questions[questionIndex];
  const [system, id] = ref;
  const question = theories[system].chapters.flatMap(chapter => chapter.recall || []).find(q => q.id === id);
  holder.append(el('p', 'question-counter', `Pergunta ${questionIndex + 1} de ${current.questions.length} · revisão original do atlas`));
  const title = el('h4', 'question-heading', question.question);
  title.id = 'question-title';
  holder.append(title);
  const label = el('label', '', 'Explique em voz alta ou escreva um rascunho (não é salvo)');
  label.htmlFor = 'question-draft';
  const draft = el('textarea');
  draft.id = 'question-draft';
  holder.append(label, draft);
  const actions = el('div', 'question-actions');
  actions.append(button('Conferir resposta', () => {
    const answer = el('section', 'answer-box');
    answer.id = 'question-answer';
    answer.append(el('strong', '', 'Resposta'), el('p', '', question.answer));
    if (question.explanation) answer.append(el('strong', '', 'Por quê?'), el('p', '', question.explanation));
    const sourceLabels = (question.references || []).map(reference => {
      const source = theories[system].sources.find(source => source.id === reference.source);
      return `${source?.label || reference.source}${reference.page ? ' · p. ' + reference.page : ''}${reference.time ? ' · ' + reference.time : ''}`;
    });
    if (sourceLabels.length) answer.append(el('p', 'answer-sources', 'Confira na unidade de teoria: ' + sourceLabels.join('; ')));
    actions.before(answer);
    draft.readOnly = true;
    actions.replaceChildren(
      button('Consegui explicar', () => recordAnswer(ref, 'known'), 'action primary'),
      button('Preciso rever', () => recordAnswer(ref, 'review')),
      button(questionIndex === current.questions.length - 1 ? 'Recomeçar perguntas' : 'Próxima pergunta', () => {
        questionIndex = (questionIndex + 1) % current.questions.length;
        renderQuestion();
        $('question-title').tabIndex = -1;
        $('question-title').focus();
      })
    );
    actions.querySelector('button').focus({preventScroll: true});
  }, 'action primary'));
  holder.append(actions, el('p', 'inline-note', 'Compare seu raciocínio com a explicação. Os botões registram sua percepção; não corrigem automaticamente o rascunho.'));
}


function renderNavigation() {
  $('path-list').replaceChildren();
  guide.topics.forEach((topic, index) => {
    const item = button('', () => selectTopic(topic.id, true), '');
    item.append(el('span', 'step-number', String(index + 1).padStart(2, '0')), el('span', '', topic.title));
    if (topic.id === current.id) item.setAttribute('aria-current', 'step');
    $('path-list').append(item);
  });
  const refs = [...new Map(guide.topics.flatMap(topic => topic.questions).map(ref => [answerKey(ref), ref])).values()];
  const rated = refs.filter(ref => answers[answerKey(ref)]).length;
  const review = refs.filter(ref => answers[answerKey(ref)] === 'review').length;
  $('path-progress').textContent = `${rated} de ${refs.length} perguntas autoavaliadas · ${review} para retomar. ${guide.topics.length} temas; complementos dependem do roteiro.`;
}

function selectTopic(id, focus = false) {
  current = guide.topics.find(topic => topic.id === id) || guide.topics[0];
  const article = $('topic');
  article.replaceChildren(el('span', 'overline', current.group));
  const heading = el('h2', '', current.title);
  heading.id = 'topic-title';
  heading.tabIndex = -1;
  article.append(heading, el('p', '', current.why));
  const diagram = el('figure', 'pathway');
  diagram.append(el('figcaption', '', current.flowLabel));
  const steps = el('ol');
  current.flow.forEach(step => steps.append(el('li', '', step)));
  diagram.append(steps);
  article.append(diagram, el('h3', '', 'O que você precisa conseguir explicar'));
  const targets = el('ul');
  current.targets.forEach(target => targets.append(el('li', '', target)));
  const pitfall = el('p', 'pitfall');
  pitfall.append(el('strong', '', 'Não confunda'), document.createTextNode(current.pitfall));
  article.append(targets, pitfall, el('h3', '', 'Volte ao ponto certo da teoria'));
  const links = el('div', 'topic-links');
  links.id = 'topic-links';
  current.chapters.forEach(([system, id]) => {
    const chapter = theories[system].chapters.find(chapter => chapter.id === id);
    const a = el('a', 'action', chapter.title);
    a.href = `theory.html?system=${system}&chapter=${encodeURIComponent(id)}`;
    links.append(a);
  });
  article.append(links);
  const topicProgress = el('p', 'inline-note');
  topicProgress.id = 'topic-progress';
  topicProgress.setAttribute('role', 'status');
  const questionBox = el('section', 'topic-question');
  questionBox.id = 'topic-question';
  article.append(topicProgress, questionBox);
  questionIndex = 0;
  updateTopicProgress();
  renderQuestion();
  const bottom = el('div', 'topic-bottom');
  const index = guide.topics.indexOf(current);
  if (index > 0) bottom.append(button('← Tema anterior', () => selectTopic(guide.topics[index - 1].id, true)));
  if (index < guide.topics.length - 1) bottom.append(button('Próximo tema →', () => selectTopic(guide.topics[index + 1].id, true)));
  article.append(bottom);
  renderNavigation();
  const url = new URL(location.href);
  url.searchParams.set('topic', current.id);
  history.replaceState(null, '', url);
  if (focus) {
    $('topic-toggle').setAttribute('aria-expanded', 'false');
    heading.focus();
  }
}

try {
  const urls = ['assets/exam-path.json', 'assets/circulatory-theory.json', 'assets/respiratory/theory.json'];
  const values = await Promise.all(urls.map(async url => {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Um arquivo de estudo não pôde ser carregado. Tente recarregar a página.');
    return response.json();
  }));
  guide = values[0];
  theories = {circulatory: values[1], respiratory: values[2]};
  if (!guide.topics?.length) throw new Error('O percurso não contém temas nesta instalação.');
  $('scope-note').textContent = guide.scope;
  selectTopic(params.get('topic'));
} catch (error) {
  $('topic').replaceChildren(el('h2', '', 'Percurso indisponível'), el('p', '', error.message));
  $('path-progress').textContent = 'Conteúdo não carregado';
  $('scope-note').textContent = 'Este percurso é um apoio de estudo, não confirmação do programa da prova.';
}
