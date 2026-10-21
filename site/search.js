const query = document.getElementById('global-query');
const filter = document.getElementById('system-filter');
const status = document.getElementById('search-status');
const results = document.getElementById('search-results');
const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const names = {circulatory: 'Circulatório', respiratory: 'Respiratório'};
const params = new URLSearchParams(location.search);
query.value = params.get('q') || '';
filter.value = names[params.get('system')] ? params.get('system') : '';
let items = null;
function render() {
  const url = new URL(location.href);
  query.value ? url.searchParams.set('q', query.value) : url.searchParams.delete('q');
  filter.value ? url.searchParams.set('system', filter.value) : url.searchParams.delete('system');
  history.replaceState(null, '', url);
  results.replaceChildren();
  if (!items) return;
  const terms = normalize(query.value).trim().split(/\s+/).filter(Boolean);
  if (!terms.length) { status.textContent = 'Digite um tema para buscar nos dois sistemas.'; return; }
  const matches = items.filter(item => (!filter.value || item.system === filter.value) && terms.every(term => item.search.includes(term)))
    .sort((a, b) => terms.filter(t => normalize(b.title).includes(t)).length - terms.filter(t => normalize(a.title).includes(t)).length || a.title.localeCompare(b.title, 'pt-BR'));
  status.textContent = matches.length ? `${matches.length} ${matches.length === 1 ? 'resultado' : 'resultados'} para “${query.value.trim()}”.` : 'Nenhum resultado. Tente menos palavras ou outro termo anatômico.';
  for (const item of matches) {
    const li = document.createElement('li');
    const heading = document.createElement('h2');
    const link = document.createElement('a');
    link.href = item.url;
    link.textContent = item.title;
    const label = document.createElement('p');
    label.className = 'result-system';
    label.textContent = names[item.system];
    const summary = document.createElement('p');
    summary.textContent = item.summary;
    heading.append(link);
    li.append(label, heading, summary);
    results.append(li);
  }
}
document.getElementById('search-form').addEventListener('submit', event => { event.preventDefault(); render(); });
query.addEventListener('input', render);
filter.addEventListener('change', render);
try {
  const response = await fetch('assets/search-index.json');
  if (!response.ok) throw new Error('Index unavailable');
  const data = await response.json();
  if (data.version !== 1 || !Array.isArray(data.items) || !data.items.length) throw new Error('Invalid index');
  items = data.items.map(item => {
    if (!names[item.system] || !['id', 'chapterId', 'title', 'summary', 'text', 'url'].every(key => typeof item[key] === 'string')) throw new Error('Invalid entry');
    const target = new URL(item.url, location.href);
    const theory = new URL('theory.html', location.href);
    if (target.origin !== theory.origin || target.pathname !== theory.pathname || target.searchParams.get('system') !== item.system || target.searchParams.get('chapter') !== item.chapterId) throw new Error('Invalid chapter target');
    return {...item, search: normalize([item.title, item.summary, item.text, names[item.system]].join(' '))};
  });
  render();
} catch {
  items = null;
  status.textContent = 'Busca global indisponível nesta instalação: não foi possível carregar um índice válido. Explore as unidades pelos links abaixo; nenhum resultado foi inventado.';
}
