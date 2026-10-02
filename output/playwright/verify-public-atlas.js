async (page) => {
  const checks = [], errors = [], requests = [];
  const check = async (label, value) => { if (!value) throw new Error(label); checks.push(label); };
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => requests.push(request.url()));
  await page.route('http://atlas.test/**', async route => {
    const url = new URL(route.request().url());
    const path = url.pathname.replace(/^\/coracao-3d-estudos\//, '/');
    await route.fulfill({response: await route.fetch({url: 'http://127.0.0.1:8891' + path + url.search})});
  });
  const base = 'http://atlas.test/coracao-3d-estudos/';
  await page.setViewportSize({width:1440,height:1000});
  await page.goto(base + 'specimens.html');
  await page.locator('#photo-status').filter({hasText:'4 de 4'}).waitFor();
  await check('Hospedagem pública usa quatro fotos licenciadas', await page.locator('#photo-collection-select').inputValue() === 'public' && await page.locator('#photo-grid-circulatory .photo-card').count() === 2 && await page.locator('#photo-grid-respiratory .photo-card').count() === 2);
  await check('Acervo pessoal indisponível na hospedagem pública', await page.locator('#photo-collection-select option[value=personal]').evaluate(el=>el.disabled));
  await check('Nenhuma requisição aos originais ou manifesto pessoal', !requests.some(url => /\/assets\/cadaver\/|\/assets\/cadaver-gallery\.json/.test(url)));
  await check('Referências pessoais não entram nas orientações públicas', await page.locator('#observation-list a[href*="photo=circulatorio_"]').count() === 0);
  await page.locator('#photographs').scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>[...document.querySelectorAll('#photo-grid-circulatory img')].every(img=>img.complete&&img.naturalWidth>0));
  await page.screenshot({path:'output/playwright/atlas-publico-galeria.png'});
  await page.locator('#photo-grid-circulatory button').first().click();
  await page.waitForFunction(()=>document.querySelector('#photo-full').naturalWidth === 960);
  await check('Foto pública mostra autor, fonte e CC BY-SA', (await page.locator('#photo-license').textContent()).includes('Anatomist90') && await page.locator('#photo-license a[href="https://creativecommons.org/licenses/by-sa/3.0/"]').count() === 1);
  await page.locator('#photo-close').click();
  await page.setViewportSize({width:390,height:844});
  await page.locator('#photos-respiratory summary').click();
  await check('Galeria pública móvel sem overflow horizontal', await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#study-chat-toggle').click();
  await page.locator('#study-chat-mode').selectOption('public-ai');
  await check('LLM7 disponível sem chave no site estático', !await page.locator('#study-chat-mode option[value=public-ai]').evaluate(el=>el.disabled));
  await check('Groq não oferece rota inexistente no GitHub Pages', await page.locator('#study-chat-mode option[value=ai]').evaluate(el=>el.hidden));
  await page.locator('#study-chat-question').fill('Quais câmaras cardíacas a valva mitral separa?');
  await page.locator('#study-chat-send').click();
  // This is a REAL generation request, with only hash-verified public theory.
  await page.locator('.study-chat-message small').filter({hasText:'IA · LLM7'}).waitFor({timeout:45000});
  const answer = await page.locator('.study-chat-message.assistant').last().textContent();
  await check('Geração real no navegador identifica AE e VE e oferece fontes', /átrio esquerdo|\bAE\b/i.test(answer) && /ventrículo esquerdo|\bVE\b/i.test(answer) && await page.locator('.study-chat-message.assistant').last().locator('.study-chat-sources a').count()>0);
  await page.screenshot({path:'output/playwright/atlas-publico-chat-real-mobile.png'});
  await page.unroute('http://atlas.test/**');
  await page.goto('http://127.0.0.1:8891/specimens.html?collection=public');
  await page.locator('#photo-status').filter({hasText:'4 de 4'}).waitFor();
  await page.locator('#photo-collection-select').selectOption('personal');
  await page.locator('#photo-status').filter({hasText:'213 de 213'}).waitFor();
  await check('Instalação local preserva o acervo e permite trocar coleções', await page.locator('#photo-collection-select').inputValue()==='personal');
  await check('Nenhum erro JavaScript', errors.length===0);
  return {passed:checks.length,checks,errors,realAIAnswer:answer,provider:'LLM7',sourcePolicy:'verified-public-source-text-only'};
}
