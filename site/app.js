import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { initStudy } from './study.js';

const $ = (id) => document.getElementById(id);
const groups = {
  camaras: 'Câmaras cardíacas', grandes: 'Grandes vasos',
  coronarias: 'Artérias coronárias', veias: 'Veias cardíacas',
  valvas: 'Folhetos valvares', papilares: 'Músculos papilares',
  contexto: 'Vasos de contexto',
};
const escapeHTML = (text) => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const normalize = (text) => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const eye = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></svg>';
const eyeOff = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 3 18 18M9.4 6.3A12 12 0 0 1 12 6c6.5 0 10 6 10 6a18 18 0 0 1-4 4M6 7.8A18 18 0 0 0 2 12s3.5 6 10 6a12 12 0 0 0 4-.7"/></svg>';
const state = { selected: null, preset: 'exterior', labels: false, palette: 'tissue', transparency: 0, clipping: false, axis: 'z', cut: 50, flipped: false, ready: false, examMode: false };
const canvas = $('heart-canvas');
const viewer = $('viewer');
const meshes = new Map();
const labels = new Map();
const collapsedGroups = new Set();
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, 1, 0.01, 150);
const fullBounds = new THREE.Box3();
let renderer, controls, catalog, entries = [], moveAnimation = null;
let frameRequested = false, lastTime = 0, dragging = false, pointerStart = null;
const pickListeners = new Set();

function fail(error) {
  console.error(error);
  $('loading').hidden = true;
  $('viewer-error').hidden = false;
  $('error-message').textContent = error.message || 'A cena não carregou. Tente abrir novamente pelo iniciador local.';
  $('model-status').textContent = 'Cena indisponível';
}

function tissueColor(part) {
  if (part.group === 'contexto') return part.kind === 'veia' ? '#897b94' : '#bc8675';
  if (part.group === 'camaras') return '#a36661';
  if (part.group === 'valvas') return '#ddd0b5';
  if (part.group === 'papilares') return '#b47e6e';
  if (part.group === 'veias') return '#897b94';
  if (part.group === 'coronarias') return '#c2947f';
  if (part.sourceName.includes('vena cava')) return '#8f8193';
  if (part.sourceName.includes('pulmonary vein')) return '#bd8c80';
  if (part.sourceName.toLowerCase().includes('pulmonary')) return '#a28788';
  return '#b7786b';
}

function refreshMaterials() {
  for (const part of entries) {
    const mesh = meshes.get(part.id);
    const material = mesh.material;
    let opacity = part.group === 'camaras' ? Math.max(0.015, 1 - state.transparency / 100) : 1;
    if (state.selected && state.selected !== part.id) opacity = Math.min(opacity, 0.17);
    if (state.selected === part.id) opacity = 1;
    const transparent = opacity < 0.995;
    const clipping = state.clipping ? [clipPlane] : [];
    if (material.transparent !== transparent || material.clippingPlanes.length !== clipping.length) material.needsUpdate = true;
    material.transparent = transparent;
    material.opacity = opacity;
    material.depthWrite = !transparent;
    material.color.set(state.palette === 'didactic' ? part.color : tissueColor(part));
    material.emissive.set(state.selected === part.id ? '#713d18' : '#000000');
    material.emissiveIntensity = state.selected === part.id ? 0.27 : 0;
    material.clippingPlanes = clipping;
    mesh.renderOrder = transparent ? 1 : 0;
    if (state.selected === part.id) mesh.renderOrder = 2;
  }
  requestFrame();
}

