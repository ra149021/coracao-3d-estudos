import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {mountCadaverPanel} from './cadaver-panel.js';
const $ = id => document.getElementById(id), base='assets/coronary-hra/';
const entries=[], heart=[], buttons=new Map();
const comparison=mountCadaverPanel($('comparison'), {manifestPath:'assets/coronary-hra/comparisons.json'});
const dialog=$('comparison').querySelector('dialog');
const zoom=document.createElement('button');
zoom.type='button';zoom.textContent='Zoom da fotografia';zoom.setAttribute('aria-pressed','false');
zoom.onclick=()=>{const image=dialog.querySelector('img');if(!image)return;const active=image.dataset.zoom!=='true';image.dataset.zoom=String(active);zoom.setAttribute('aria-pressed',String(active));};
dialog.insertBefore(zoom,dialog.children[1]);
dialog.addEventListener('close',()=>zoom.setAttribute('aria-pressed','false'));
$('comparison-loading').remove();
function syncComparison(){
 const e=entries.find(e=>e.name===selected);
 comparison?.setSelection(e?{modelId:'coronary-reference::'+e.sourceId,system:'circulatory',partId:e.name}:null);
}
let renderer,scene,camera,orbit,center,size,selected=null,isolated=false,ready=false;
function snapshot(){return {ready,selected,isolated,wall:$('wall').value,visibleMeshes:entries.filter(e=>e.mesh.visible).length+heart.filter(e=>e.mesh.visible).length,drawCalls:renderer?.info.render.calls||0,triangles:renderer?.info.render.triangles||0,camera:camera?.position.toArray(),zoom:camera?.zoom,target:orbit?.target.toArray(),meshes:[...heart,...entries].map(e=>({name:e.name,visible:e.mesh.visible,matrix:e.mesh.matrixWorld.toArray(),opacity:e.mesh.material.opacity}))};}
window.coronaryReference={snapshot};
function render(){if(!ready)return;renderer.render(scene,camera);const s=snapshot();$('metrics').textContent=`${s.visibleMeshes} malhas visíveis · ${s.drawCalls} draw calls · ${s.triangles} triângulos renderizados`;}
function apply(){
 if(!ready)return;
 for(const e of [...heart,...entries]){
  const isHeart=e.group==='heart';
  e.mesh.visible=isolated ? e.name===selected : isHeart ? $('wall').value!=='vessels' : $(e.group).checked;
  const m=e.mesh.material;m.color.copy(e.color);
  if($('colors').checked)m.color.set(isHeart?'#b79c80':e.group==='arteries'?'#cf3529':'#285bb6');
  m.opacity=isHeart&&$('wall').value==='translucent'?.24:1;m.transparent=m.opacity<1;m.depthWrite=!m.transparent;
  m.emissive.set(e.name===selected?'#b88700':'#000000');m.emissiveIntensity=e.name===selected?.65:0;m.needsUpdate=true;
 }
 for(const [name,b] of buttons)b.setAttribute('aria-pressed',String(name===selected));
 $('isolate').disabled=!selected;$('isolate').textContent=isolated?'Mostrar contexto':'Isolar seleção';
 const e=entries.find(e=>e.name===selected);$('selection').textContent=e?`${e.label} · ${e.name}${isolated?' — isolado':' — contexto preservado; gire para ver faces ocultas'}${e.name==='VH_F_left_anterior_descending_artery'?' — Identificação em revisão: o nome do nó indica descendente anterior coronária, mas o grafo HRA v1.3 associa fma8636 a um ramo da artéria pulmonar esquerda. Essa divergência de metadados não demonstra erro de geometria; não use esta identificação isoladamente como gabarito.':''}`:'Nenhum vaso selecionado.';
 render();
}
function select(name){const e=entries.find(e=>e.name===name);if(!e)return;selected=name;$(e.group).checked=true;apply();syncComparison();}
// Equivalent to Blender's (0, ±2, .35) with its glTF Y-up → Z-up conversion.
function view(sign){camera.position.copy(center).add(new THREE.Vector3(0,.35,sign*2).multiplyScalar(size));camera.up.set(0,1,0);orbit.target.copy(center);camera.zoom=1;camera.updateProjectionMatrix();orbit.update();render();}
function reset(){selected=null;syncComparison();isolated=false;$('wall').value='opaque';$('arteries').checked=$('veins').checked=$('colors').checked=true;view(1);apply();}
try{
 const response=await fetch(base+'manifest.json');if(!response.ok)throw Error('Manifesto indisponível');const manifest=await response.json();
 for(const s of manifest.sources){const p=document.createElement('p');p.textContent=s.title+' — '+s.author+' · ';for(const [text,url] of [['Registro HRA',s.url],['DataCite / DOI',s.doi],['Original GLB',base+s.file]]){const a=document.createElement('a');a.textContent=text;a.href=url;p.append(a,document.createTextNode(' · '));}const hash=document.createElement('small');hash.textContent='SHA-256 '+s.sha256;p.append(hash);$('sources').append(p);}
 const loaded=await Promise.all(manifest.sources.map(async source=>({source,gltf:await new GLTFLoader().loadAsync(base+source.file)})));
 scene=new THREE.Scene();scene.background=new THREE.Color('#e6e4df');
 const exact=new Map(manifest.parts.map(p=>[p.name,p]));
 for(const {source,gltf} of loaded){
  // Preserve the complete scene hierarchy and every native node transform.
  scene.add(gltf.scene);gltf.scene.traverse(mesh=>{if(!mesh.isMesh)return;const part=source.role==='heart'?{name:mesh.name,group:'heart'}:exact.get(mesh.name);mesh.visible=!!part;if(!part)return;
   if(Array.isArray(mesh.material))throw Error('Material múltiplo inesperado');
   mesh.material=mesh.material.clone();mesh.material.metalness=0;mesh.material.roughness=.82;
   const e={...part,sourceId:source.id,mesh,color:mesh.material.color.clone()};(source.role==='heart'?heart:entries).push(e);
  });
 }
 if(heart.length!==14||entries.length!==17||new Set(entries.map(e=>e.name)).size!==17)throw Error('Inventário divergente: carregamento interrompido');
 scene.updateMatrixWorld(true);const box=new THREE.Box3();for(const e of [...heart,...entries])box.union(new THREE.Box3().setFromObject(e.mesh));center=box.getCenter(new THREE.Vector3());const extent=box.getSize(new THREE.Vector3());size=Math.max(extent.x,extent.y,extent.z);
 renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;$('viewport').append(renderer.domElement);
 camera=new THREE.OrthographicCamera(-size,size,size,-size,size*.001,size*100);
 orbit=new OrbitControls(camera,renderer.domElement);orbit.enablePan=false;orbit.minZoom=.3;orbit.maxZoom=8;orbit.addEventListener('change',render);
 scene.add(new THREE.HemisphereLight('#fff9ed','#657080',2.5));for(const sign of [1,-1]){const light=new THREE.DirectionalLight('#ffffff',2);light.position.copy(center).add(new THREE.Vector3(sign,1,sign).multiplyScalar(size*3));scene.add(light);}
 for(const group of ['arteries','veins']){const h=document.createElement('h3');h.textContent=group==='arteries'?'Artérias (9)':'Veias (8)';$('parts').append(h);for(const e of entries.filter(e=>e.group===group)){const b=document.createElement('button');b.textContent=e.label;const small=document.createElement('small');small.textContent=e.name;b.append(small);b.dataset.name=e.name;b.setAttribute('aria-pressed','false');b.onclick=()=>{select(e.name);$('comparison').scrollIntoView({block:'start'});};buttons.set(e.name,b);$('parts').append(b);}}
 for(const id of ['wall','arteries','veins','colors'])$(id).onchange=()=>{isolated=false;const e=entries.find(e=>e.name===selected);if(e&&!$(e.group).checked){selected=null;syncComparison();}apply();};
 $('isolate').onclick=()=>{isolated=!isolated;apply();};$('reset').onclick=reset;$('view-a').onclick=()=>view(1);$('view-b').onclick=()=>view(-1);
 for(const [id,factor] of [['zoom-in',1.25],['zoom-out',.8]])$(id).onclick=()=>{camera.zoom=THREE.MathUtils.clamp(camera.zoom*factor,.3,8);camera.updateProjectionMatrix();render();};
 for(const [id,angle] of [['left',.25],['right',-.25]])$(id).onclick=()=>{camera.position.sub(center).applyAxisAngle(new THREE.Vector3(0,1,0),angle).add(center);orbit.update();render();};
 let down;renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);const hit=ray.intersectObjects([...heart,...entries].filter(e=>e.mesh.visible).map(e=>e.mesh),false)[0];if(hit&&entries.some(e=>e.mesh===hit.object))select(hit.object.name);});
 ready=true;function resize(){const w=$('viewport').clientWidth,h=$('viewport').clientHeight,aspect=w/h;const half=size*.575;camera.left=-half*Math.max(1,aspect);camera.right=-camera.left;camera.top=half*Math.max(1,1/aspect);camera.bottom=-camera.top;camera.updateProjectionMatrix();renderer.setSize(w,h);render();}new ResizeObserver(resize).observe($('viewport'));resize();reset();$('controls').disabled=false;$('status').textContent='Par HRA carregado: 14 malhas cardíacas + 17 coronárias nas coordenadas originais.';
}catch(error){ready=false;selected=null;syncComparison();renderer?.dispose();$('viewport').replaceChildren();$('status').textContent='Não foi possível carregar o par HRA. Use “Voltar ao atlas original” ou baixe os GLBs na procedência. '+error.message;}
