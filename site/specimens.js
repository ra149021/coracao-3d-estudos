const $ = id => document.getElementById(id);
const state = { models: [], selected: null, loaded: null, reminder: null, native: null, controller: null };

function httpsURL(value) {
  const url = new URL(value);
  if (url.protocol !== 'https:') throw new Error('A fonte deve usar HTTPS.');
  return url.href;
}

function validateModel(model) {
  if (model.type === 'local') {
    if (!model.id || !model.title || !/^assets\/(heart-ct|lung-ct|heart-hra|respiratory)\/model\.glb$/.test(model.asset)) throw new Error('Modelo local inválido.');
    if (model.catalog && (!/^assets\/(heart-hra|respiratory)\/catalog\.json$/.test(model.catalog) || !Array.isArray(model.groups) || !Array.isArray(model.labels))) throw new Error('Identificação inválida.');
    for (const key of ['url', 'authorUrl', 'institutionUrl']) httpsURL(model[key]);
    if (!Array.isArray(model.limits) || !Array.isArray(model.observations)) throw new Error('Orientações indisponíveis.');
    return model;
  }
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
  state.controller?.abort(); state.controller = null;
  state.native?.dispose(); state.native = null;
  $('native-tools').hidden = true;
  $('anatomy-study').hidden = true; $('native-names').hidden = true;
  $('native-names').setAttribute('aria-pressed', 'true'); $('anatomy-isolate').setAttribute('aria-pressed','false');
  $('native-rotate').setAttribute('aria-pressed', 'false');
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
    if (observation.photoIds?.length && document.body.dataset.photoCollection === 'personal') {
      const links = document.createElement('div');links.className = 'observation-sources';
      for (const photo of observation.photoIds) {
        const link = document.createElement('a');
        link.href = `specimens.html?${new URLSearchParams({photo})}`;
        link.textContent = photo.startsWith('esquema') ? 'Comparar com seu esquema →' : `Comparar com foto ${photo.replace('_', ' ')} →`;
        links.append(link);
      }
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

document.addEventListener('atlas-gallery-ready', () => { if (state.selected) renderObservations(state.selected); });

function selectModel(model, updateURL = true) {
  clearPlayer();
  state.selected = model;
  $('model-picker').value = model.id;
  for (const button of $('specimen-list').querySelectorAll('button')) button.setAttribute('aria-pressed', String(button.dataset.model === model.id));
  $('model-title').textContent = model.title;
  $('model-kicker').textContent = `${model.code} / ${model.catalog ? 'ESTRUTURAS NOMEADAS' : model.type === 'local' ? 'RECONSTRUÇÃO DE CT' : 'PEÇA HUMANA'}`;
  $('viewer-badge').textContent = model.catalog ? 'Nomes e seleção' : model.type === 'local' ? 'Reconstrução de exame' : 'Peça digitalizada';
  $('model-load-note').textContent = model.catalog ? 'Modelo da fonte anatômica com nomes visíveis. Clique em um rótulo ou escolha uma estrutura para destacar e ler sua descrição.' : model.type === 'local' ? 'Reconstrução de tomografia, com origem e licença verificadas. Arraste para girar e use a roda para aproximar.' : 'Peça humana digitalizada no visualizador oficial do Sketchfab. Requer internet.';
  $('model-load-detail').textContent = model.type === 'local' ? 'Arquivo servido pelo atlas; sem conexão com visualizador externo.' : 'A conexão com o visualizador começa ao clicar.';
  $('load-model').textContent = model.catalog ? 'Explorar com nomes visíveis' : model.type === 'local' ? 'Carregar reconstrução de exame' : 'Carregar peça digitalizada';
  $('placeholder-code').textContent = `${model.code} · ${model.author}`;
  $('collection-label').textContent = model.institution;
  $('model-description').textContent = model.description;
  $('specimen-description').textContent = model.specimen;
  $('license-label').textContent = model.license;
  externalLink('open-source', model.url);
  externalLink('license-source', model.url);
  externalLink('institution-link', model.institutionUrl, model.institution);
  externalLink('author-link', model.authorUrl, model.author);
  $('player-status').textContent = 'Peça selecionada. O visualizador aguarda seu clique.';
  renderObservations(model);
  const respiratory = model.system === 'respiratory';
  const params = new URLSearchParams({ system: respiratory ? 'respiratory' : 'circulatory' });
  if (model.photoRegion) params.set('region', model.photoRegion);
  const studyLinks = $('model-study-links');
  studyLinks.replaceChildren();
  for (const [label, href] of [
    ['Comparar com suas fotografias →', `specimens.html?${params}#photographs`],
    ['Explorar estruturas na cena didática →', respiratory ? 'atlas.html?system=respiratory&view=didactic' : 'atlas.html?view=didactic'],
    ['Retomar a teoria →', `theory.html?system=${respiratory ? 'respiratory' : 'circulatory'}`]
  ]) {
    const link = document.createElement('a');link.textContent = label;link.href = href;studyLinks.append(link);
  }
  if (model.system === 'both') {
    const link = document.createElement('a');link.textContent = 'Comparar com fotos dos pulmões →';
    link.href = 'specimens.html?system=respiratory&region=pulmoes#photographs';studyLinks.append(link);
  }
  if (updateURL) {
    const url = new URL(location.href);
    url.searchParams.set('model', model.id);
    history.replaceState(null, '', url);
  }
}

async function loadModel() {
  const model = state.selected;
  if (!model || state.loaded) return;
  if (model.type === 'local') {
    state.loaded = model.id;
    state.controller = new AbortController();
    const controller = state.controller;
    $('load-model').disabled = true; $('player-placeholder').hidden = true; $('stop-model').hidden = false;
    $('player-status').textContent = 'Preparando a reconstrução de exame…';
    try {
      const {mountRealModel} = await import('./real-model-viewer.js');
      if (controller.signal.aborted) return;
      const viewer = await mountRealModel($('embed-host'), model, controller.signal, message => { $('player-status').textContent = message; });
      if (controller.signal.aborted) { viewer.dispose(); return; }
      state.native = viewer; $('native-tools').hidden = false;
      if (viewer.parts.length) {
        $('anatomy-part').replaceChildren(new Option('Visão geral · nomes principais',''), ...viewer.parts.map(part=>new Option(part.label,part.id)));
        $('anatomy-study').hidden = false; $('native-names').hidden = false;
        $('anatomy-isolate').disabled = true;
        $('anatomy-explanation').textContent = 'Clique em um nome ou na peça para destacar a estrutura. Escolha na lista para revelar as peças internas.';
      }
      $('player-status').textContent = model.catalog ? 'Nomes ativados. Selecione uma estrutura para destacá-la; “Isolar seleção” revela seu formato.' : 'Reconstrução carregada. Arraste para girar; roda para aproximar; botão direito para mover.';
      $('embed-help').textContent = model.catalog ? 'Os nomes identificam peças da fonte. Gire para ver outros rótulos; estruturas encobertas podem ser escolhidas na lista. Cores ilustrativas; detalhes não segmentados não recebem nomes próprios.' : 'Geometria derivada de exame, sem estruturas segmentadas para rotular. Escolha um modelo “com nomes” na lista para estudar a identificação.';
    } catch (error) {
      if (controller.signal.aborted) return;
      clearPlayer(); $('player-status').textContent = 'Não foi possível carregar a reconstrução. Tente novamente ou abra a fonte.';
    }
    return;
  }
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
  $('model-picker').replaceChildren(...models.map(model => new Option(model.shortTitle + ' · ' + model.code, model.id)));
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
$('model-picker').addEventListener('change', () => { const model = state.models.find(model => model.id === $('model-picker').value); if (model) selectModel(model); });
$('native-fit').addEventListener('click', () => state.native?.fit());
$('native-in').addEventListener('click', () => state.native?.zoom(.8));
$('native-out').addEventListener('click', () => state.native?.zoom(1.25));
$('native-rotate').addEventListener('click', () => $('native-rotate').setAttribute('aria-pressed', String(state.native?.toggleRotation() || false)));
$('native-names').addEventListener('click', () => $('native-names').setAttribute('aria-pressed',String(state.native?.toggleNames() || false)));
$('anatomy-part').addEventListener('change', () => state.native?.select($('anatomy-part').value));
$('anatomy-isolate').addEventListener('click', () => $('anatomy-isolate').setAttribute('aria-pressed',String(state.native?.toggleIsolation() || false)));
$('anatomy-reset').addEventListener('click', () => { state.native?.select(null); state.native?.fit(); });
$('embed-host').addEventListener('anatomy-select', event => {
  const part = event.detail;
  $('anatomy-part').value = part?.id || ''; $('anatomy-isolate').disabled = !part;
  if (!part) $('anatomy-isolate').setAttribute('aria-pressed','false');
  $('anatomy-explanation').textContent = part ? `${part.label} — ${part.note} Fonte: ${part.source}.` : 'Visão geral. Clique em um nome ou escolha uma estrutura na lista para revelar as peças internas.';
});
function filterModels(updateSelection = true) {
  const system = $('model-filter').value;
  const models = state.models.filter(model => system === 'all' || model.system === system || model.system === 'both');
  renderChoices(models);
  $('model-count').textContent = `${models.length} de ${state.models.length} modelos · carregamento ao clicar`;
  if (updateSelection && models.length) selectModel(models.find(model => model.id === state.selected?.id) || models[0]);
  return models;
}
$('model-filter').addEventListener('change', () => {
  filterModels();
  const url = new URL(location.href);
  if ($('model-filter').value === 'all') url.searchParams.delete('modelsystem');
  else url.searchParams.set('modelsystem', $('model-filter').value);
  history.replaceState(null, '', url);
});
$('stop-model').addEventListener('click', () => { stopPlayer(); $('load-model').focus({ preventScroll: true }); });
window.addEventListener('pagehide', stopPlayer);

async function initialize() {
  try {
    const response = await fetch('assets/specimens.json');
    if (!response.ok) throw new Error('Acervo indisponível.');
    const data = await response.json();
    if (!Array.isArray(data.models) || !data.models.length) throw new Error('Acervo vazio.');
    state.models = data.models.map(model => validateModel({system: 'circulatory', ...model}));
    const params = new URLSearchParams(location.search);
    const selectedId = params.get('model');
    const selected = state.models.find(model => model.id === selectedId);
    const system = params.get('modelsystem') || params.get('system');
    if (['circulatory', 'respiratory'].includes(system)) $('model-filter').value = system;
    if (selected && $('model-filter').value !== 'all' && !['both', $('model-filter').value].includes(selected.system)) $('model-filter').value = 'all';
    const models = filterModels(false);
    selectModel(selected || models[0], false);
    $('specimen-workspace').hidden = false;
    $('study-context').hidden = false;
    if (selected && !params.has('photo')) $('institutional').scrollIntoView({block: 'start'});
  } catch {
    $('specimen-list').replaceChildren();
    $('specimens-error').hidden = false;
    $('specimen-workspace').hidden = true;
    $('study-context').hidden = true;
  }
}

initialize();
