const $ = id => document.getElementById(id);
const normalize = text => String(text).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const systemNames = { circulatory: 'Circulatório', respiratory: 'Respiratório' };
const preparation = kind => ({ mixed: 'Crânio seco/colorido ou composição mista', cadaver: 'Peça cadavérica', illustration: 'Esquema desenhado' })[kind];
const viewNames = { photo: 'Foto individual', sheet: 'Prancha completa', illustration: 'Esquema' };
const state = { images: [], regions: {}, filtered: [], visible: {circulatory: 12, respiratory: 12}, selected: null, zoom: null, opener: null };
const dialog = $('photo-dialog');
let initialization = 0;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function assetPath(value) {
  if (!/^assets\/(cadaver|public-specimens)\/(originals|thumbs)\/[a-z]+_\d{3}(?:_\d{2})?\.(png|jpe?g|webp)$/.test(value)) throw new Error('Caminho de imagem inválido.');
  return value;
}

function updateURL() {
  const url = new URL(location.href);
  for (const [key, id] of [['system', 'photo-system'], ['region', 'photo-region'], ['kind', 'photo-kind'], ['view', 'photo-view-type'], ['q', 'photo-search']]) {
    const value = $(id).value;
    if (value && value !== 'all') url.searchParams.set(key, value);
    else url.searchParams.delete(key);
  }
  if (state.selected) url.searchParams.set('photo', state.selected.id);
  else url.searchParams.delete('photo');
  history.replaceState(null, '', url);
}

function populateRegions() {
  const select = $('photo-region'), previous = select.value, system = $('photo-system').value;
  select.replaceChildren(new Option('Todas as regiões', 'all'));
  const available = new Set(state.images.filter(item => system === 'all' || item.system === system).map(item => item.region));
  for (const [key, label] of Object.entries(state.regions)) if (available.has(key)) select.append(new Option(label, key));
  if (available.has(previous)) select.value = previous;
}

function applyFilters(syncURL = true) {
  state.visible = {circulatory: 12, respiratory: 12};
  const system = $('photo-system').value, region = $('photo-region').value, kind = $('photo-kind').value;
  const view = $('photo-view-type').value;
  const words = normalize($('photo-search').value).split(/\s+/).filter(Boolean);
  state.filtered = state.images.filter(item => {
    const text = normalize([item.title, ...item.terms, state.regions[item.region], item.id, systemNames[item.system]].join(' '));
    return (system === 'all' || item.system === system) && (region === 'all' || item.region === region) &&
      (kind === 'all' || item.kind === kind) && (view === 'all' || item.viewType === view) && words.every(word => text.includes(word));
  });
  if (system !== 'all') $(`photos-${system}`).open = true;
  const systems = new Set(state.filtered.map(item => item.system));
  if (systems.size === 1) $(`photos-${[...systems][0]}`).open = true;
  renderGrid();
  if (syncURL) updateURL();
}

