const $ = id => document.getElementById(id);
const state = { models: [], selected: null, loaded: null, reminder: null };

function httpsURL(value) {
  const url = new URL(value);
  if (url.protocol !== 'https:') throw new Error('A fonte deve usar HTTPS.');
  return url.href;
}

function validateModel(model) {
  if (!model.id || !model.title || !/^[a-f0-9]{32}$/.test(model.sketchfabId)) throw new Error('Referência inválida.');
  const embed = new URL(model.embedUrl);
  if (embed.origin !== 'https://sketchfab.com' || embed.pathname !== `/models/${model.sketchfabId}/embed`) throw new Error('Incorporação não oficial.');
  for (const key of ['url', 'authorUrl', 'institutionUrl']) httpsURL(model[key]);
  if (!Array.isArray(model.limits) || !Array.isArray(model.observations)) throw new Error('Orientações indisponíveis.');
  return model;
}

function externalLink(id, href, text) {
  const link = $(id);
  link.href = httpsURL(href);
  if (text !== undefined) link.textContent = text;
}

function classroomLink(reference) {
  const params = new URLSearchParams({ doc: reference.source, page: String(reference.page) });
  const link = document.createElement('a');
  link.href = `classroom.html?${params}`;
  link.textContent = reference.label || `Slide ${reference.page}`;
  return link;
}

function clearPlayer() {
  if (state.reminder !== null) clearTimeout(state.reminder);
  state.reminder = null;
  state.loaded = null;
  $('embed-host').replaceChildren();
  $('player-placeholder').hidden = false;
  $('stop-model').hidden = true;
  $('load-model').disabled = false;
  $('embed-help').textContent = 'Se a peça não aparecer, use “Abrir na fonte”. Ao trocar de peça, a visualização anterior é encerrada.';
}

function stopPlayer() {
  clearPlayer();
  $('player-status').textContent = 'Visualização encerrada. Você pode carregar a peça novamente.';
}

function renderObservations(model) {
  const list = $('observation-list');
  list.replaceChildren();
  for (const observation of model.observations) {
    const item = document.createElement('li');
    const title = document.createElement('h3');
    title.textContent = observation.title;
    const paragraph = document.createElement('p');
    paragraph.textContent = observation.text;
    item.append(title, paragraph);
    if (observation.references?.length) {
      const links = document.createElement('div');
      links.className = 'observation-sources';
      for (const reference of observation.references) links.append(classroomLink(reference));
      item.append(links);
    }
    if (observation.requirementIds?.length) {
      const scope = document.createElement('span');
      scope.className = 'requirement-note';
      scope.textContent = `Comparar com os itens ${observation.requirementIds.join(', ')} do roteiro.`;
      item.append(scope);
    }
    list.append(item);
  }
  $('model-limits').replaceChildren();
  for (const limit of model.limits) {
    const item = document.createElement('li');
    item.textContent = limit;
    $('model-limits').append(item);
  }
}

function selectModel(model, updateURL = true) {
  clearPlayer();
  state.selected = model;
  for (const button of $('specimen-list').querySelectorAll('button')) button.setAttribute('aria-pressed', String(button.dataset.model === model.id));
  $('model-title').textContent = model.title;
  $('model-kicker').textContent = `${model.code} / PEÇA HUMANA`;
  $('placeholder-code').textContent = `${model.code} · Visible Heart Laboratories`;
  $('model-description').textContent = model.description;
  $('specimen-description').textContent = model.specimen;
  $('license-label').textContent = model.license;
  externalLink('open-source', model.url);
  externalLink('license-source', model.url);
  externalLink('institution-link', model.institutionUrl, model.institution);
  externalLink('author-link', model.authorUrl, model.author);
  $('player-status').textContent = 'Peça selecionada. O visualizador aguarda seu clique.';
  renderObservations(model);
  if (updateURL) {
    const url = new URL(location.href);
    url.searchParams.set('model', model.id);
    history.replaceState(null, '', url);
  }
}

function loadModel() {
  const model = state.selected;
  if (!model || state.loaded) return;
  const url = new URL(model.embedUrl);
  url.searchParams.set('autostart', '1');
  const frame = document.createElement('iframe');
  frame.title = `${model.title} — visualizador oficial de ${model.author}`;
  frame.allow = 'autoplay; fullscreen; xr-spatial-tracking';
  frame.allowFullscreen = true;
  frame.referrerPolicy = 'strict-origin-when-cross-origin';
  frame.addEventListener('load', () => {
    if (state.loaded !== model.id || !frame.isConnected) return;
    $('player-status').textContent = 'Página do visualizador aberta. Aguarde a peça; se houver um aviso de erro, use “Abrir na fonte”.';
  });
  frame.addEventListener('error', () => {
    if (state.loaded !== model.id) return;
    $('player-status').textContent = 'O visualizador não pôde ser aberto. Tente “Abrir na fonte”.';
  });
  state.loaded = model.id;
  $('load-model').disabled = true;
  $('player-placeholder').hidden = true;
  $('stop-model').hidden = false;
  $('player-status').textContent = 'Abrindo o visualizador oficial…';
  frame.src = url.href;
  $('embed-host').replaceChildren(frame);
  $('stop-model').focus({ preventScroll: true });
  state.reminder = setTimeout(() => {
    if (state.loaded === model.id && frame.isConnected) $('embed-help').textContent = 'O carregamento depende da conexão e do Sketchfab. Se a peça não aparecer, use “Abrir na fonte”. Trocar de peça encerra a visualização anterior.';
  }, 15000);
}

function renderChoices(models) {
  $('specimen-list').replaceChildren();
  for (const model of models) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'specimen-choice';
    button.dataset.model = model.id;
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-controls', 'specimen-workspace');
    const top = document.createElement('span');
    top.className = 'choice-top';
    const code = document.createElement('span');
    code.textContent = model.code;
    const selected = document.createElement('span');
    selected.className = 'choice-state';
    selected.setAttribute('aria-hidden', 'true');
    selected.textContent = '✓';
    top.append(code, selected);
    const title = document.createElement('span');
    title.className = 'choice-title';
    title.textContent = model.shortTitle;
    const focus = document.createElement('span');
    focus.className = 'choice-focus';
    focus.textContent = model.focus.join(' · ');
    button.append(top, title, focus);
    button.addEventListener('click', () => selectModel(model));
    $('specimen-list').append(button);
  }
}

$('load-model').addEventListener('click', loadModel);
$('stop-model').addEventListener('click', () => { stopPlayer(); $('load-model').focus({ preventScroll: true }); });
window.addEventListener('pagehide', stopPlayer);

async function initialize() {
  try {
    const response = await fetch('assets/specimens.json');
    if (!response.ok) throw new Error('Acervo indisponível.');
    const data = await response.json();
    if (!Array.isArray(data.models) || !data.models.length) throw new Error('Acervo vazio.');
    state.models = data.models.map(validateModel);
    renderChoices(state.models);
    const selectedId = new URLSearchParams(location.search).get('model');
    selectModel(state.models.find(model => model.id === selectedId) || state.models[0], false);
    $('specimen-workspace').hidden = false;
    $('study-context').hidden = false;
  } catch {
    $('specimen-list').replaceChildren();
    $('specimens-error').hidden = false;
    $('specimen-workspace').hidden = true;
    $('study-context').hidden = true;
  }
}

initialize();
