/** Teaching pages stay intact; a gallery loads at most two pages at a time. */
export const documentAliases = {coracao:'coracao',vasos:'vasos',linfatico:'linfatico',respiratorio:'respiratorio',roteiro:'roteiro',C:'coracao',V:'vasos',L:'linfatico'};
let galleryIndex = 0;
const element = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

function pages(value) {
  if (Array.isArray(value)) return value.flatMap(pages);
  if (typeof value === 'number') return Number.isInteger(value) && value > 0 ? [value] : [];
  const values = [];
  for (const token of String(value || '').split(/[,;]/)) {
    const range = token.trim().match(/^(\d+)\s*[-–—]\s*(\d+)$/);
    if (range) {
      const start = Number(range[1]), end = Number(range[2]);
      if (end >= start && end - start < 100) for (let page = start; page <= end; page++) values.push(page);
    } else if (/^\d+$/.test(token.trim())) values.push(Number(token));
  }
  return values.filter(page => page > 0);
}

export function createFigureGallery(figures, {references = [], sourceInfo, interactive = true, label = 'Figuras desta seção'} = {}) {
  const choices = new Map();
  for (const ref of [...(figures || []), ...references]) {
    if (!ref || !documentAliases[ref.source]) continue;
    for (const page of pages(ref.page)) {
      const item = {...ref, page}, info = sourceInfo(item);
      if (info.source.pageCount && page > info.source.pageCount) continue;
      const id = `${documentAliases[ref.source]}:${page}`;
      if (!choices.has(id)) choices.set(id, {...item, id, info});
    }
  }
  if (!choices.size) return null;
  const items = [...choices.values()], container = element('div', 'lesson-figures');
  container.setAttribute('role', 'group');
  container.setAttribute('aria-label', label);
  const uid = `figure-gallery-${++galleryIndex}`;
  let first = items[0].id, second = items[1]?.id;
  const preferred = new Set((figures || []).flatMap(ref => pages(ref.page).map(page => `${documentAliases[ref.source]}:${page}`)));
  let comparing = preferred.size > 1 && Boolean(second);
  const grid = element('div', 'figure-grid');
  let primarySelect, secondarySelect, secondaryField, compare;

  function figure(item) {
    const node = element('figure', 'teaching-figure');
    node.dataset.source = documentAliases[item.source];
    node.dataset.page = item.page;
    const link = element('a', 'figure-image-link');
    link.href = item.info.url;
    link.setAttribute('aria-label', `Abrir ${item.info.label} na biblioteca de slides`);
    const img = element('img');
    img.loading = 'lazy';
    img.decoding = 'async';
    img.alt = `Página ${item.page} · ${item.info.source.label}${item.caption ? '. ' + item.caption : ''}`;
    img.src = `assets/lectures/slides/${documentAliases[item.source]}/${item.page}.jpg`;
    const unavailable = element('p', 'figure-unavailable', 'A prévia não pôde ser carregada. Use o link para conferir o slide na biblioteca.');
    unavailable.hidden = true;
    img.addEventListener('error', () => {img.hidden = true; unavailable.hidden = false;}, {once: true});
    link.append(img, unavailable);
    const caption = element('figcaption');
    if (item.caption) caption.append(element('span', 'figure-description', item.caption));
    const original = element('a', '', `${item.info.label} ↗`);
    original.href = item.info.url;
    caption.append(original);
    node.append(link, caption);
    return node;
  }
  function render() {
    if (first === second) second = items.find(item => item.id !== first)?.id;
    grid.classList.toggle('is-comparison', comparing);
    grid.replaceChildren(figure(choices.get(first)));
    if (comparing && second) grid.append(figure(choices.get(second)));
    if (secondaryField) {
      secondaryField.hidden = !comparing;
      secondarySelect.replaceChildren();
      for (const item of items.filter(item => item.id !== first)) {
        const option = element('option', '', item.info.label); option.value = item.id;
        secondarySelect.append(option);
      }
      secondarySelect.value = second;
    }
  }
  if (interactive && items.length > 1) {
    const controls = element('div', 'figure-controls');
    const primaryField = element('label', 'figure-field', 'Figura em leitura');
    primarySelect = element('select'); primarySelect.id = `${uid}-first`; primaryField.htmlFor = primarySelect.id;
    for (const item of items) {const option = element('option', '', item.info.label); option.value = item.id; primarySelect.append(option);}
    primarySelect.value = first;
    primarySelect.addEventListener('change', () => {first = primarySelect.value; render();});
    primaryField.append(primarySelect);
    const toggle = element('label', 'figure-compare-toggle');
    compare = element('input'); compare.type = 'checkbox'; compare.checked = comparing;
    compare.addEventListener('change', () => {comparing = compare.checked; render();});
    toggle.append(compare, document.createTextNode('Comparar duas páginas'));
    secondaryField = element('label', 'figure-field', 'Comparar com');
    secondarySelect = element('select'); secondarySelect.id = `${uid}-second`; secondaryField.htmlFor = secondarySelect.id;
    secondarySelect.addEventListener('change', () => {second = secondarySelect.value; render();});
    secondaryField.append(secondarySelect);
    controls.append(primaryField, toggle, secondaryField);
    container.append(controls);
  }
  container.append(grid, element('p', 'figure-note', 'Legendas originais preservadas. Abra o slide para observar os detalhes em tamanho maior.'));
  render();
  return container;
}
