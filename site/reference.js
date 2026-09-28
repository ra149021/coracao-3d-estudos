import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const $ = id => document.getElementById(id);
const SOURCE = 'https://www.vhlab.umn.edu/atlas/echocardiography-tutorial/exam-views-models.shtml';
const ASSET_ROOT = './assets/local-references/';
const formatter = new Intl.NumberFormat('pt-BR');
const canvas = $('reference-canvas');
const viewport = $('viewport');
let renderer, scene, camera, controls, catalog;
let selected = null;
let dirty = true;
let loaded = false;
let initialDirection = new THREE.Vector3(.65, .48, 1).normalize();
const meshes = new Map();
const colors = [0xb97b70, 0xc99474, 0xa56c69, 0xccaa83];

function showError(kind) {
  $('loading').hidden = true;
  $('error').hidden = false;
  $('geometry-status').textContent = 'Referência indisponível';
  $('cuts').replaceChildren();
  const message = document.createElement('p');
  message.className = 'muted';
  message.textContent = 'O atlas principal continua disponível.';
  $('cuts').append(message);
  if (kind === 'webgl') {
    $('error-title').textContent = 'Não foi possível abrir o 3D';
    $('error-message').textContent = 'Seu navegador não conseguiu iniciar a visualização. Você pode voltar ao atlas ou consultar o material na fonte oficial.';
  } else if (kind === 'invalid') {
    $('error-title').textContent = 'O arquivo local não pôde ser aberto';
    $('error-message').textContent = 'A referência pode estar incompleta. Consulte o material original da Universidade de Minnesota para obtê-la novamente.';
  }
}

function prepareScene() {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(35, 1, .01, 100);
  camera.position.set(5, 4, 8);
  controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = .1;
  controls.autoRotateSpeed = .8;
  controls.minDistance = .12;
  controls.maxDistance = 40;
  controls.addEventListener('change', () => { dirty = true; });
  scene.add(new THREE.HemisphereLight(0xffffff, 0x81766b, 2.2));
  const key = new THREE.DirectionalLight(0xfff2dd, 3.0);
  key.position.set(-5, 8, 7);
  const fill = new THREE.DirectionalLight(0xe0ecf6, 1.8);
  fill.position.set(6, 2, -4);
  const lower = new THREE.DirectionalLight(0xf6dfcc, .7);
  lower.position.set(2, -6, 5);
  scene.add(key, fill, lower);
  const resize = () => {
    const width = viewport.clientWidth;
    const height = viewport.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    dirty = true;
  };
  new ResizeObserver(resize).observe(viewport);
  resize();
  const frame = () => {
    requestAnimationFrame(frame);
    if (document.hidden) return;
    if (controls.update() || dirty) {
      renderer.render(scene, camera);
      dirty = false;
    }
  };
  frame();
}

function activeBox() {
  const box = new THREE.Box3();
  for (const [id, mesh] of meshes) if (!selected || id === selected) box.expandByObject(mesh);
  return box;
}

function fit(resetDirection = false) {
  if (!loaded) return;
  const box = activeBox();
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  const halfFov = THREE.MathUtils.degToRad(camera.fov / 2);
  const horizontal = Math.atan(Math.tan(halfFov) * camera.aspect);
  const distance = sphere.radius / Math.sin(Math.min(halfFov, horizontal)) * 1.13;
  const direction = resetDirection ? initialDirection.clone() : camera.position.clone().sub(controls.target).normalize();
  controls.target.copy(sphere.center);
  camera.position.copy(sphere.center).addScaledVector(direction, distance);
  camera.near = Math.max(.001, sphere.radius / 200);
  camera.far = Math.max(100, distance * 30);
  camera.updateProjectionMatrix();
  controls.update();
  dirty = true;
}

function updateMaterials() {
  const style = $('palette').value;
  const context = $('context').checked;
  for (const [id, mesh] of meshes) {
    const index = catalog.parts.findIndex(part => part.id === id);
    const ghost = !!selected && id !== selected;
    mesh.visible = !ghost || context;
    mesh.material.color.setHex(style === 'neutral' ? 0xc9c4b5 : style === 'cuts' ? colors[index % colors.length] : 0xbf8b79);
    mesh.material.transparent = ghost;
    mesh.material.opacity = ghost ? .12 : 1;
    mesh.material.depthWrite = !ghost;
    mesh.material.roughness = style === 'neutral' ? .82 : .65;
    mesh.material.needsUpdate = true;
    mesh.renderOrder = ghost ? 0 : 1;
  }
  dirty = true;
}

function selectPart(id, resetView = true) {
  if (!loaded) return;
  selected = id;
  for (const button of document.querySelectorAll('[data-cut]')) {
    const active = button.dataset.cut === id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  }
  $('all-cuts').classList.toggle('active', !id);
  $('all-cuts').setAttribute('aria-pressed', String(!id));
  $('context').disabled = !id;
  const part = catalog.parts.find(p => p.id === id);
  $('selection-name').textContent = part ? part.sourceName : 'Conjunto original';
  const triangles = part ? part.triangles : catalog.parts.reduce((sum, item) => sum + item.triangles, 0);
  $('geometry-status').textContent = `${formatter.format(triangles)} triângulos preservados`;
  updateMaterials();
  if (resetView) fit(true);
}