function updateClipping() {
  const axis = state.axis;
  const sign = state.flipped ? 1 : -1;
  clipPlane.normal.set(axis === 'x' ? sign : 0, axis === 'y' ? sign : 0, axis === 'z' ? sign : 0);
  const min = fullBounds.min[axis] - 0.01;
  const max = fullBounds.max[axis] + 0.01;
  const position = min + (max - min) * (state.cut / 100);
  clipPlane.constant = -sign * position;
  $('cut-controls').hidden = !state.clipping;
  $('cut-badge').hidden = !state.clipping;
  $('cut-output').textContent = `${state.cut}%`;
  $('clipping').checked = state.clipping;
  $('cut-position').value = state.cut;
  $('cut-axis').value = state.axis;
  $('flip-cut').setAttribute('aria-pressed', String(state.flipped));
  refreshMaterials();
}

function syncVisibility() {
  const visible = entries.filter(p => meshes.get(p.id).visible).length;
  $('visible-count').textContent = `${visible} de ${entries.length} visíveis`;
  $('empty-scene').hidden = visible > 0;
  document.querySelectorAll('.structure-row').forEach(row => {
    const visible = meshes.get(row.dataset.id).visible;
    row.classList.toggle('is-hidden', !visible);
    row.classList.toggle('selected', row.dataset.id === state.selected);
    row.querySelector('.part-select').setAttribute('aria-pressed', String(row.dataset.id === state.selected));
    const button = row.querySelector('.visibility');
    const part = entries.find(p => p.id === row.dataset.id);
    button.innerHTML = visible ? eye : eyeOff;
    button.title = `${visible ? 'Ocultar' : 'Mostrar'} ${part.label}`;
    button.setAttribute('aria-label', button.title);
    button.setAttribute('aria-pressed', String(visible));
  });
  document.querySelectorAll('.group-toggle').forEach(button => {
    const allVisible = entries.filter(p => p.group === button.dataset.group).every(p => meshes.get(p.id).visible);
    button.textContent = allVisible ? 'Ocultar' : 'Mostrar';
    button.setAttribute('aria-label', `${allVisible ? 'Ocultar' : 'Mostrar'} ${groups[button.dataset.group]}`);
  });
  requestFrame();
}

function renderList() {
  const query = normalize($('search').value.trim());
  let html = '';
  for (const [group, name] of Object.entries(groups)) {
    const parts = entries.filter(p => p.group === group && normalize(`${p.label} ${p.sourceName} ${(p.aliases || []).join(' ')} ${name} ${p.requirement?.id || ''}`).includes(query));
    if (!parts.length) continue;
    const closed = !query && collapsedGroups.has(group);
    html += `<section class="structure-group"><div class="group-heading"><button class="group-name" data-group="${group}" aria-expanded="${!closed}">${closed ? '›' : '⌄'} ${name}<span>${parts.length}</span></button><button class="group-toggle" data-group="${group}">Ocultar</button></div><div ${closed ? 'hidden' : ''}>`;
    for (const part of parts) {
      html += `<div class="structure-row" data-id="${part.id}"><button class="part-select" title="${escapeHTML(part.label)}" aria-pressed="false"><span class="swatch" style="--swatch:${part.color}"></span><span class="part-name">${escapeHTML(part.label)}</span></button><button class="visibility"></button></div>`;
    }
    html += '</div></section>';
  }
  $('structure-list').innerHTML = html || '<div class="no-results"><strong>Nenhuma peça com este nome nesta cena.</strong><br>A auditoria registra outras estruturas do roteiro que ainda não foram integradas.</div>';
  syncVisibility();
}

function selectPart(id, scroll = false) {
  state.selected = id;
  $('selection-empty').hidden = !!id;
  $('selection-detail').hidden = !id;
  $('clear-selection').hidden = !id;
  if (id) {
    const part = entries.find(p => p.id === id);
    meshes.get(id).visible = true;
    $('selection-category').textContent = groups[part.group];
    $('selection-title').textContent = part.label;
    $('selection-description').textContent = part.note;
    $('selection-source').textContent = `${part.sourceName} · ${part.sourceFile} · ${part.source} / ${part.license}. Identificação do arquivo; revisão anatômica integral pendente.`;
    const ref = part.requirement;
    $('selection-requirement').textContent = ref ? `${ref.source === 'roteiro' ? 'Roteiro' : 'Slides'} · item ${ref.id} · página ${ref.page}` : 'Peça complementar da fonte';
    if (scroll) {
      collapsedGroups.delete(part.group);
      renderList();
      document.querySelector(`[data-id="${id}"]`)?.scrollIntoView({block: 'nearest', behavior: 'smooth'});
    }
  }
  refreshMaterials();
  syncVisibility();
}

