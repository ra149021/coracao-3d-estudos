import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createAnatomyRenderer} from './anatomy-renderer.js';
let reviewed=0;
function savedRecord(key){try{const value=JSON.parse(localStorage.getItem(key)||'{}');return value&&typeof value==='object'&&!Array.isArray(value)?value:{};}catch{return {};}}
for(const scope of ['circulatory','respiratory','larynx','heart-hra']){const count=savedRecord(`atlas:practice-summary:${scope}`).reviewed;if(typeof count==='number'&&Number.isFinite(count)&&count>=0)reviewed+=Math.floor(count);}
for(const system of ['circulatory','respiratory']){const answers=savedRecord(`atlas:theory:${system}`).answers;if(answers&&typeof answers==='object'&&!Array.isArray(answers))reviewed+=Object.values(answers).filter(answer=>answer&&['known','review'].includes(answer.rating)).length;}
document.getElementById('review-count').textContent=reviewed;
async function preview(holder){
 const respiratory=holder.dataset.model==='respiratory',root=respiratory?'assets/lung-ct/':'assets/heart-ct/';
 try{
  document.getElementById(respiratory?'resp-count':'heart-count').textContent='Reconstrução de tomografia';
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(32,1,.01,200);const controls=new OrbitControls(camera,renderer.domElement);controls.enableZoom=false;controls.enablePan=false;controls.enableDamping=true;controls.rotateSpeed=.55;
  const lighting=createAnatomyRenderer(renderer,scene,camera);lighting.setProfile('relief');
  const gltf=await new GLTFLoader().loadAsync(root+'model.glb');const sourceBox=new THREE.Box3().setFromObject(gltf.scene);
  if(!respiratory)gltf.scene.traverse(node=>{for(const material of Array.isArray(node.material)?node.material:[node.material])if(material?.isMeshStandardMaterial){material.color.set('#c8b4a4');material.metalness=0;material.roughness=.78;material.side=THREE.DoubleSide;}});
  const extent=sourceBox.getSize(new THREE.Vector3()),longest=Math.max(extent.x,extent.y,extent.z);
  if(!Number.isFinite(longest)||longest<=0)throw new Error('Modelo sem limites');
  const content=new THREE.Group();content.add(gltf.scene);gltf.scene.position.sub(sourceBox.getCenter(new THREE.Vector3()));content.scale.setScalar(4/longest);scene.add(content);
  const box=new THREE.Box3().setFromObject(content);if(box.isEmpty())throw new Error('Prévia sem superfície');
  holder.querySelector('.preview-loading')?.remove();holder.append(renderer.domElement);const center=box.getCenter(new THREE.Vector3()),radius=box.getBoundingSphere(new THREE.Sphere()).radius;
  let dirty=true,visible=true;const fit=()=>{const w=holder.clientWidth,h=holder.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();const f=Math.min(camera.fov*Math.PI/180,2*Math.atan(Math.tan(camera.fov*Math.PI/360)*camera.aspect));const direction=new THREE.Vector3(respiratory?.15:.3,.1,1).normalize();controls.target.copy(center);camera.position.copy(center).addScaledVector(direction,radius/Math.sin(f/2)*1.02);controls.update();dirty=true;};
  new ResizeObserver(fit).observe(holder);fit();controls.addEventListener('change',()=>dirty=true);new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;dirty=true;}).observe(holder);
  const frame=()=>{requestAnimationFrame(frame);if(!visible||document.hidden)return;const changed=controls.update();if(dirty||changed){renderer.render(scene,camera);dirty=false;}};frame();
 }catch{const message=holder.querySelector('.preview-loading');if(message)message.textContent='Abra o atlas para explorar este sistema.';}
}
for(const holder of document.querySelectorAll('.model-preview'))preview(holder);