function makeCutButtons() {
  $('cuts').replaceChildren();
  catalog.parts.forEach((part, index) => {
    const button = document.createElement('button');
    button.className = 'cut';
    button.dataset.cut = part.id;
    button.setAttribute('aria-pressed', 'false');
    const number = document.createElement('span');
    number.className = 'cut-number';
    number.textContent = String(index + 1).padStart(2, '0');
    const label = document.createElement('span');
    const strong = document.createElement('strong');
    strong.textContent = `Peça ${index + 1}`;
    const small = document.createElement('small');
    small.textContent = part.sourceName;
    label.append(strong, small);
    button.append(number, label);
    button.addEventListener('click', () => selectPart(part.id));
    $('cuts').append(button);
  });
}

function zoom(factor) {
  if (!loaded) return;
  const offset = camera.position.clone().sub(controls.target);
  const distance = THREE.MathUtils.clamp(offset.length() * factor, controls.minDistance, controls.maxDistance);
  camera.position.copy(controls.target).addScaledVector(offset.normalize(), distance);
  controls.update();
  dirty = true;
}

function rotateView(horizontal, vertical = 0) {
  if (!loaded) return;
  const offset = camera.position.clone().sub(controls.target);
  const spherical = new THREE.Spherical().setFromVector3(offset);
  spherical.theta += horizontal;
  spherical.phi = THREE.MathUtils.clamp(spherical.phi + vertical, .05, Math.PI - .05);
  camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));
  controls.update();
  dirty = true;
}

async function loadReference() {
  let response;
  try {
    response = await fetch(`${ASSET_ROOT}umn_reference_catalog.json`);
    if (!response.ok) throw new Error('Reference catalog is unavailable.');
    catalog = await response.json();
  } catch (error) {
    console.info('Local reference not installed; official source:', SOURCE);
    showError('missing');
    return;
  }
  try {
    const gltf = await new GLTFLoader().loadAsync(`${ASSET_ROOT}umn_reference.glb`, event => {
      const total = event.total || catalog.bytes;
      $('progress').textContent = total ? `Carregando detalhes · ${Math.min(100, Math.round(event.loaded / total * 100))}%` : 'Carregando os detalhes…';
    });
    const nodes = new Map(catalog.parts.map(part => [part.id, part]));
    gltf.scene.traverse(node => {
      if (!node.isMesh) return;
      const id = node.userData.partId || node.name;
      if (!nodes.has(id)) throw new Error('Unexpected object in local reference.');
      node.material = new THREE.MeshStandardMaterial({ color: 0xbf8b79, side: THREE.DoubleSide, roughness: .65, metalness: 0 });
      meshes.set(id, node);
    });
    if (meshes.size !== catalog.parts.length) throw new Error('Local reference has missing cuts.');
    scene.add(gltf.scene);
    loaded = true;
    makeCutButtons();
    for (const id of ['all-cuts', 'context', 'palette', 'fit', 'opposite', 'auto-rotate', 'zoom-out', 'zoom-in']) $(id).disabled = false;
    $('loading').hidden = true;
    // This smaller institutional cut exposes an informative plane. It is not
    // labelled as a specific chamber without an independent identification.
    selectPart(catalog.parts[2]?.id || catalog.parts[0].id);
  } catch (error) {
    console.error('Could not load local anatomical reference:', error);
    showError('invalid');
  }
}

$('about-button').addEventListener('click', () => $('about').showModal());
$('close-about').addEventListener('click', () => $('about').close());
$('all-cuts').addEventListener('click', () => selectPart(null));
$('context').addEventListener('change', updateMaterials);
$('palette').addEventListener('change', updateMaterials);
$('fit').addEventListener('click', () => fit(true));
$('opposite').addEventListener('click', () => rotateView(Math.PI));
$('zoom-in').addEventListener('click', () => zoom(.8));
$('zoom-out').addEventListener('click', () => zoom(1.25));
$('auto-rotate').addEventListener('click', () => {
  controls.autoRotate = !controls.autoRotate;
  $('auto-rotate').setAttribute('aria-pressed', String(controls.autoRotate));
  $('auto-rotate').textContent = controls.autoRotate ? 'Ⅱ Pausar' : '↻ Girar';
});
$('fullscreen').addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else if (viewport.requestFullscreen) await viewport.requestFullscreen();
  } catch { /* Fullscreen can be unavailable in an embedded browser. */ }
});
if (!document.fullscreenEnabled) $('fullscreen').hidden = true;
canvas.addEventListener('keydown', event => {
  if (!loaded) return;
  const actions = { ArrowLeft: () => rotateView(-.15), ArrowRight: () => rotateView(.15), ArrowUp: () => rotateView(0, -.15), ArrowDown: () => rotateView(0, .15), '+': () => zoom(.85), '=': () => zoom(.85), '-': () => zoom(1.15), r: () => fit(true), R: () => fit(true) };
  if (actions[event.key]) { event.preventDefault(); actions[event.key](); }
});

try { prepareScene(); await loadReference(); }
catch (error) { console.error('Reference viewer could not initialize:', error); showError('webgl'); }
