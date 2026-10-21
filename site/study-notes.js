// Personal writing stays separate from reading/review progress.
// Keep failed patches alive when a workspace recreates a system's renderer.
const workspaces = new Map();
window.addEventListener('beforeunload', event => {
  if (![...workspaces.values()].some(workspace => workspace.hasPending())) return;
  event.preventDefault();
  event.returnValue = '';
});
export function createStudyNotes(system) {
  if (workspaces.has(system)) return workspaces.get(system).render;
  const key = `atlas:notes:${system}`;
  let notes = {}, unavailable = false;
  const pending = {};
  const record = value => value && typeof value === 'object' && !Array.isArray(value);
  const refresh = () => {
    let saved;
    try {
      saved = JSON.parse(localStorage.getItem(key) || '{}');
      if (!record(saved)) throw new Error('Invalid notes record');
    } catch {
      unavailable = true;
      return false;
    }
    notes = {...saved};
    for (const [id, patch] of Object.entries(pending)) {
      notes[id] = {...(record(saved[id]) ? saved[id] : {}), ...patch};
    }
    unavailable = Object.keys(pending).length > 0;
    return true;
  };
  refresh();
  const render = chapter => {
    refresh();
    const box = document.createElement('details');
    box.id = 'study-notes-box';
    box.className = 'study-notes-box';
    const summary = document.createElement('summary');
    summary.textContent = 'Minhas anotações desta unidade';
    const label = document.createElement('label');
    label.htmlFor = 'study-notes';
    label.textContent = 'Minhas dúvidas e explicações';
    const field = document.createElement('textarea');
    field.id = 'study-notes';
    field.rows = 7;
    field.value = notes[chapter.id]?.text || '';
    box.open = Boolean(field.value);
    const status = document.createElement('p');
    status.id = 'study-notes-status';
    status.className = 'inline-note';
    status.setAttribute('role', 'status');
    field.setAttribute('aria-describedby', status.id);
    const report = () => {
      status.textContent = unavailable
        ? 'Não foi possível salvar neste navegador. As anotações ficam somente nesta sessão desta página; recarregar, fechar ou mudar de sistema pode apagá-las. Baixe uma cópia antes de sair.'
        : 'Anotações salvas somente neste navegador, sem envio. Baixe uma cópia para guardar fora dele.';
    };
    report();
    field.addEventListener('input', () => {
      pending[chapter.id] = {title: chapter.title, text: field.value};
      notes[chapter.id] = {...notes[chapter.id], ...pending[chapter.id]};
      // Never replace a record we could not read; retry only the edited fields.
      if (refresh()) {
        try {
          localStorage.setItem(key, JSON.stringify(notes));
          for (const id of Object.keys(pending)) delete pending[id];
          unavailable = false;
        } catch { unavailable = true; }
      }
      report();
    });
    const download = document.createElement('button');
    download.type = 'button';
    download.className = 'action';
    download.textContent = 'Baixar minhas anotações';
    download.addEventListener('click', () => {
      const heading = `Minhas anotações — ${system === 'respiratory' ? 'Respiratório' : 'Circulatório'}`;
      refresh();
      report();
      const entries = Object.entries(notes).filter(([, value]) => typeof value?.text === 'string' && value.text.trim());
      const text = heading + '\n\n' + (entries.map(([id, value]) => `${value.title || id}\n${value.text}`).join('\n\n---\n\n') || 'Nenhuma anotação escrita neste sistema.');
      const url = URL.createObjectURL(new Blob([text + '\n'], {type: 'text/plain;charset=utf-8'}));
      const link = document.createElement('a');
      link.href = url;
      link.download = `anotacoes-${system}.txt`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    box.append(summary, label, field, status, download);
    return box;
  };
  workspaces.set(system, {render, hasPending: () => Object.keys(pending).length > 0});
  return render;
}
