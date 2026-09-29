const path=location.pathname.split('/').pop() || 'index.html';
const nav=document.createElement('nav');
nav.className='global-nav';nav.setAttribute('aria-label','Navegação principal');
const links=[['index.html','Início'],['atlas.html','Coração 3D'],['atlas.html?system=respiratory','Respiratório 3D'],['specimens.html','Peças reais'],['theory.html','Teoria e revisão'],['classroom.html','Aulas e materiais'],['about.html','Sobre o projeto']];
const brand=document.createElement('a');brand.className='global-brand';brand.href='./';brand.innerHTML='<span aria-hidden="true">✳</span> ATLAS <b>ESTUDO</b>';nav.append(brand);
const items=document.createElement('div');items.className='global-links';items.id='site-navigation';
for(const [url,label] of links){const a=document.createElement('a');a.href=url;a.textContent=label;const target=new URL(url,location.href);if(path===target.pathname.split('/').pop()&&(path!=='atlas.html'||(new URLSearchParams(location.search).get('system')==='respiratory')===(target.searchParams.get('system')==='respiratory')))a.setAttribute('aria-current','page');items.append(a);}
const toggle=document.createElement('button');toggle.type='button';toggle.className='nav-toggle';toggle.textContent='Menu';toggle.setAttribute('aria-controls','site-navigation');toggle.setAttribute('aria-expanded','false');
function closeMenu(){toggle.setAttribute('aria-expanded','false');nav.classList.remove('nav-open');}
toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('nav-open',open);});
nav.addEventListener('keydown',event=>{if(event.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){closeMenu();toggle.focus();}});
nav.append(toggle,items);document.body.prepend(nav);
if(!document.querySelector('link[rel="stylesheet"][href="shell.css"]')){const css=document.createElement('link');css.rel='stylesheet';css.href='shell.css';document.head.append(css);}
const skip=document.createElement('a');skip.className='skip-link';skip.href='#main-content';skip.textContent='Ir para o conteúdo';document.body.prepend(skip);
const main=document.querySelector('main');if(main){main.id='main-content';main.tabIndex=-1;}
