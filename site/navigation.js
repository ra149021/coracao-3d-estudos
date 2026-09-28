const path=location.pathname.split('/').pop() || 'index.html';
const nav=document.createElement('nav');
nav.className='global-nav';nav.setAttribute('aria-label','Navegação principal');
const links=[['index.html','Início'],['atlas.html','Coração 3D'],['atlas.html?system=respiratory','Respiratório 3D'],['theory.html','Teoria e revisão'],['classroom.html','Aulas e materiais']];
const brand=document.createElement('a');brand.className='global-brand';brand.href='./';brand.innerHTML='<span aria-hidden="true">✳</span> ATLAS <b>ESTUDO</b>';nav.append(brand);
const items=document.createElement('div');items.className='global-links';
for(const [url,label] of links){const a=document.createElement('a');a.href=url;a.textContent=label;const target=new URL(url,location.href);if(path===target.pathname.split('/').pop()&&(path!=='atlas.html'||(new URLSearchParams(location.search).get('system')==='respiratory')===(target.searchParams.get('system')==='respiratory')))a.setAttribute('aria-current','page');items.append(a);}
nav.append(items);document.body.prepend(nav);
const css=document.createElement('link');css.rel='stylesheet';css.href='shell.css';document.head.append(css);
const skip=document.createElement('a');skip.className='skip-link';skip.href='#main-content';skip.textContent='Ir para o conteúdo';document.body.prepend(skip);
const main=document.querySelector('main');if(main){main.id='main-content';main.tabIndex=-1;}
