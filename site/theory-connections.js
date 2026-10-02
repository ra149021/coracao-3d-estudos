/** Local links between teaching content, the route and available anatomy.
 * Associations describe the loaded catalogue, not anatomical validation.
 */
let connections = null;
const caches = new Map();
const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const node = (tag, className, value) => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (value !== undefined) element.textContent = value;
  return element;
};
const link = (label, href, className = '') => {
  const element = node('a', className, label);
  element.href = href;
  return element;
};
const statusLabels = { present: 'Peça associada', related: 'Contexto parcial', pending: 'Pendente' };
const sourceLabels = {
  roteiro: 'Roteiro', coracao: 'Slides de coração', respiratorio: 'Slides de respiratório',
  complementar: 'Roteiro complementar', roteiro_complementar: 'Roteiro complementar',
  vasos: 'Slides de vasos', linfatico: 'Slides de linfático', mediastino: 'Slides de mediastino'
};

async function readJSON(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Referência local indisponível: ${path}`);
  return response.json();
}

export async function loadTheoryConnections(system = 'circulatory') {
  const selectedSystem = system === 'respiratory' ? 'respiratory' : 'circulatory';
  if (!caches.has(selectedSystem)) {
    const respiratory = selectedSystem === 'respiratory';
    const root = respiratory ? 'assets/respiratory/' : 'assets/';
    const paths = [root + 'catalog.json', respiratory ? root + 'requirements.json' : 'auditoria/matriz_coracao.json', root + 'practice-evidence.json', 'assets/study-views.json', 'assets/specimens.json'];
    const pending = Promise.allSettled(paths.map(readJSON)).then(results => {
      // Without the catalogue and route it would be misleading to report statuses.
      for (const index of [0, 1]) if (results[index].status === 'rejected') throw results[index].reason;
      const [catalogue, route, evidence = {}, allViews = {}, specimenData = {}] = results.map(result => result.status === 'fulfilled' ? result.value : undefined);
      const parts = catalogue.parts.filter(part => part.id && part.label && part.triangles > 0);
      const requirements = Array.isArray(route.alvos) ? route.alvos : [];
      const views = (allViews[selectedSystem] || []).filter(view =>
        Array.isArray(view.partIds) && view.partIds.every(id => parts.some(part => part.id === id)) &&
        (!view.focusPartIds || (view.focusPartIds.length > 0 && view.focusPartIds.every(id => view.partIds.includes(id)))));
      const sources = new Map([...(route.sources || []), ...(evidence.sources || [])].map(source => [source.id, source.label || source.name || source.id]));
      const state = {
        system: selectedSystem, parts, requirements, views,
        specimens: Array.isArray(specimenData.models) ? specimenData.models : [],
        warnings: results.flatMap((result, index) => result.status === 'rejected' ? [paths[index]] : []),
        sources, byPart: new Map(parts.map(part => [part.id, part])),
        byRequirement: new Map(requirements.map(item => [String(item.id), item])),
        evidence: new Map((evidence.targets || []).map(target => [String(target.id), target]))
      };
      state.rows = new Map(requirements.map(item => [String(item.id), association(item, parts)]));
      return state;
    });
    caches.set(selectedSystem, pending);
    pending.catch(() => caches.delete(selectedSystem));
  }
  connections = await caches.get(selectedSystem);
  return connections;
}

function association(item, parts) {
  // Keep this criterion identical to the route in study.js, including partial meshes.
  const direct = parts.filter(part => String(part.requirement?.id) === String(item.id) || (part.requirementIds || []).map(String).includes(String(item.id)));
  const evidence = new Set(Array.isArray(item.z_evidencia) ? item.z_evidencia : []);
  const related = parts.filter(part => ((part.relatedRequirementIds || []).map(String).includes(String(item.id)) || [part.sourceName, ...(Array.isArray(part.sourceAliases) ? part.sourceAliases : [])].some(name => evidence.has(name))) && !direct.includes(part));
  const hasWholeAssociation = direct.some(part => part.correspondence !== 'partial');
  return { item, direct, related, status: hasWholeAssociation ? 'present' : direct.length || related.length ? 'related' : 'pending' };
}

function classroomHref(reference) {
  if (['roteiro', 'coracao', 'vasos', 'respiratorio', 'linfatico', 'mediastino'].includes(reference.source)) {
    const page = String(reference.page || '').match(/\d+/)?.[0] || '1';
    return `classroom.html?${new URLSearchParams({doc: reference.source, page})}`;
  }
  if (/^[CR][1-4]$/.test(reference.source)) {
    const time = String(reference.time || '').match(/\d{1,2}:\d{2}(?::\d{2})?/);
    const seconds = time ? time[0].split(':').reduce((value, number) => value * 60 + Number(number), 0) : 0;
    return `classroom.html?${new URLSearchParams({video: reference.source, t: String(seconds)})}`;
  }
  return null;
}

function sourceText(source, page, time) {
  const label = connections.sources.get(source) || sourceLabels[source] || source || 'Material de apoio';
  return `${label}${page ? ` · p. ${Array.isArray(page) ? page.join(', ') : page}` : ''}${time ? ` · ${time}` : ''}`;
}

function routeHref(id) {
  return `atlas.html?${new URLSearchParams({system: connections.system, mode: 'route', requirement: String(id)})}`;
}

function requirementsDetails(chapter) {
  const ids = [...new Set((chapter.requirementIds || []).map(String))];
  if (!ids.length) return null;
  const details = node('details', 'theory-requirements');
  details.append(node('summary', '', `Conferir os itens do roteiro desta unidade (${ids.length})`));
  details.append(node('p', 'inline-note', 'A situação descreve a associação com o catálogo local. Peça associada e contexto parcial exigem conferência de forma, posição e limites; não são validação anatômica.'));
  const list = node('ul', 'theory-requirement-list');
  for (const id of ids) {
    const row = connections.rows.get(id), item = row?.item;
    const entry = node('li', 'theory-requirement');
    entry.dataset.requirementId = id;
    entry.append(link(`${id} · ${item?.estrutura || 'Referência não localizada no roteiro'}`, routeHref(id), 'theory-requirement-link'));
    if (row) {
      entry.append(node('span', `theory-requirement-status ${row.status}`, statusLabels[row.status]));
      const source = {source: item.fonte, page: item.pagina};
      const href = classroomHref(source);
      entry.append(href ? link(sourceText(item.fonte, item.pagina), href, 'theory-requirement-source') : node('span', 'theory-requirement-source', sourceText(item.fonte, item.pagina)));
      const academic = connections.evidence.get(id);
      if (academic?.criterion) entry.append(node('p', 'theory-requirement-criterion', academic.criterion));
      const references = node('div', 'source-links');
      const seen = new Set(href ? [href] : []);
      for (const reference of [...(academic?.pages || []), ...(academic?.lecture || [])]) {
        const referenceHref = classroomHref(reference);
        if (referenceHref && !seen.has(referenceHref)) {
          seen.add(referenceHref);
          references.append(link(sourceText(reference.source, reference.page, reference.time), referenceHref));
        }
      }
      if (references.children.length) entry.append(references);
    }
    list.append(entry);
  }
  details.append(list);
  return details;
}

function relatedViews(chapter) {
  const requirements = new Set((chapter.requirementIds || []).map(String));
  const parts = new Set(chapter.partIds || []);
  return connections.views.filter(view => {
    const viewRequirements = new Set((view.requirementIds || []).map(String));
    if ([...viewRequirements].some(id => requirements.has(id))) return true;
    // A shared carrier such as the trachea must not connect every thoracic view.
    // A part is an anchor only if it is associated with that view's own targets.
    return view.partIds.some(id => {
      if (!parts.has(id)) return false;
      const part = connections.byPart.get(id);
      return [part?.requirement?.id, ...(part?.requirementIds || [])].some(requirement => requirement !== undefined && viewRequirements.has(String(requirement)));
    });
  });
}

function viewsSection(views, contextual = false) {
  if (!views.length) return null;
  const section = node('section', contextual ? 'theory-section-connections' : 'theory-views');
  section.append(node(contextual ? 'h3' : 'h2', '', contextual ? 'Observar esta relação no atlas' : 'Vistas para relacionar texto e modelo'));
  const list = node('div', 'theory-view-links');
  for (const view of views) {
    const card = node('div', 'theory-view-card');
    card.append(link(view.label, `atlas.html?${new URLSearchParams({system: connections.system, preset: view.id})}`, 'theory-view-link'));
    if (view.note) card.append(node('p', 'inline-note', view.note));
    if (view.source) {
      const reference = {source: view.source.document, page: view.source.page};
      const href = classroomHref(reference);
      if (href) card.append(link(sourceText(reference.source, reference.page), href, 'theory-view-source'));
    }
    list.append(card);
  }
  section.append(list);
  return section;
}

function sectionViews(chapter, section) {
  const available = relatedViews(chapter);
  const requirements = new Set((section.requirementIds || []).map(String));
  const refs = section.references || [];
  return available.filter(view =>
    (view.requirementIds || []).some(id => requirements.has(String(id))) ||
    refs.some(ref => ref.source === view.source?.document && String(ref.page) === String(view.source?.page)) ||
    (chapter.id === 'resp_12' && /duas pressoes/.test(normalize(section.heading)) && view.id === 'pleura_inspecao'));
}

function specimenSection(chapter, section) {
  if (connections.system !== 'circulatory') return null;
  const heading = normalize(section.heading);
  const assignments = [
    {chapter: 'circ-ventriculos', heading: /ventriculo direito/, model: 'umn-heart-188', observation: 0},
    {chapter: 'circ-ventriculos', heading: /papilares, cordas/, model: 'umn-heart-188', observation: 1},
    {chapter: 'circ-valvas', heading: /quatro valvas/, model: 'umn-heart-064', observation: 0},
    {chapter: 'circ-valvas', heading: /folhetos, seios/, model: 'umn-heart-188', observation: 2}
  ];
  const matches = assignments.filter(assignment => assignment.chapter === chapter.id && assignment.heading.test(heading));
  if (!matches.length) return null;
  const holder = node('section', 'theory-specimens');
  holder.append(node('h3', '', 'Comparar com uma peça humana'));
  for (const assignment of matches) {
    const model = connections.specimens.find(specimen => specimen.id === assignment.model);
    const observation = model?.observations?.[assignment.observation];
    if (!model || !observation) continue;
    const card = node('article', 'theory-specimen-card');
    card.dataset.model = model.id;
    card.append(link(`${model.code} · ${model.shortTitle || model.title}`, `specimens.html?${new URLSearchParams({model: model.id})}#institutional`, 'theory-specimen-link'), node('strong', 'theory-specimen-observation', observation.title), node('p', '', observation.text));
    const limits = node('ul', 'theory-specimen-limits');
    for (const limit of model.limits || []) limits.append(node('li', '', limit));
    card.append(limits, node('p', 'inline-note', 'Acervo externo da Universidade de Minnesota. A visualização é carregada somente na página da peça, mediante sua ação, e não amplia a cobertura do atlas local.'));
    holder.append(card);
  }
  return holder.querySelector('.theory-specimen-card') ? holder : null;
}