function currentBounds(predicate = () => true) {
  const bounds = new THREE.Box3();
  for (const part of entries) if (meshes.get(part.id).visible && predicate(part)) bounds.union(meshes.get(part.id).geometry.boundingBox);
  return bounds.isEmpty() ? fullBounds.clone() : bounds;
}

function cameraTo(bounds, direction = null, animate = true) {
  const center = bounds.getCenter(new THREE.Vector3());
  const radius = Math.max(bounds.getBoundingSphere(new THREE.Sphere()).radius, 0.09);
  const fov = Math.min(camera.fov * Math.PI / 180, 2 * Math.atan(Math.tan(camera.fov * Math.PI / 360) * camera.aspect));
  const distance = radius / Math.sin(fov / 2) * 1.09;
  const vector = direction ? new THREE.Vector3(...direction) : camera.position.clone().sub(controls.target).normalize();
  vector.normalize();
  const dest = center.clone().addScaledVector(vector, distance);
  moveAnimation = animate && !matchMedia('(prefers-reduced-motion: reduce)').matches ? { start: performance.now(), from: camera.position.clone(), to: dest, targetFrom: controls.target.clone(), targetTo: center } : null;
  if (!moveAnimation) {
    controls.target.copy(center);
    camera.position.copy(dest);
    controls.update();
  }
  requestFrame();
}

function stopAutoRotate() {
  controls.autoRotate = false;
  $('rotate').setAttribute('aria-pressed', 'false');
}

function activeView(name=null) {
  document.querySelectorAll('[data-view]').forEach(button=>{
    const active=button.dataset.view===name;
    button.classList.toggle('active',active);
    button.setAttribute('aria-pressed',String(active));
  });
}

function preset(name, animate = true) {
  state.preset = name;
  state.selected = null;
  selectPart(null);
  state.transparency = name === 'coronarias' ? 72 : 0;
  state.clipping = name === 'interior';
  state.axis = 'z'; state.cut = 54; state.flipped = false;
  for (const part of entries) {
    const visible = name === 'valvas' ? ['valvas', 'papilares'].includes(part.group)
      : name === 'coronarias' ? ['camaras', 'coronarias', 'veias'].includes(part.group)
      : name === 'interior' ? ['camaras', 'valvas', 'papilares'].includes(part.group)
      : name === 'contexto' ? ['camaras', 'grandes', 'contexto'].includes(part.group)
      : part.defaultVisible !== false;
    meshes.get(part.id).visible = visible;
  }
  document.querySelectorAll('[data-preset]').forEach(button => {
    button.classList.toggle('active', button.dataset.preset === name);
    button.setAttribute('aria-pressed', String(button.dataset.preset === name));
  });
  $('mode-note').textContent = name === 'valvas' ? 'Folhetos disponíveis · inserções das cordas em revisão'
    : name === 'coronarias' ? 'Paredes transparentes para observar os vasos'
    : name === 'interior' ? 'Corte visual · detalhes internos simplificados'
    : name === 'contexto' ? 'Vasos do roteiro · contexto cervical, torácico e abdominal'
    : 'Geometria original · cores ilustrativas';
  $('transparency').value = state.transparency;
  $('transparency-output').textContent = `${state.transparency}%`;
  updateClipping();
  syncVisibility();
  stopAutoRotate();
  $('view-name').textContent = name === 'valvas' ? 'Valvas · vista oblíqua' : 'Vista anterior oblíqua';
  activeView();
  cameraTo(currentBounds(), name === 'valvas' ? [0.45, 0.65, 1] : [0.26, 0.12, 1], animate);
}