function openPhoto(item, opener) {
  if (opener) state.opener = opener;
  state.selected = item;
  $('photo-title').textContent = item.title;
  $('photo-code').textContent = `${systemNames[item.system]} / ${item.id.replace('_', ' · ')}`;
  $('photo-terms').replaceChildren(...item.terms.map(term => element('span', '', term)));
  $('photo-terms-note').textContent = item.sourceUrl ? 'Nomes conforme a descrição da fonte. A fotografia não recebeu rótulos ou alterações locais.' : item.parentId
    ? 'Termos da prancha de origem: nem todos aparecem neste recorte. Abra a prancha para conferir as legendas externas. Fotos sobrepostas conservam o que está visível na origem.'
    : 'A lista ajuda a localizar a foto. Os rótulos dos baralhos e do esquema não têm auditoria anatômica individual.';
  $('photo-preparation').textContent = preparation(item.kind);
  $('photo-package').textContent = item.package;
  $('photo-source').textContent = item.sourceFile;
  $('photo-resolution').textContent = `${item.width} × ${item.height} px` + (item.kind === 'illustration' || item.sourceUrl ? '' : ` · ${item.noteIds.length} notas associadas ${item.parentId ? 'à prancha' : 'no Anki'}`);
  $('photo-license').replaceChildren();
  if (item.sourceUrl && item.licenseUrl) {
    for (const [url, label] of [[item.sourceUrl, `${item.author} · fonte original ↗`], [item.licenseUrl, item.license]]) {
      const link = element('a', 'action', label); link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; $('photo-license').append(link);
    }
  } else $('photo-license').textContent = 'Acervo pessoal local; autorização de divulgação não documentada.';
  $('photo-original-link').href = item.original;
  $('photo-original-link').textContent = item.parentId ? 'Abrir foto separada ↗' : 'Abrir imagem original ↗';
  $('photo-parent-link').hidden = !item.parentId;
  if (item.parentId) $('photo-parent-link').href = `specimens.html?photo=${encodeURIComponent(item.parentId)}`;
  const children = state.images.filter(photo => photo.parentId === item.id);
  $('photo-crop-links').replaceChildren(...children.map(photo => {
    const link = element('a', 'action', `Foto ${photo.id.slice(-2)} →`);
    link.href = `specimens.html?photo=${encodeURIComponent(photo.id)}`;
    return link;
  }));
  $('photo-atlas-link').href = item.system === 'respiratory' ? 'atlas.html?system=respiratory' : 'atlas.html';
  $('photo-theory-link').href = `theory.html?system=${item.system}`;
  $('photo-copy').textContent = 'Copiar link desta foto';
  const index = state.filtered.findIndex(image => image.id === item.id);
  $('photo-position').textContent = `${index + 1} / ${state.filtered.length}`;
  $('photo-previous').disabled = index <= 0;
  $('photo-next').disabled = index < 0 || index >= state.filtered.length - 1;
  const full = $('photo-full');
  full.alt = `${item.title}. ${preparation(item.kind)}${item.sourceUrl ? ", fotografia original de " + item.author : ", com anotações originais"}.`;
  $('photo-image-status').textContent = 'Carregando a imagem original…';
  full.onload = () => {
    $('photo-image-status').textContent = 'Imagem original carregada. Amplie e use as barras de rolagem para explorar. Setas ← e → trocam de foto; Esc fecha.';
    if (state.zoom === null) fitPhoto();
  };
  full.onerror = () => { $('photo-image-status').textContent = 'Não foi possível abrir a imagem. Tente “Abrir imagem original”.'; };
  full.src = item.original;
  if (!dialog.open) dialog.showModal();
  fitPhoto();
  updateURL();
}

function fitPhoto() {
  state.zoom = null;
  $('photo-viewport').classList.add('fit');
  $('photo-full').style.removeProperty('width');
  $('photo-full').style.removeProperty('height');
  $('photo-viewport').scrollTo(0, 0);
}

function zoomPhoto(scale) {
  if (!state.selected) return;
  const viewport = $('photo-viewport'), item = state.selected;
  const current = state.zoom ?? Math.min(viewport.clientWidth / item.width, viewport.clientHeight / item.height);
  state.zoom = Math.max(0.1, Math.min(4, scale === 'actual' ? 1 : current * scale));
  viewport.classList.remove('fit');
  $('photo-full').style.width = `${Math.round(item.width * state.zoom)}px`;
  $('photo-full').style.height = `${Math.round(item.height * state.zoom)}px`;
}

function movePhoto(direction) {
  const index = state.filtered.findIndex(item => item.id === state.selected?.id);
  const item = state.filtered[index + direction];
  if (item) openPhoto(item);
}

function renderGrid() {
  for (const system of ['circulatory', 'respiratory']) renderSection(system);
  $('photo-status').textContent = `${state.filtered.length} de ${state.images.length} imagens · organizadas por sistema`;
  $('photo-empty').hidden = state.filtered.length > 0;
}