/** A fragment for a whole chapter, or contextual links after one lesson section. */
export function renderTheoryConnections(chapter, sectionIndex) {
  const fragment = document.createDocumentFragment();
  if (!connections || !chapter) return fragment;
  if (sectionIndex === undefined) {
    const requirements = requirementsDetails(chapter), views = viewsSection(relatedViews(chapter));
    if (requirements) fragment.append(requirements);
    if (views) fragment.append(views);
    const photoRegions = {
      'circ-orientacao': 'superficie', 'circ-parede': 'camaras', 'circ-pericardio': 'pericardio',
      'circ-atrios': 'camaras', 'circ-ventriculos': 'camaras', 'circ-valvas': 'valvas',
      'circ-coronarias': 'coronarias', 'circ-veias': 'coronarias', 'circ-grandes-vasos': 'grandes_vasos',
      'resp_02': 'nariz', 'resp_03': 'nariz', 'resp_04': 'faringe', 'resp_05': 'laringe',
      'resp_06': 'laringe', 'resp_07': 'traqueia', 'resp_08': 'traqueia', 'resp_09': 'pulmoes', 'resp_10': 'pleura'
    };
    if (photoRegions[chapter.id]) {
      const photos = node('section', 'theory-specimens');
      photos.append(node('h3', '', 'Compare com as fotografias da prática'),
        link('Abrir as peças desta região →', `specimens.html?${new URLSearchParams({system: connections.system, region: photoRegions[chapter.id]})}#photographs`, 'theory-specimen-link'),
        node('p', 'inline-note', 'Fotografias das coleções disponíveis nesta instalação. Consulte os rótulos originais, os créditos e as condições de cada imagem.'));
      fragment.append(photos);
    }
  } else {
    const section = chapter.sections?.[sectionIndex];
    if (!section) return fragment;
    const views = viewsSection(sectionViews(chapter, section), true), specimens = specimenSection(chapter, section);
    if (views) fragment.append(views);
    if (specimens) fragment.append(specimens);
  }
  return fragment;
}

