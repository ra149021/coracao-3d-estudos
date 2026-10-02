import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

function disposeScene(scene) {
  const geometries = new Set(), materials = new Set(), textures = new Set();
  scene.traverse(node => {
    if (node.geometry) geometries.add(node.geometry);
    for (const material of Array.isArray(node.material) ? node.material : [node.material]) if (material) {
      materials.add(material);
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    }
  });
  for (const value of [...geometries, ...materials, ...textures]) value.dispose();
}

export async function mountRealModel(host, model, signal, progress) {
  if (!/^assets\/(heart-ct|lung-ct|heart-hra|respiratory)\/model\.glb$/.test(model.asset)) throw new Error('Arquivo 3D inválido.');
  let catalog = null;
  if (model.catalog) {
    if (!/^assets\/(heart-hra|respiratory)\/catalog\.json$/.test(model.catalog)) throw new Error('Catálogo inválido.');
    const response = await fetch(model.catalog, {signal});
    if (!response.ok) throw new Error('Nomes indisponíveis.');
    catalog = await response.json();
  }
  const gltf = await new GLTFLoader().loadAsync(model.asset, event => {
    if (!signal.aborted && event.total) progress(`Carregando a reconstrução · ${Math.round(event.loaded / event.total * 100)}%`);
  });
  if (signal.aborted) { disposeScene(gltf.scene); throw new DOMException('Cancelado', 'AbortError'); }
  // The NIH file has no material: glTF's metallic default obscures its relief.
  // Set display-only matte shading; the source mesh and GLB stay unchanged.
  if (model.id === 'nih-heart-ct') gltf.scene.traverse(node => {
    for (const material of Array.isArray(node.material) ? node.material : [node.material]) if (material?.isMeshStandardMaterial) {
      material.color.set('#c8b4a4'); material.metalness = 0; material.roughness = .78; material.side = THREE.DoubleSide;
    }
  });
  let renderer;
  try { renderer = new THREE.WebGLRenderer({antialias: true, alpha: true}); }
  catch (error) { disposeScene(gltf.scene); throw error; }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#edece5');
  scene.add(new THREE.HemisphereLight('#fffaf0', '#6c7480', 2));
  const light = new THREE.DirectionalLight('#fff4e8', 3); light.position.set(5, 7, 9); scene.add(light);
  const fill = new THREE.DirectionalLight('#d6e6ff', 1.1); fill.position.set(-6, 1, -4); scene.add(fill);
  // Move and scale the whole scene uniformly; do not infer anatomy or alter topology.
  const box = new THREE.Box3().setFromObject(gltf.scene), center = box.getCenter(new THREE.Vector3());
  const extent = box.getSize(new THREE.Vector3());
  const longest = Math.max(extent.x, extent.y, extent.z);
  if (!Number.isFinite(longest) || longest <= 0) { disposeScene(gltf.scene); renderer.dispose(); throw new Error('Modelo sem limites válidos.'); }
  const content = new THREE.Group(); content.add(gltf.scene); gltf.scene.position.sub(center); content.scale.setScalar(4 / longest); scene.add(content);
  const entries = [];
  if (catalog) gltf.scene.traverse(node => {
    if (!node.isMesh) return;
    const part = catalog.parts.find(part => part.id === (node.userData.partId || node.name));
    node.visible = Boolean(part && model.groups.includes(part.group));
    if (!node.visible) return;
    node.geometry.computeBoundingBox();
    // Name and anchor belong to this source mesh, never to an inferred substructure.
    const original = node.material;
    node.material = original.clone(); node.material.metalness = 0; node.material.roughness = .8;
    original.dispose();
    entries.push({part, mesh:node, color:node.material.color.clone(), anchor:node.geometry.boundingBox.getCenter(new THREE.Vector3())});
  });
  content.updateMatrixWorld(true);
  const visibleBox = new THREE.Box3();
  if (entries.length) for (const entry of entries) visibleBox.expandByObject(entry.mesh);
  else visibleBox.setFromObject(content);
  const sphere = visibleBox.getBoundingSphere(new THREE.Sphere());
  const camera = new THREE.PerspectiveCamera(35, 1, .01, 100);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.minDistance = sphere.radius * .5; controls.maxDistance = sphere.radius * 10;
  controls.target.copy(sphere.center);
  let alive = true, dirty = true, frame = 0, visible = true, selected = null, names = true, isolated = false;
  const fit = (target = sphere) => {
    const angle = Math.min(camera.fov * Math.PI / 180, 2 * Math.atan(Math.tan(camera.fov * Math.PI / 360) * camera.aspect));
    controls.minDistance = target.radius * .3;
    camera.position.copy(target.center).addScaledVector(new THREE.Vector3(.25, .12, 1).normalize(), target.radius / Math.sin(angle / 2) * 1.08);
    controls.target.copy(target.center); controls.update(); dirty = true;
  };
  const resize = () => {
    const width = Math.max(1, host.clientWidth), height = Math.max(1, host.clientHeight);
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix(); dirty = true;
  };
  controls.addEventListener('change', () => { dirty = true; });
  host.replaceChildren(renderer.domElement); renderer.domElement.setAttribute('aria-label', model.title + '. Arraste para girar; use a roda para aproximar.');
  const overlay = document.createElement('div'); overlay.className = 'anatomy-names';
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('aria-hidden', 'true'); overlay.append(svg);
  const raycaster = new THREE.Raycaster();
  const meshes = entries.map(entry => entry.mesh);
  const emitSelection = entry => host.dispatchEvent(new CustomEvent('anatomy-select', {detail:entry?.part || null}));
  const select = id => {
    selected = entries.find(entry => entry.part.id === id) || null;
    if (!selected) isolated = false;
    for (const entry of entries) {
      const material = entry.mesh.material;
      entry.mesh.visible = !isolated || !selected || entry === selected;
      material.color.copy(entry.color); material.emissive.set(entry === selected ? '#593d08' : '#000000');
      material.transparent = Boolean(selected && entry !== selected);
      material.opacity = selected && entry !== selected ? .13 : 1;
      material.depthWrite = !material.transparent;
      material.needsUpdate = true;
    }
    if (isolated && selected) fit(new THREE.Box3().setFromObject(selected.mesh).getBoundingSphere(new THREE.Sphere()));
    dirty = true; emitSelection(selected);
  };
  for (const entry of entries) {
    const label = document.createElement('button'); label.type = 'button'; label.className = 'anatomy-name';
    label.textContent = entry.part.label; label.dataset.part = entry.part.id; label.hidden = true;
    label.addEventListener('click', () => select(entry.part.id));
    const line = document.createElementNS(svg.namespaceURI, 'path'); line.hidden = true; line.style.display = 'none'; svg.append(line);
    overlay.append(label); Object.assign(entry, {label,line});
  }
  if (entries.length) host.append(overlay);
  const updateNames = () => {
    const width = host.clientWidth, height = host.clientHeight, columns = [[], []];
    for (const entry of entries) {
      entry.label.hidden = true; entry.line.style.display = 'none';
      if (!names || !entry.mesh.visible || (selected ? entry !== selected : !model.labels.includes(entry.part.id))) continue;
      const point = entry.mesh.localToWorld(entry.anchor.clone()).project(camera);
      if (point.z < -1 || point.z > 1 || Math.abs(point.x) > 1 || Math.abs(point.y) > 1) continue;
      raycaster.setFromCamera(new THREE.Vector2(point.x, point.y), camera);
      // Hide labels of opaque pieces behind another mesh; selecting reveals them.
      const hits = raycaster.intersectObjects(meshes.filter(mesh => mesh.visible), false);
      if (!selected && hits[0]?.object !== entry.mesh) continue;
      const x = (point.x + 1) * width / 2, y = (1 - point.y) * height / 2;
      columns[x < width / 2 ? 0 : 1].push({entry,x,y});
    }
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    columns.forEach((items, side) => {
      items.sort((a,b) => a.y - b.y);
      let previousBottom = 8;
      for (const {entry,x,y} of items) {
        entry.label.hidden = false;
        entry.label.style.maxWidth = `${Math.min(165, width * .37)}px`;
        entry.label.style.left = side ? 'auto' : '8px'; entry.label.style.right = side ? '8px' : 'auto';
        const h = entry.label.offsetHeight;
        const top = Math.max(previousBottom, Math.min(height - h - 54, y - h / 2));
        if (top + h > height - 46) { entry.label.hidden = true; continue; }
        entry.label.style.top = `${top}px`; previousBottom = top + h + 6;
        entry.label.setAttribute('aria-pressed', String(entry === selected));
        const endX = side ? width - 8 - entry.label.offsetWidth : 8 + entry.label.offsetWidth;
        entry.line.setAttribute('d', `M ${x} ${y} L ${endX} ${top + h / 2}`); entry.line.style.display = '';
      }
    });
  };
  let pointerStart = null;
  const pointerDown = event => { pointerStart = {x:event.clientX,y:event.clientY}; };
  const pointerUp = event => {
    if (!pointerStart || Math.hypot(event.clientX-pointerStart.x,event.clientY-pointerStart.y)>5) return;
    const rect = renderer.domElement.getBoundingClientRect();
    raycaster.setFromCamera(new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,1-(event.clientY-rect.top)/rect.height*2),camera);
    const hits = raycaster.intersectObjects(meshes.filter(mesh=>mesh.visible),false);
    if (hits.length) select(entries.find(entry=>entry.mesh===hits[0].object)?.part.id);
  };
  renderer.domElement.addEventListener('pointerdown',pointerDown); renderer.domElement.addEventListener('pointerup',pointerUp);
  const observer = new ResizeObserver(resize); observer.observe(host); resize(); fit();
  const intersection = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; dirty = true; }); intersection.observe(host);
  const draw = () => {
    if (!alive) return;
    frame = requestAnimationFrame(draw);
    if (visible && !document.hidden && (controls.update() || dirty || controls.autoRotate)) { renderer.render(scene, camera); updateNames(); dirty = false; }
  }; draw();
  const dispose = () => {
    if (!alive) return;
    alive = false; cancelAnimationFrame(frame); observer.disconnect(); intersection.disconnect(); controls.dispose(); disposeScene(scene);
    renderer.domElement.removeEventListener('pointerdown',pointerDown); renderer.domElement.removeEventListener('pointerup',pointerUp);
    renderer.dispose(); renderer.forceContextLoss(); renderer.domElement.remove(); overlay.remove(); signal.removeEventListener('abort', dispose);
  };
  signal.addEventListener('abort', dispose, {once: true});
  return {dispose, fit, parts:entries.map(entry=>entry.part), select,
    toggleNames: () => { names = !names; dirty = true; return names; },
    toggleIsolation: () => { isolated = !isolated; select(selected?.part.id); if (!isolated) fit(); return isolated; },
    zoom: factor => { camera.position.sub(controls.target).multiplyScalar(factor).add(controls.target); controls.update(); dirty = true; },
    toggleRotation: () => { controls.autoRotate = !controls.autoRotate; return controls.autoRotate; }};
}
