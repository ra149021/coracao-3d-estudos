import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

/** Lighting and screen-space contact shading; never modifies anatomical vertices. */
export function createAnatomyRenderer(renderer, scene, camera) {
  const ambient=new THREE.HemisphereLight('#fff8ee','#7b8387',.82);
  const key=new THREE.DirectionalLight('#fff3e4',2.8);key.position.set(-4,6,7);
  const fill=new THREE.DirectionalLight('#dfebff',.65);fill.position.set(6,1,3);
  const rim=new THREE.DirectionalLight('#ffdfcc',1.1);rim.position.set(1,5,-6);
  scene.add(ambient,key,fill,rim);
  let composer=null,ao=null,active=false,profile='relief',available=Boolean(renderer.extensions.get('EXT_color_buffer_float'));
  let width=1,height=1,radius=.2;
  function allocate(){
    if(composer||!available)return;
    const ratio=Math.min(renderer.getPixelRatio(),1.5);
    const target=new THREE.WebGLRenderTarget(width*ratio,height*ratio,{type:THREE.HalfFloatType,samples:4});
    composer=new EffectComposer(renderer,target);composer.setPixelRatio(ratio);
    composer.addPass(new RenderPass(scene,camera));
    ao=new GTAOPass(scene,camera,width*ratio,height*ratio,undefined,{radius,thickness:radius*1.5,distanceFallOff:1,samples:16,scale:1},{radius:3,samples:16});
    ao.normalMaterial.side=THREE.DoubleSide;
    ao.blendIntensity=.65;
    composer.addPass(ao);composer.addPass(new OutputPass());
    composer.setSize(width,height);
  }
  return {
    resize(w,h){width=Math.max(1,w);height=Math.max(1,h);composer?.setSize(width,height);},
    setScale(bounds){radius=Math.max(.03,bounds.getSize(new THREE.Vector3()).length()*.025);ao?.updateGtaoMaterial({radius,thickness:radius*1.5});},
    setProfile(value){
      profile=value==='uniform'?'uniform':'relief';
      const uniform=profile==='uniform';
      ambient.intensity=uniform?1.65:.82;key.intensity=uniform?2.4:2.8;fill.intensity=uniform?1.25:.65;rim.intensity=uniform?1.35:1.1;
      renderer.toneMappingExposure=uniform?1.07:1.06;
    },
    render({depth=true,clipping=false,transparent=false}={}){
      active=Boolean(depth&&!clipping&&!transparent&&available);
      if(active){
        try{allocate();composer.render();}
        catch(error){available=false;active=false;console.warn('Sombras de profundidade indisponíveis; visualização direta preservada.',error);renderer.setRenderTarget(null);renderer.render(scene,camera);}
      }else renderer.render(scene,camera);
    },
    snapshot(){return {profile,depthAvailable:available,depthActive:active};},
    dispose(){ao?.dispose();composer?.dispose();}
  };
}
