// Keep a cited class or slide alongside the explanation, without changing pages.
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const panel = el('dialog', 'study-source-panel');
panel.id = 'source-panel';
panel.setAttribute('aria-labelledby', 'source-title');
const header = el('header', 'source-panel-header');
const title = el('h2', '', 'Material de apoio');
title.id = 'source-title';
const fullLink = el('a', 'action', 'Abrir em outra aba ↗');
fullLink.target = '_blank';
fullLink.rel = 'noopener noreferrer';
const close = el('button', 'action', 'Voltar à leitura');
close.type = 'button';
close.setAttribute('aria-label', 'Fechar material e voltar à leitura');
header.append(title, fullLink, close);
const frame = el('iframe');
frame.id = 'source-frame';
frame.title = 'Slide ou videoaula de apoio';
frame.allow = 'fullscreen';
frame.src = 'about:blank';
panel.append(header, frame);
document.body.append(panel);
let trigger = null;

function releaseSource() {
  // A breakpoint change briefly closes/reopens the same dialog.
  if (panel.open) return;
  // Unload immediately so a closed class cannot keep playing out of view.
  if (frame.getAttribute('src') !== 'about:blank') frame.src = 'about:blank';
  document.body.classList.remove('study-source-open');
  if (trigger?.isConnected) trigger.focus({preventScroll: true});
}
function closeSource() {
  if (!panel.open) return;
  panel.close();
  releaseSource();
}
panel.addEventListener('close', releaseSource);
close.addEventListener('click', closeSource);
const escape = event => {
  if (event.key === 'Escape' && panel.open) {
    event.preventDefault();
    closeSource();
  }
};
document.addEventListener('keydown', escape);
frame.addEventListener('load', () => {
  try { frame.contentDocument?.addEventListener('keydown', escape); } catch { /* Only local frames are created. */ }
});

const wideScreen = matchMedia('(min-width: 1450px)');
function showSource() {
  document.body.classList.toggle('study-source-open', wideScreen.matches);
  if (wideScreen.matches) panel.show();
  else panel.showModal();
}
wideScreen.addEventListener('change', () => {
  if (!panel.open) return;
  panel.close();
  showSource();
  close.focus({preventScroll: true});
});

document.addEventListener('click', event => {
  const link = event.target.closest('a[href]');
  if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const url = new URL(link.href, location.href);
  const classroom = new URL('classroom.html', location.href);
  if (url.origin !== location.origin || url.pathname !== classroom.pathname || (!url.searchParams.has('doc') && !url.searchParams.has('video'))) return;
  // Review dialogs keep their own focus/reveal flow; allow their normal links.
  if (link.closest('#review-dialog')) return;
  event.preventDefault();
  trigger = link;
  fullLink.href = url.href;
  title.textContent = url.searchParams.has('video') ? 'Aula de apoio à leitura' : 'Slide de apoio à leitura';
  url.searchParams.set('embed', '1');
  frame.src = url.href;
  if (!panel.open) showSource();
  close.focus({preventScroll: true});
});