function reset() {
  $('search').value = '';
  state.palette = 'tissue'; $('palette').value = 'tissue';
  state.labels = false; $('labels').setAttribute('aria-pressed', 'false');
  preset('exterior');
  renderList();
}

function requestFrame() {
  if (!renderer || frameRequested) return;
  frameRequested = true;
  requestAnimationFrame(render);
}

function render(now) {
  frameRequested = false;
  const delta = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  if (moveAnimation) {
    const t = Math.min((now - moveAnimation.start) / 450, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    camera.position.lerpVectors(moveAnimation.from, moveAnimation.to, ease);
    controls.target.lerpVectors(moveAnimation.targetFrom, moveAnimation.targetTo, ease);
    if (t === 1) moveAnimation = null;
  }
  controls.update(delta);
  renderer.render(scene, camera);
  updateLabels();
  drawCompass();
  if (moveAnimation || controls.autoRotate) requestFrame();
}

function updateLabels() {
  for (const [id, label] of labels) {
    const mesh = meshes.get(id);
    const center = mesh.geometry.boundingBox.getCenter(new THREE.Vector3());
    const visible = state.labels && mesh.visible && (!state.clipping || clipPlane.distanceToPoint(center) >= 0);
    label.hidden = !visible;
    if (!visible) continue;
    const projected = center.clone().project(camera);
    label.hidden = projected.z < -1 || projected.z > 1 || Math.abs(projected.x) > 1 || Math.abs(projected.y) > 1;
    // Label chamber centroids; no claim that the label marks an independently segmented substructure.
    label.style.left = `${(projected.x * .5 + .5) * viewer.clientWidth}px`;
    label.style.top = `${(-projected.y * .5 + .5) * viewer.clientHeight}px`;
  }
}

function drawCompass() {
  const c = $('compass');
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, c.width, c.height);
  const q = camera.quaternion.clone().invert();
  const axes = [
    [[1,0,0], 'E', '#9b716a'], [[-1,0,0], 'D', '#9b716a'],
    [[0,1,0], 'S', '#81956f'], [[0,-1,0], 'I', '#81956f'],
    [[0,0,1], 'A', '#788da0'], [[0,0,-1], 'P', '#788da0'],
  ].map(([xyz, label, color]) => ({v:new THREE.Vector3(...xyz).applyQuaternion(q), label, color})).sort((a,b)=>a.v.z-b.v.z);
  for (const {v,label,color} of axes) {
    const x = 110 + v.x * 69, y = 104 - v.y * 69;
    ctx.globalAlpha = v.z < -.1 ? .38 : .95;
    ctx.beginPath(); ctx.moveTo(110,104); ctx.lineTo(x,y); ctx.strokeStyle=color; ctx.lineWidth=2; ctx.stroke();
    ctx.beginPath(); ctx.arc(x,y,16,0,2*Math.PI); ctx.fillStyle='#f9f7ef'; ctx.fill();
    ctx.strokeStyle=color; ctx.lineWidth=1; ctx.stroke();
    ctx.fillStyle=color; ctx.font='600 18px system-ui'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(label,x,y+.5);
  }
  ctx.globalAlpha = 1;
}

