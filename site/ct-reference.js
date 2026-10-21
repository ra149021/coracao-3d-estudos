import { mountRealModel } from './real-model-viewer.js';

const $ = id => document.getElementById(id);
const lung = new URLSearchParams(location.search).get('model') === 'lung';
const model = lung ? {
  id: 'lung-ct', title: 'Conjunto broncovascular de CT', asset: 'assets/lung-ct/model.glb',
  purpose: 'Compare a ramificação tridimensional e as relações espaciais do conjunto broncovascular. Fonte de caso real preparada para ensino cirúrgico; não é uma superfície pulmonar completa.',
  limits: 'Conjunto sem segmentação semântica editável: não selecione um vaso ou brônquio individual por este arquivo. Os autores suavizaram e truncaram superfícies para impressão; entalhes para ímãs e pequenos componentes são artefatos preservados, não anatomia. Não mostra pleuras nem volumes segmentares completos.',
  credit: 'Armelle J. A. Meershoek, Tom G. J. Loonen, Thomas J. J. Maal, Edo J. Hekma e Niek Hugen (2023). Modelo: CC BY-NC-SA 4.0, uso não comercial e compartilhamento pela mesma licença; diferente da licença do artigo.',
  attribution: 'assets/lung-ct/NOTICE.md', source: 'https://doi.org/10.1007/s40670-023-01807-x', back: 'atlas.html?system=respiratory',
} : {
  id: 'nih-heart-ct', title: 'Coração reconstruído de CT', asset: 'assets/heart-ct/model.glb',
  purpose: 'Observe a forma global e as relações das superfícies reconstruídas de uma aquisição de CT em diástole. Compare com as câmaras e vasos nomeados do atlas, sem sobrepor acervos de pessoas diferentes.',
  limits: 'Caso específico: “17 yo Female, Normal Heart”. Arquivo sem segmentação semântica para selecionar câmaras, coronárias ou valvas individuais. A resolução e a aquisição limitam detalhes valvares; material fosco não é textura de tecido. Não é um coração dissecado nem uma validação do atlas.',
  credit: 'Matthew Bramlet, NIH 3DPX-002636, versão 2. Domínio público / CC0 1.0. GLB oficial preservado byte a byte; somente transformação global uniforme e material de exibição.',
  attribution: 'assets/heart-ct/ATTRIBUTION.md', source: 'https://3d.nih.gov/entries/3DPX-002636', back: 'atlas.html',
};
$('ct-title').textContent = model.title;
document.title = model.title + ' · Atlas local';
$('ct-purpose').textContent = model.purpose;
$('ct-limits').textContent = model.limits;
$('ct-credit').textContent = model.credit;
$('ct-license').href = model.attribution;
$('ct-original').href = model.source;
$('ct-back').href = model.back;
$('ct-other').href = 'ct-reference.html?model=' + (lung ? 'heart' : 'lung');
$('ct-other').textContent = lung ? 'Ver coração de CT local' : 'Ver conjunto broncovascular local';
const lifecycle = new AbortController();
window.addEventListener('pagehide', () => lifecycle.abort(), {once: true});
try {
  const api = await mountRealModel($('ct-host'), model, lifecycle.signal, text => { $('ct-status').textContent = text; });
  window.ctViewer = api;
  $('ct-fit').onclick = () => api.fit();
  $('ct-zoom-in').onclick = () => api.zoom(.85);
  $('ct-zoom-out').onclick = () => api.zoom(1 / .85);
  $('ct-rotate').onclick = () => $('ct-rotate').setAttribute('aria-pressed', String(api.toggleRotation()));
  document.querySelectorAll('.ct-controls button').forEach(button => { button.disabled = false; });
  $('ct-status').textContent = 'Modelo local carregado · arraste para explorar · sem rótulos individuais';
} catch (error) {
  if (error.name !== 'AbortError') {
    $('ct-status').textContent = 'Não foi possível carregar a referência. O atlas segmentado continua disponível no link acima. ' + error.message;
    $('ct-status').setAttribute('role', 'alert');
  }
}
