async (page) => {
  const checks = [];
  const check = (name, ok) => { if (!ok) throw new Error(name); checks.push(name); };
  const base = 'http://127.0.0.1:8891/';
  const index = await (await page.request.get(base+'assets/study-chat-index.json')).json();
  await page.addInitScript(() => {
    window.__chatTimers = [];
    const original = window.setTimeout;
    window.setTimeout = (callback, delay, ...args) => {
      if (delay === 40000) { window.__chatTimers.push(callback); return original(()=>{},120000); }
      return original(callback,delay,...args);
    };
  });
  let release;
  const gate = new Promise(resolve=>{release=resolve;});
  await page.route('**/assets/study-chat-index.json', async route => { await gate; try { await route.fulfill({json:index}); } catch {} });
  await page.goto(base+'specimens.html?collection=public');
  await page.locator('#study-chat-toggle').click();
  await page.locator('#study-chat-question').fill('O que é a valva mitral?');
  await page.locator('#study-chat-send').click();
  await page.waitForFunction(()=>window.__chatTimers.length===1);
  await page.evaluate(()=>window.__chatTimers[0]());
  await page.waitForFunction(()=>!document.querySelector('#study-chat-send').disabled);
  check('Timeout enquanto índice está retido libera Enviar e explica indisponibilidade', (await page.locator('#study-chat-messages').textContent()).includes('indisponível'));
  release(); await page.unroute('**/assets/study-chat-index.json');
  let releaseSecond;
  const secondGate = new Promise(resolve=>{releaseSecond=resolve;});
  await page.route('**/assets/study-chat-index.json', async route=>{await secondGate;try{await route.fulfill({json:index});}catch{}});
  let requests = 0;
  await page.route('https://api.llm7.io/v1/chat/completions', async route=>{
    requests++;
    await route.fulfill({json:{model:'simulated-cancellation-check',choices:[{message:{content:'A segunda pergunta foi respondida com fontes [1].'}}]}});
  });
  await page.goto(base+'specimens.html?collection=public');
  await page.locator('#study-chat-toggle').click();
  await page.locator('#study-chat-mode').selectOption('public-ai');
  await page.locator('#study-chat-question').fill('Primeira pergunta sobre valva mitral');
  await page.locator('#study-chat-send').click();
  await page.waitForFunction(()=>window.__chatTimers.length===1);
  await page.locator('#study-chat-clear').click();
  await page.locator('#study-chat-question').fill('Segunda pergunta sobre valva mitral');
  await page.locator('#study-chat-send').click();
  await page.waitForFunction(()=>window.__chatTimers.length===2);
  // Force the old timeout callback after clearing to exercise controller isolation.
  await page.evaluate(()=>window.__chatTimers[0]());
  releaseSecond();
  await page.locator('.study-chat-message.assistant').filter({hasText:'A segunda pergunta foi respondida'}).waitFor();
  check('Cancelamento e callback antigo não abortam a nova pergunta', requests===1);
  check('Primeira conversa limpa não reaparece', !/Primeira pergunta/.test(await page.locator('#study-chat-messages').textContent()));
  check('Nova resposta libera Enviar', !await page.locator('#study-chat-send').isDisabled());
  await page.unroute('**/assets/study-chat-index.json');
  await page.unroute('https://api.llm7.io/v1/chat/completions');
  return {passed:checks.length,checks,providerResponses:'simulated',timeout:'controlled callback; no real 40-second wait'};
}
