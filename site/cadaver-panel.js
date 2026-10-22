const siteRoot = new URL('./', import.meta.url);
const key = ({ modelId, system, partId }) => JSON.stringify([modelId, system, partId]);
const text = (tag, value, className) => {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
};

const nonempty = value => typeof value === 'string' && value.trim().length > 0;
function localPhoto(src) {
  if (!nonempty(src) || !src.startsWith('assets/') || /[%\\\\?#:\u0000-\u0020]/.test(src) ||
      src.split('/').some(segment => !segment || segment === '.' || segment === '..')) throw new Error('Unsafe photo path');
  const url = new URL(src, siteRoot);
  if (url.origin !== siteRoot.origin || !url.pathname.startsWith(siteRoot.pathname + 'assets/')) throw new Error('Unsafe photo path');
  return url.href;
}
function validate(data) {
  if (data?.version !== 1 || !Array.isArray(data.entries) || !data.photos || typeof data.photos !== 'object' || Array.isArray(data.photos)) throw new Error('Invalid manifest');
  for (const photo of Object.values(data.photos)) {
    if (!photo || !nonempty(photo.title) || !nonempty(photo.evidence)) throw new Error('Invalid evidence');
    localPhoto(photo.src);
  }
  const seen = new Set();
  for (const entry of data.entries) {
    if (!entry || !['modelId', 'system', 'partId', 'label'].every(field => nonempty(entry[field])) ||
        !Array.isArray(entry.photoIds) || !entry.photoIds.length ||
        !entry.photoIds.every(id => nonempty(id) && Object.hasOwn(data.photos, id)) ||
        new Set(entry.photoIds).size !== entry.photoIds.length || seen.has(key(entry))) throw new Error('Invalid mapping');
    seen.add(key(entry));
  }
  return data;
}

// Selection-specific qualifications never replace the original photo evidence.
function selectionEvidence(entry) {
  const details = text('section', '', 'cadaver-selection-evidence');
  details.setAttribute('aria-label', 'Evidência e limites desta seleção');
  for (const [field, label] of [['status', 'Status da correspondência'], ['visualLocator', 'Localizador visual'],
    ['evidence', 'Evidência desta seleção'], ['limits', 'Limites e ressalvas']]) {
    const values = Array.isArray(entry[field]) ? entry[field] : [entry[field]];
    const present = values.filter(nonempty);
    if (present.length) details.append(text('p', `${label}: ${present.join(' • ')}`, `cadaver-selection-field-${field}`));
  }
  return details;
}

/** Explicit selection adapter; never guesses anatomy from names. */
export function mountCadaverPanel(host, { manifestPath = 'assets/cadaver-comparison.json' } = {}) {
  const manifestURL = localPhoto(manifestPath);
  const root = text('section', '', 'cadaver-panel');
  root.setAttribute('aria-label', 'Comparação cadavérica');
  const heading = text('h2', 'Comparação cadavérica');
  const status = text('p', 'Selecione uma estrutura no modelo 3D.');
  status.setAttribute('role', 'status');
  const content = document.createElement('div');
  root.append(heading, status, content);
  host.append(root);
  const dialog = text('dialog', '', 'cadaver-panel-dialog');
  dialog.setAttribute('aria-label', 'Original ampliado');
  const back = text('button', 'Voltar à comparação');
  back.type = 'button';
  const enlarged = document.createElement('div');
  dialog.append(back, enlarged);
  root.append(dialog);
  let opener = null;
  function closeModal() {
    if (dialog.open) dialog.close();
    enlarged.replaceChildren();
    if (opener?.isConnected) opener.focus({ preventScroll: true });
    opener = null;
  }
  back.addEventListener('click', closeModal);
  dialog.addEventListener('cancel', event => { event.preventDefault(); closeModal(); });
  let manifest, selection = null, failure = false, destroyed = false;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  const ready = fetch(manifestURL, { signal: controller.signal, redirect: 'error' })
    .then(response => { if (!response.ok) throw new Error('manifest'); return response.json(); })
    .then(data => { manifest = validate(data); render(); })
    .catch(() => { failure = true; render(); })
    .finally(() => clearTimeout(timeout));
  function render() {
    if (destroyed) return;
    closeModal();
    content.replaceChildren();
    if (!selection) { status.textContent = 'Selecione uma estrutura no modelo 3D.'; return; }
    if (failure) { status.textContent = 'Não foi possível carregar o manifesto de comparação.'; return; }
    if (!manifest) { status.textContent = 'Carregando comparações…'; return; }
    const entry = manifest.entries.find(item => key(item) === key(selection));
    if (!entry) {
      status.textContent = 'Sem correspondência revisada para esta seleção. Isso não indica ausência de foto no acervo.';
      return;
    }
    status.textContent = entry.label;
    const details = selectionEvidence(entry);
    if (details.childElementCount) content.append(details);
    for (const id of entry.photoIds) {
      const photo = manifest.photos[id];
      const figure = document.createElement('figure');
      const image = document.createElement('img');
      image.src = localPhoto(photo.src);
      image.alt = photo.title;
      const button = text('button', `Ampliar original: ${photo.title}`);
      button.type = 'button';
      button.addEventListener('click', () => {
        opener = button;
        enlarged.replaceChildren(image.cloneNode(), text('p', photo.evidence));
        if (details.childElementCount) enlarged.append(details.cloneNode(true));
        dialog.showModal();
        back.focus();
      });
      button.disabled = true;
      const mediaStatus = text('p', 'Carregando imagem original…');
      mediaStatus.setAttribute('role', 'status');
      image.addEventListener('load', () => { button.disabled = false; mediaStatus.textContent = ''; });
      image.addEventListener('error', () => {
        button.disabled = true;
        image.hidden = true;
        mediaStatus.textContent = 'Não foi possível abrir esta imagem. O vínculo existe, mas o arquivo não pôde ser carregado.';
      });
      figure.append(image, text('figcaption', photo.title), text('p', photo.evidence), mediaStatus, button);
      content.append(figure);
    }
  }
  return Object.freeze({
    ready,
    setSelection(value) {
      if (destroyed) return;
      selection = value && ['modelId', 'system', 'partId'].every(field => nonempty(value[field]))
        ? { modelId: value.modelId, system: value.system, partId: value.partId } : null;
      render();
    },
    clear() { selection = null; render(); },
    destroy() {
      destroyed = true;
      controller.abort();
      clearTimeout(timeout);
      closeModal();
      root.remove();
    },
  });
}