function renderSection(system) {
  const grid = $(`photo-grid-${system}`);
  grid.replaceChildren();
  const group = state.filtered.filter(item => item.system === system);
  const visible = group.slice(0, state.visible[system]);
  $(`images-${system}`).hidden = group.length === 0;
  $(`photo-${system}-count`).textContent = `${group.length} imagens · ${visible.length} por página`;
  for (const item of visible) {
    const card = element('article', 'photo-card');
    card.dataset.photo = item.id;
    const button = element('button', 'photo-open');
    button.type = 'button';
    button.setAttribute('aria-label', `Ampliar: ${item.title}`);
    const img = element('img');
    img.src = item.thumbnail;
    img.alt = item.sourceUrl ? `${item.title} — fotografia de ${item.author}` : `${item.title} — anotações originais`;
    img.loading = 'lazy';
    img.decoding = 'async';
    button.append(img, element('span', '', 'Ampliar ↗'));
    button.addEventListener('click', () => openPhoto(item, button));
    const copy = element('div', 'photo-card-copy');
    const title = element('h3'), titleButton = element('button', '', item.title);
    titleButton.type = 'button';
    titleButton.addEventListener('click', () => openPhoto(item, titleButton));
    title.append(titleButton);
    copy.append(element('p', 'photo-card-code', `${systemNames[item.system]} · ${item.id.split('_').slice(1).join(' / ')}`), title,
      element('p', 'photo-card-region', state.regions[item.region]),
      element('p', 'photo-card-terms', item.terms.slice(0, 4).join(' · ') + (item.terms.length > 4 ? '…' : '')),
      element('span', `photo-kind ${item.kind}`, `${viewNames[item.viewType]} · ${preparation(item.kind)}`));
    card.append(button, copy);
    grid.append(card);
  }
  $(`photo-more-${system}`).hidden = visible.length >= group.length;
}

$('photo-filters').addEventListener('submit', event => event.preventDefault());
$('photo-search').addEventListener('input', () => applyFilters());
$('photo-system').addEventListener('change', () => { populateRegions(); applyFilters(); });
for (const id of ['photo-region', 'photo-kind', 'photo-view-type']) $(id).addEventListener('change', () => applyFilters());
$('photo-reset').addEventListener('click', () => {
  $('photo-search').value = '';
  for (const id of ['photo-system', 'photo-region', 'photo-kind', 'photo-view-type']) $(id).value = 'all';
  $('photos-circulatory').open = true;
  $('photos-respiratory').open = false;
  populateRegions(); applyFilters(); $('photo-search').focus();
});
for (const system of ['circulatory', 'respiratory']) $(`photo-more-${system}`).addEventListener('click', () => {
  const previous = state.visible[system];
  state.visible[system] += 12;
  renderSection(system);
  // Keep keyboard focus on the first newly revealed image rather than a removed card.
  $(`photo-grid-${system}`).children[previous]?.querySelector('button').focus({ preventScroll: true });
});
$('photo-close').addEventListener('click', () => dialog.close());
$('photo-previous').addEventListener('click', () => movePhoto(-1));
$('photo-next').addEventListener('click', () => movePhoto(1));
$('photo-fit').addEventListener('click', fitPhoto);
$('photo-actual').addEventListener('click', () => zoomPhoto('actual'));
$('photo-zoom-in').addEventListener('click', () => zoomPhoto(1.3));
$('photo-zoom-out').addEventListener('click', () => zoomPhoto(1 / 1.3));
dialog.addEventListener('keydown', event => {
  if (event.altKey || event.ctrlKey || event.metaKey || ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) return;
  if ((event.key === 'ArrowLeft' || event.key === 'ArrowRight') && event.target !== $('photo-viewport')) {
    event.preventDefault(); movePhoto(event.key === 'ArrowLeft' ? -1 : 1);
  }
});
dialog.addEventListener('close', () => {
  state.selected = null;
  updateURL();
  if (state.opener?.isConnected) state.opener.focus({ preventScroll: true });
  else $('photo-search').focus({ preventScroll: true });
});
$('photo-copy').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(location.href);
    $('photo-copy').textContent = 'Link copiado';
  } catch {
    $('photo-copy').textContent = 'Copie o endereço na barra do navegador';
  }
});
$('photo-collection-select').addEventListener('change', () => {
  if (dialog.open) dialog.close();
  const url = new URL(location.href); url.searchParams.delete('photo');
  if ($('photo-collection-select').value === 'public') url.searchParams.set('collection', 'public');
  else url.searchParams.delete('collection');
  for (const key of ['region', 'kind', 'view', 'q']) url.searchParams.delete(key);
  history.replaceState(null, '', url); initialize();
});