function hitsAt(event) {
  if (!state.ready) return [];
  const rect = canvas.getBoundingClientRect();
  pointer.set((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const candidates = [...meshes.values()].filter(m => m.visible && m.material.opacity > .045);
  return raycaster.intersectObjects(candidates, false).filter(hit => !state.clipping || clipPlane.distanceToPoint(hit.point) >= -1e-6);
}

function attachEvents() {
  $('structure-list').addEventListener('click', event => {
    const groupToggle = event.target.closest('.group-toggle');
    if (groupToggle) {
      const parts = entries.filter(p => p.group === groupToggle.dataset.group);
      const visible = !parts.every(p => meshes.get(p.id).visible);
      parts.forEach(p => {meshes.get(p.id).visible = visible;});
      if (!visible && parts.some(p => p.id === state.selected)) selectPart(null);
      syncVisibility(); return;
    }
    const groupName = event.target.closest('.group-name');
    if (groupName) {
      const group = groupName.dataset.group;
      if (collapsedGroups.has(group)) collapsedGroups.delete(group); else collapsedGroups.add(group);
      renderList(); return;
    }
    const row = event.target.closest('.structure-row');
    if (!row) return;
    if (event.target.closest('.visibility')) {
      const mesh = meshes.get(row.dataset.id);
      mesh.visible = !mesh.visible;
      if (!mesh.visible && state.selected === row.dataset.id) selectPart(null);
      syncVisibility();
    } else selectPart(state.selected === row.dataset.id ? null : row.dataset.id);
  });
  $('search').addEventListener('input', renderList);
  $('show-all').addEventListener('click', () => {entries.forEach(p => meshes.get(p.id).visible = true); selectPart(null); syncVisibility(); cameraTo(currentBounds());});
  $('clear-selection').addEventListener('click', () => selectPart(null));
  $('focus-part').addEventListener('click', () => {if (state.selected) cameraTo(meshes.get(state.selected).geometry.boundingBox);});
  $('isolate-part').addEventListener('click', () => {
    if (!state.selected) return;
    entries.forEach(p => meshes.get(p.id).visible = p.id === state.selected);
    state.clipping = false; updateClipping(); syncVisibility();
    cameraTo(currentBounds());
  });
  $('hide-part').addEventListener('click', () => {if (state.selected) meshes.get(state.selected).visible = false; selectPart(null);});
  document.querySelectorAll('[data-preset]').forEach(b => b.addEventListener('click', () => preset(b.dataset.preset)));
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
    const view = button.dataset.view;
    const directions = { anterior:[0,0,1], posterior:[0,0,-1], direita:[-1,0,0], esquerda:[1,0,0], superior:[0,1,0.001] };
    stopAutoRotate();
    $('view-name').textContent = `Vista ${view}`;
    activeView(view);
    cameraTo(currentBounds(), directions[view]);
  }));
  $('reset').addEventListener('click', reset);
  $('empty-reset').addEventListener('click', reset);
  $('palette').addEventListener('change', event => {state.palette = event.target.value; refreshMaterials();});
  $('transparency').addEventListener('input', event => {state.transparency = Number(event.target.value); $('transparency-output').textContent=`${state.transparency}%`; refreshMaterials();});
  $('clipping').addEventListener('change', event => {state.clipping=event.target.checked; updateClipping();});
  $('cut-axis').addEventListener('change', event => {state.axis=event.target.value; updateClipping();});
  $('cut-position').addEventListener('input', event => {state.cut=Number(event.target.value); updateClipping();});
  $('flip-cut').addEventListener('click', () => {state.flipped=!state.flipped; updateClipping();});
  $('rotate').addEventListener('click', () => {
    controls.autoRotate = !controls.autoRotate;
    $('rotate').setAttribute('aria-pressed', String(controls.autoRotate));
    if (controls.autoRotate) { $('view-name').textContent='Exploração em rotação'; activeView(); }
    requestFrame();
  });
  $('labels').addEventListener('click', () => {state.labels=!state.labels; $('labels').setAttribute('aria-pressed', String(state.labels)); requestFrame();});
  $('fullscreen').addEventListener('click', async () => {
    try {if (document.fullscreenElement) await document.exitFullscreen(); else await viewer.requestFullscreen();}
    catch (error) { $('mode-note').textContent='Tela cheia indisponível neste navegador.'; }
  });
  canvas.addEventListener('pointerdown', event => {pointerStart={x:event.clientX,y:event.clientY,button:event.button}; dragging=false; $('hover-label').hidden=true;});
  canvas.addEventListener('pointermove', event => {
    if (pointerStart && Math.hypot(event.clientX-pointerStart.x,event.clientY-pointerStart.y)>5) dragging=true;
    if (dragging || event.buttons || state.examMode) { $('hover-label').hidden=true; return; }
    const hit = hitsAt(event)[0];
    $('hover-label').hidden = !hit;
    if (hit) {
      $('hover-label').textContent = hit.object.userData.part.label;
      const rect = viewer.getBoundingClientRect();
      $('hover-label').style.left = `${Math.max(8,Math.min(event.clientX-rect.left+14,rect.width-230))}px`;
      $('hover-label').style.top = `${Math.max(10,Math.min(event.clientY-rect.top+14,rect.height-55))}px`;
    }
  });
  canvas.addEventListener('pointerup', event => {
    if (pointerStart?.button === 0 && !dragging) {
      const hit = hitsAt(event)[0];
      const id = hit?.object.userData.part.id || null;
      if (!state.examMode) selectPart(id, false);
      if (id) for (const callback of pickListeners) callback(id);
    }
    pointerStart=null; dragging=false;
  });
  canvas.addEventListener('pointercancel', () => {pointerStart=null; dragging=false;});
  canvas.addEventListener('pointerleave', () => { $('hover-label').hidden=true; });
  canvas.addEventListener('keydown', event => {
    if (event.key === 'Escape') {if (!state.examMode) selectPart(null); return;}
    const angle = Math.PI / 24;
    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','_'].includes(event.key)) {
      event.preventDefault(); moveAnimation=null; stopAutoRotate();
      if (event.key==='ArrowLeft') controls.rotateLeft(angle);
      if (event.key==='ArrowRight') controls.rotateLeft(-angle);
      if (event.key==='ArrowUp') controls.rotateUp(angle);
      if (event.key==='ArrowDown') controls.rotateUp(-angle);
      if (['+','='].includes(event.key)) controls.dollyIn(1.12);
      if (['-','_'].includes(event.key)) controls.dollyOut(1.12);
      controls.update(); $('view-name').textContent='Ângulo livre'; activeView(); requestFrame();
    }
  });
  canvas.addEventListener('webglcontextlost', event => {event.preventDefault(); fail(new Error('O navegador perdeu o acesso à placa gráfica. Recarregue a página para restaurar a cena.'));});
}

