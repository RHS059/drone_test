import {restoreCadNodeNames} from './connected/restore-cad-names.mjs';
import * as T from 'three/webgpu';
import {OrbitControls} from './vendor/OrbitControls.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';
import {forward,origin,multiply,homeJoints} from './kinematics.js';
import {loadRover} from './rover.js?v=panel-visibility-01';
import {decodeCadBytes} from './cad-loading.js?v=motion-03';
const ROOT='./assets/robots/';
export async function createScene(host,onSelect){
 const graph=await fetch(ROOT+'robot-kinematics.json').then(r=>{if(!r.ok)throw Error('Source joint graph unavailable');return r.json()});
 const scene=new T.Scene();scene.background=new T.Color('#1c2b2c');
 const camera=new T.PerspectiveCamera(38,1,.02,80);camera.up.set(0,0,1);camera.position.set(5,-6,4.4);
 let renderer=null,renderError=null;try{renderer=new T.WebGPURenderer({antialias:true,forceWebGL:new URLSearchParams(location.search).has('webgl')});renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));await renderer.init();host.appendChild(renderer.domElement);renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.2;}catch(e){renderError=e;renderer=null;const box=document.querySelector('#scene-error');box.hidden=false;box.textContent='3D rendering is unavailable in this browser. Source joint controls and forward kinematics remain executable; no replacement geometry is shown. Try a browser with WebGPU or WebGL 2 enabled.';}
 
 const controls=new OrbitControls(camera,renderer?.domElement??document.createElement('div'));controls.target.set(.2,0,1);controls.enableDamping=true;controls.minDistance=.2;controls.maxDistance=18;
 scene.add(new T.HemisphereLight('#e7f2ee','#738887',3));const light=new T.DirectionalLight('#fff2dd',4);light.position.set(2,-3,6);scene.add(light);const fill=new T.DirectionalLight('#bddef4',2);fill.position.set(-2,4,3);scene.add(fill);
 const grid=new T.GridHelper(12,24,'#668477','#334b45');grid.rotation.x=Math.PI/2;grid.position.z=0;scene.add(grid);const axes=new T.AxesHelper(.4);axes.visible=false;scene.add(axes);
 const loader=new GLTFLoader(),cache=new Map();const pending=new Map();let meshCount=0;
 async function asset(url,label){if(!pending.has(url))pending.set(url,url.endsWith('.gz')?(async()=>{const r=await fetch(url);if(!r.ok)throw Error('Missing compressed CAD asset');const bytes=await decodeCadBytes(await r.arrayBuffer());return loader.parseAsync(bytes,new URL('.',new URL(url,location.href)).href)})():loader.loadAsync(url));const original=restoreCadNodeNames(await pending.get(url)).scene;const obj=original.clone(true);obj.traverse(o=>{if(o.isMesh){o.userData.label=label;meshCount++;}});cache.set(url,original);return obj;}
 const vehicle=new T.Group();vehicle.position.z=.6655;scene.add(vehicle);
 const frame=await asset('./assets/mechanical/frame_R07.glb','Original lighter frame candidate · parametric B-rep · unqualified structure');vehicle.add(frame);
 const rover=await loadRover(vehicle,asset);
 const arms=[],tools=[],jointNames=graph.ur20.joints.filter(j=>j.type!=='fixed').map(j=>j.name);
 async function robot(model,name){const group=new T.Group(),links={};for(const link of model.links){const g=new T.Group();g.name=link.name;g.matrixAutoUpdate=false;group.add(g);links[link.name]=g;if(link.visual){const visual=new T.Group();visual.matrixAutoUpdate=false;visual.matrix.fromArray(origin(link.visual.origin));visual.add(await asset(ROOT+link.visual.asset,`${name} / ${link.name} · licensed OEM visual mesh`));visual.children[0].scale.set(...(link.visual.scale??[1,1,1]));g.add(visual);}}return{group,links,model,pose:{},set(values){this.pose={...values};const fk=forward(model,values);for(const[name,m]of Object.entries(fk))if(links[name])links[name].matrix.fromArray(m);this.fk=fk;return fk;}};}
 for(let i=0;i<2;i++){
  const arm=await robot(graph.ur20,`UR20 ${i?'right':'left'}`);arm.group.position.set(.9,i?-.3:.3,.13);vehicle.add(arm.group);
  const chain=new T.Group();chain.matrixAutoUpdate=false;arm.group.add(chain);tools.push(chain);
  const adapter=await asset('./assets/mechanical/adapter_R04.glb','Original tool adapter · mating geometry only · loads unqualified');chain.add(adapter);
  const couplingNode=new T.Group();couplingNode.position.z=.0235;chain.add(couplingNode);couplingNode.add(await asset(ROOT+graph.coupling.visual.asset,'Licensed Robotiq 2F85 source coupling · source seating frames · not manufacturing STEP'));
  const gripper=await robot(graph.robotiq,'Robotiq 2F85');gripper.group.position.z=.011;couplingNode.add(gripper.group);
  arm.gripper=gripper;arm.chain=chain;arms.push(arm);
 }
 const driver=graph.robotiq.joints.find(j=>j.type!=='fixed'&&!j.mimic).name;
 function setArm(i,values){const fk=arms[i].set(values);arms[i].chain.matrix.fromArray(multiply(fk.tool0,origin({rpy:[0,0,Math.PI]})));}
 function home(){rover.homeSteering();arms.forEach((a,i)=>setArm(i,Object.fromEntries(jointNames.map((n,j)=>[n,homeJoints[j]]))));arms.forEach(a=>a.gripper.set({[driver]:0}));}
 home();
 const ray=new T.Raycaster(),pointer=new T.Vector2();let down;
 renderer?.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);renderer?.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const b=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-b.left)/b.width*2-1,1-(e.clientY-b.top)/b.height*2);ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(scene.children,true).find(h=>{let p=h.object;if(!p.userData.label)return false;while(p){if(!p.visible)return false;p=p.parent}return true});if(hit)onSelect(hit.object.userData.label)});
 const resize=()=>{if(!renderer||!host.clientWidth||!host.clientHeight)return;renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix()};new ResizeObserver(resize).observe(host);resize();renderer?.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera)});
 const api={rover,setWheelAngle:v=>rover.setWheelAngle(v),setMotionStudy:v=>rover.setMotionStudy(v),setSuspension:q=>rover.setSuspension(q),setRack:(end,value)=>rover.setRack(end,value),setWorkshop:v=>rover.setWorkshop(v),setCradle:id=>rover.setCradle(id),showBody:v=>rover.showBody(v),showCorners:v=>rover.showCorners(v),openService:v=>rover.openService(v),graph,arms,jointNames,renderer,renderError:renderError?.message??null,setJoint(i,name,value){setArm(i,{...arms[i].pose,[name]:value})},setGripper(value){arms.forEach(a=>a.gripper.set({[driver]:value}))},home,showFrame(v){frame.visible=v},showRight(v){arms[1].group.visible=v},showTools(v){tools.forEach(t=>t.visible=v)},axes(){axes.visible=!axes.visible;return axes.visible},view(v){camera.position.set(...(v==='top'?[.2,0,7]:v==='side'?[.2,-7,.9]:[5,-6,4.4]));controls.target.set(.2,0,1);controls.update()},renderOnce(){scene.updateMatrixWorld(true);controls.update();renderer?.render(scene,camera);},pauseRendering(){renderer?.setAnimationLoop(null);},snapshot(){scene.updateMatrixWorld(true);let actualMeshes=0;vehicle.traverse(n=>{if(n.isMesh)actualMeshes++;});return{rover:rover.snapshot(),joints:arms.map(a=>a.pose),toolMatrices:arms.map(a=>a.chain.matrix.elements.slice()),linkMatrices:arms.map(a=>Object.fromEntries(Object.entries(a.links).map(([n,l])=>[n,l.matrix.elements.slice()]))),meshes:actualMeshes,loadedAssetMeshes:meshCount,renderer:renderer?(renderer.backend.isWebGPUBackend?'webgpu':'webgl2'):'unavailable'};}};
 window.__CAD_DEBUG__=api;return api;
}