/** Only bronchus B tokens are links; territory S tokens remain teaching text. */
export function renderLinkedCell(value, chapter, sectionIndex, columnIndex) {
  const text = String(value ?? '');
  if (!connections || connections.system !== 'respiratory' || chapter?.id !== 'resp_08') return document.createTextNode(text);
  const section = chapter.sections?.[sectionIndex];
  if (!section?.table || (columnIndex !== undefined && !/codigo|bronqu/i.test(normalize(section.table.headers?.[columnIndex])))) return document.createTextNode(text);
  const heading = normalize(section.heading);
  const side = heading.includes('esquerd') ? 'left' : heading.includes('direit') ? 'right' : null;
  if (!side) return document.createTextNode(text);
  const holder = node('span', 'theory-bronchus-code');
  const pattern = /\bB(\d+(?:\+\d+)?)\b/g;
  let start = 0, match;
  while ((match = pattern.exec(text))) {
    holder.append(document.createTextNode(text.slice(start, match.index)));
    const part = connections.parts.find(part => part.id.includes(`_of_${side}_lung_`) && part.id.includes('segmental_bronchus') && part.label.match(/\bB(\d+(?:\+\d+)?)\b/)?.[1] === match[1]);
    const view = part && connections.views.find(view => view.id.startsWith('arvore_') && view.partIds.includes(part.id));
    if (part && view) {
      const anchor = link(match[0], `atlas.html?${new URLSearchParams({system: 'respiratory', preset: view.id, part: part.id})}`, 'theory-bronchus-link');
      anchor.title = `${part.label} · ${view.label}. O volume segmentar S não está individualizado no atlas.`;
      holder.append(anchor);
    } else holder.append(document.createTextNode(match[0]));
    start = pattern.lastIndex;
  }
  holder.append(document.createTextNode(text.slice(start)));
  return holder;
}