function initAbout() {
  for (const id of ['about-open','sources-link','limits-link']) $(id).addEventListener('click', () => $('about').showModal());
  $('about-close').addEventListener('click', () => $('about').close());
  $('about').addEventListener('click', event => {if (event.target === $('about')) {const r = $('about').getBoundingClientRect(); if (event.clientX<r.left || event.clientX>r.right || event.clientY<r.top || event.clientY>r.bottom) $('about').close();}});
  $('retry').addEventListener('click', () => location.reload());
}

async function init() {
  initAbout();
  if (location.protocol === 'file:') return;
  try {
    renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true, powerPreference:'high-performance'});
  } catch {
    throw new Error('WebGL 2 não está disponível. Abra em um navegador com aceleração gráfica para explorar o modelo.');
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.13;
  renderer.localClippingEnabled = true;
  scene.add(new THREE.HemisphereLight('#fff8ec','#8a8e86',2.15));
  const key = new THREE.DirectionalLight('#fff5e6',3.4); key.position.set(-4,7,7); scene.add(key);
  const fill = new THREE.DirectionalLight('#e2efff',1.6); fill.position.set(6,1,3); scene.add(fill);
  const rim = new THREE.DirectionalLight('#ffe1ca',2.2); rim.position.set(1,5,-6); scene.add(rim);
  controls = new OrbitControls(camera,canvas);
  controls.enableDamping = true; controls.dampingFactor=.1; controls.rotateSpeed=.7; controls.zoomSpeed=.9;
  controls.minDistance=.18; controls.maxDistance=55; controls.autoRotateSpeed=.6;
  camera.position.set(3,2,12);
  controls.addEventListener('change',requestFrame);
  controls.addEventListener('start',() => {moveAnimation=null; stopAutoRotate(); $('view-name').textContent='Ângulo livre'; activeView();});
  const resize = () => {
    const w=viewer.clientWidth,h=viewer.clientHeight;
    renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); requestFrame();
  };
  new ResizeObserver(resize).observe(viewer); resize();
  const response = await fetch('assets/catalog.json');
  if (!response.ok) throw new Error('O catálogo local não foi encontrado. Reabra pelo iniciador do projeto.');
  catalog = await response.json(); entries = catalog.parts;
  $('limitations-list').innerHTML = catalog.limitations.map(t=>`<li>${escapeHTML(t)}</li>`).join('');
  $('sources-list').innerHTML = catalog.sources.map(s=>`<li><a href="${escapeHTML(s.url)}" target="_blank" rel="noopener">${escapeHTML(s.label)}</a></li>`).join('');
  const gltf = await new GLTFLoader().loadAsync('assets/heart.glb', event => {if(event.total) $('loading-progress').textContent=`Carregando peças locais · ${Math.round(event.loaded/event.total*100)}%`;});
  gltf.scene.traverse(object=> {
    if (!object.isMesh) return;
    const part=entries.find(p=>p.id===object.userData.partId || p.id===object.name);
    if (!part) throw new Error(`Peça sem identificação: ${object.name}`);
    object.material=new THREE.MeshPhysicalMaterial({color:tissueColor(part),roughness:.55,metalness:0,clearcoat:.12,clearcoatRoughness:.48,side:THREE.DoubleSide,clippingPlanes:[],depthWrite:true});
    object.userData.part=part;
    object.geometry.computeBoundingBox(); object.geometry.computeBoundingSphere();
    if(part.defaultVisible !== false)fullBounds.union(object.geometry.boundingBox);
    meshes.set(part.id,object);
    if(part.group==='camaras') {
      const label=document.createElement('span'); label.className='mesh-label';label.textContent=part.label;label.hidden=true;
      $('labels-layer').appendChild(label); labels.set(part.id,label);
    }
  });
  if (meshes.size!==entries.length) throw new Error('A cena não carregou todas as peças do catálogo.');
  scene.add(gltf.scene);
  $('part-count').textContent=entries.length;
  document.querySelectorAll('[data-part-count]').forEach(node=>node.textContent=entries.length);
  $('model-status').textContent=`${entries.length} peças · 3D local · sem CDN`;
  $('loading').hidden=true; state.ready=true;
  renderList(); attachEvents(); preset('exterior',false);
  // Local study controls and rendering diagnostics; no data is sent externally.
  const snapshot = ()=>({
    ready:state.ready, parts:meshes.size, visible:entries.filter(p=>meshes.get(p.id).visible).length,
    selected:state.selected, preset:state.preset, camera:camera.position.toArray(),target:controls.target.toArray(),
    clipping:state.clipping,axis:state.axis,cut:state.cut,flipped:state.flipped,transparency:state.transparency,
    autoRotate:controls.autoRotate,labels:state.labels,palette:state.palette,
    drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,
    modelBytes:catalog.model.bytes,gl:renderer.getContext().getParameter(renderer.getContext().VERSION),
    visibleParts:entries.filter(p=>meshes.get(p.id).visible).map(p=>p.id),
    viewName:$('view-name').textContent, modeNote:$('mode-note').textContent,examMode:state.examMode,
    activeView:document.querySelector('[data-view].active')?.dataset.view || null,
  });
  const viewerAPI = Object.freeze({
    snapshot,
    select:id=>{if(meshes.has(id))selectPart(id);},
    clear:()=>selectPart(null),
    show:ids=>{
      const visible=new Set(ids);
      entries.forEach(p=>meshes.get(p.id).visible=visible.has(p.id));
      if(state.selected&&!visible.has(state.selected))selectPart(null);
      syncVisibility();
    },
    showAll:()=>{entries.forEach(p=>meshes.get(p.id).visible=true);syncVisibility();},
    showContext:()=>preset('contexto',false),
    showHeart:()=>preset('exterior',false),
    isolate:id=>{if(!meshes.has(id))return;entries.forEach(p=>meshes.get(p.id).visible=p.id===id);selectPart(id);syncVisibility();},
    view:name=>{
      const direction={anterior:[0,0,1],posterior:[0,0,-1],direita:[-1,0,0],esquerda:[1,0,0],superior:[0,1,.001]}[name];
      if(direction){stopAutoRotate();cameraTo(currentBounds(),direction,false);$('view-name').textContent=`Vista ${name}`;activeView(name);}
    },
    focus:id=>{if(meshes.has(id))cameraTo(meshes.get(id).geometry.boundingBox);},
    labels:enabled=>{state.labels=Boolean(enabled);$('labels').setAttribute('aria-pressed',String(state.labels));requestFrame();},
    setExamMode:enabled=>{
      state.examMode=Boolean(enabled);
      document.body.classList.toggle('exam-mode',state.examMode);
      document.querySelector('.structures').inert=state.examMode;
      document.querySelector('.inspector').inert=state.examMode;
      document.querySelector('.presets').inert=state.examMode;
      $('fullscreen').disabled=state.examMode;
      $('reset').disabled=state.examMode;
      if(state.examMode){
        state.clipping=false;state.transparency=0;state.labels=false;
        $('mode-note').textContent='Treino de identificação · gire para observar as relações';
        stopAutoRotate();$('hover-label').hidden=true;updateClipping();
        if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});
      }
      requestFrame();
    },
    onPick:callback=>{pickListeners.add(callback);return()=>pickListeners.delete(callback);},
    restore:s=>{
      if(!s)return;
      moveAnimation=null;
      const visible=new Set(s.visibleParts || entries.map(p=>p.id));
      entries.forEach(p=>meshes.get(p.id).visible=visible.has(p.id));
      for(const key of ['preset','palette','transparency','axis','cut','flipped','clipping','labels']) if(s[key]!==undefined)state[key]=s[key];
      $('palette').value=state.palette;
      $('transparency').value=state.transparency;
      $('transparency-output').textContent=`${state.transparency}%`;
      $('labels').setAttribute('aria-pressed',String(state.labels));
      document.querySelectorAll('[data-preset]').forEach(b=>{b.classList.toggle('active',b.dataset.preset===state.preset);b.setAttribute('aria-pressed',String(b.dataset.preset===state.preset));});
      updateClipping();selectPart(meshes.has(s.selected)?s.selected:null);syncVisibility();
      controls.target.fromArray(s.target);camera.position.fromArray(s.camera);controls.update();
      controls.autoRotate=Boolean(s.autoRotate);$('rotate').setAttribute('aria-pressed',String(controls.autoRotate));
      $('view-name').textContent=s.viewName || 'Ângulo livre';$('mode-note').textContent=s.modeNote || 'Geometria original · cores ilustrativas';requestFrame();
      activeView(s.activeView);
    },
  });
  window.heartViewer=viewerAPI;
  try {
    const requirementsResponse=await fetch('auditoria/matriz_coracao.json');
    if(!requirementsResponse.ok)throw new Error('Não foi possível ler a matriz do roteiro.');
    const requirements=await requirementsResponse.json();
    let evidence=null;
    try {
      const evidenceResponse=await fetch('assets/practice-evidence.json');
      if(evidenceResponse.ok)evidence=await evidenceResponse.json();
    } catch(error) { console.warn('Referências de aula indisponíveis nesta abertura.',error); }
    initStudy({parts:entries,requirements:requirements.alvos,viewer:viewerAPI,evidence});
  } catch(error) {
    console.error(error);
    $('model-status').textContent='Cena pronta; módulo de prática indisponível. Recarregue a página.';
  }
}

init().catch(fail);