async function initialize() {
  const serial = ++initialization;
  try {
    const local = ['127.0.0.1', 'localhost', '[::1]'].includes(location.hostname);
    const personal = local && new URLSearchParams(location.search).get('collection') !== 'public';
    let response = await fetch(personal ? 'assets/cadaver-gallery.json' : 'assets/cadaver-public-gallery.json');
    if (!response.ok && personal) response = await fetch('assets/cadaver-public-gallery.json');
    if (!response.ok) throw new Error('Acervo indisponível.');
    const data = await response.json();
    if (serial !== initialization) return;
    $('photo-error').hidden = true;
    for (const input of $('photo-filters').elements) input.disabled = false;
    if (!Array.isArray(data.images) || !data.images.length) throw new Error('Acervo vazio.');
    state.regions = data.regions;
    document.body.dataset.photoCollection = data.collection === 'public' ? 'public' : 'personal';
    $('photo-collection-select').value = document.body.dataset.photoCollection;
    $('photo-collection-select').querySelector('[value=personal]').disabled = !local;
    if (data.collection === 'public') {
      $('photos-heading').textContent = 'Fotografias de peças humanas';
      $('photo-intro').textContent = 'Quatro fotografias de peças humanas por Anatomist90, no Wikimedia Commons, sob CC BY-SA 3.0. Abra uma imagem para conferir sua fonte e licença. O acervo pessoal dos Ankis permanece disponível apenas na instalação local.';
      $('photo-label-note').textContent = data.labelStatus;
    } else {
      $('photos-heading').textContent = 'Seu acervo de peças';
      $('photo-intro').textContent = '152 fotos separadas das pranchas dos Ankis: 84 do circulatório e 68 do respiratório. As 60 imagens-base e o seu esquema das coronárias continuam disponíveis. Escolha “Fotos individuais” para explorar cada recorte ou “Pranchas completas” para conferir o contexto.';
      $('photo-label-note').textContent = 'Os termos foram transcritos das anotações nas imagens. Os rótulos e as setas foram preservados e ainda precisam de conferência anatômica.';
    }
    document.querySelectorAll('.photo-shortcuts a').forEach(link => {
      const params = new URL(link.href).searchParams;
      if (params.has('photo') || params.get('region') === 'laringe') link.hidden = data.collection === 'public';
    });
    document.dispatchEvent(new CustomEvent('atlas-gallery-ready'));
    state.images = data.images.map(item => {
      if (!systemNames[item.system] || !state.regions[item.region] || !['mixed', 'cadaver', 'illustration'].includes(item.kind) ||
          !viewNames[item.viewType] || !Array.isArray(item.terms) || !Array.isArray(item.noteIds) || !item.width || !item.height) throw new Error('Registro inválido.');
      if (item.sourceUrl && (!/^https:\/\/commons\.wikimedia\.org\/wiki\/File:/.test(item.sourceUrl) || item.licenseUrl !== 'https://creativecommons.org/licenses/by-sa/3.0/')) throw new Error('Fonte ou licença pública inválida.');
      return { ...item, original: assetPath(item.original), thumbnail: assetPath(item.thumbnail) };
    });
    const params = new URLSearchParams(location.search);
    $('photo-search').value = '';
    for (const id of ['photo-system', 'photo-region', 'photo-kind', 'photo-view-type']) $(id).value = 'all';
    if (systemNames[params.get('system')]) $('photo-system').value = params.get('system');
    if (['mixed', 'cadaver', 'illustration'].includes(params.get('kind'))) $('photo-kind').value = params.get('kind');
    if (viewNames[params.get('view')]) $('photo-view-type').value = params.get('view');
    $('photo-search').value = params.get('q') || '';
    populateRegions();
    if (Array.from($('photo-region').options).some(option => option.value === params.get('region'))) $('photo-region').value = params.get('region');
    applyFilters(false);
    const selected = state.images.find(item => item.id === params.get('photo'));
    if (selected) {
      if (!state.filtered.includes(selected)) {
        $('photo-search').value = '';
        $('photo-system').value = selected.system;
        $('photo-kind').value = 'all';
        $('photo-view-type').value = 'all';
        populateRegions(); $('photo-region').value = 'all'; applyFilters(false);
      }
      openPhoto(selected);
    }
  } catch (error) {
    if (serial !== initialization) return;
    $('photo-status').textContent = '';
    $('photo-error').hidden = false;
    for (const system of ['circulatory', 'respiratory']) $(`photo-more-${system}`).hidden = true;
    for (const input of $('photo-filters').elements) input.disabled = true;
    console.error('Galeria de fotografias:', error);
  }
}

initialize();
