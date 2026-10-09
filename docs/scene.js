import * as T from 'three/webgpu';
import { OrbitControls } from './vendor/OrbitControls.js';
export async function createScene(host,onSelect){
 const scene=new T.Scene();scene.background=new T.Color('#1e292c');scene.fog=new T.Fog('#1e292c',17,37);
 const camera=new T.PerspectiveCamera(40,1,.05,80);camera.position.set(6.7,5.7,7.9);
 const renderer=new T.WebGPURenderer({antialias:true,forceWebGL:new URLSearchParams(location.search).has('webgl')});renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));await renderer.init();host.appendChild(renderer.domElement);
 document.querySelector('#backend').textContent=renderer.backend.isWebGPUBackend?'WEBGPU ACTIVE':'WEBGL 2 FALLBACK · WebGPU unavailable';
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,.65,0);controls.enableDamping=true;controls.maxPolarAngle=Math.PI/2-.02;controls.minDistance=3;controls.maxDistance=18;
 scene.add(new T.HemisphereLight('#e7f1ec','#586971',3));const sun=new T.DirectionalLight('#fff4da',4);sun.position.set(3,8,5);scene.add(sun);
 const platform=new T.Group();scene.add(platform);let vehicle=new T.Group();platform.add(vehicle);
 const grid=new T.GridHelper(30,60,'#627170','#334449');grid.position.y=-.027;platform.add(grid);
 const floor=new T.Mesh(new T.PlaneGeometry(70,70),new T.MeshStandardMaterial({color:'#1c292d',roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.035;platform.add(floor);
 const mats={body:new T.MeshStandardMaterial({color:'#a8bc69',metalness:.5,roughness:.53}),edge:new T.MeshStandardMaterial({color:'#3d5148',metalness:.7,roughness:.45}),black:new T.MeshStandardMaterial({color:'#172326',roughness:.86}),battery:new T.MeshStandardMaterial({color:'#82bed0',metalness:.25,roughness:.47}),arm:new T.MeshStandardMaterial({color:'#e7aa78',metalness:.35,roughness:.45}),steel:new T.MeshStandardMaterial({color:'#889b9c',metalness:.75,roughness:.32}),lift:new T.MeshStandardMaterial({color:'#e8df76',metalness:.5,roughness:.5})};
 const selectable=[],modules=[],wheels=[],armGroups=[],points=[];
 function box(w,h,d,x,y,z,mat,name,parent=vehicle){const m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);if(name){m.userData.label=name;selectable.push(m)}return m}
 function cylinder(r,h,x,y,z,mat,name,parent=vehicle){const m=new T.Mesh(new T.CylinderGeometry(r,r,h,24),mat);m.position.set(x,y,z);parent.add(m);if(name){m.userData.label=name;selectable.push(m)}return m}
 function strut(a,b,r,mat,parent=vehicle){const d=new T.Vector3().subVectors(b,a);const m=new T.Mesh(new T.CylinderGeometry(r,r,d.length(),12),mat);m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());parent.add(m);return m}
 function group(name){const g=new T.Group();vehicle.add(g);g.userData.label=name;return g}
 box(3.75,.2,1.3,0,.72,0,mats.edge,'Chassis / 4.0 × 1.8 m transport design assumption');
 box(3.75,.12,1.35,0,.89,0,mats.body,'Upper deck / fabrication design unresolved');
 for(const z of [-.60,.60]){box(3.8,.17,.08,0,1.02,z,mats.body);box(3.7,.11,.12,0,.52,z,mats.edge)}
 for(const x of [-1.35,0,1.35])for(const z of [-.76,.76]){
 const g=group('Wheel station');g.position.set(x,.362,z);const tire=cylinder(.39,.267,0,0,0,mats.black,'BKT SKID POWER HD 10-16.5 envelope / 780 mm OD',g);tire.rotation.x=Math.PI/2;
 const hub=cylinder(.19,.282,0,0,0,mats.steel,'Wheel drive / motor and reduction unresolved',g);hub.rotation.x=Math.PI/2;
 const cap=cylinder(.095,.30,0,0,0,mats.body,null,g);cap.rotation.x=Math.PI/2;
 for(let j=0;j<20;j++){let t=j*Math.PI/10;const tread=box(.10,.065,.28,Math.sin(t)*.375,Math.cos(t)*.375,0,mats.black,null,g);tread.rotation.z=-t}
 strut(new T.Vector3(x,.7,z*.65),new T.Vector3(x,.38,z),.07,mats.steel);wheels.push(g);modules.push({obj:g,base:g.position.clone(),offset:new T.Vector3(0,.1,Math.sign(z)*.8)});
 }
 for(let i=0;i<10;i++){const x=-1.25+(i%5)*.55,z=i<5?-.32:.32;const m=box(.260,.276,.180,x,1.098,z,mats.battery,'RELiON InSight 48 V / 1.536 kWh, 15.6 kg');modules.push({obj:m,base:m.position.clone(),offset:new T.Vector3(0,.75,0),battery:i})}
 for(const z of [-.48,.48]){const g=group('UR20 arm reference envelope');g.position.set(.9,1.02,z);cylinder(.13,.16,0,.06,0,mats.steel,'UR20 / 64 kg arm; 20 kg nominal payload',g);strut(new T.Vector3(0,.14,0),new T.Vector3(-.32,.65,0),.09,mats.arm,g);cylinder(.12,.19,-.32,.65,0,mats.steel,null,g);strut(new T.Vector3(-.32,.65,0),new T.Vector3(.25,.84,0),.075,mats.arm,g);cylinder(.10,.17,.25,.84,0,mats.steel,null,g);strut(new T.Vector3(.25,.84,0),new T.Vector3(.45,.48,0),.055,mats.arm,g);box(.12,.14,.14,.45,.43,0,mats.steel,'Tool flange / tool mass and inertia must be checked',g);armGroups.push(g);modules.push({obj:g,base:g.position.clone(),offset:new T.Vector3(.3,1.3,Math.sign(z)*.2)})}
 const liftGroup=group('Carried lift concept');box(2.6,.13,.18,-.25,1.35,0,mats.lift,'Folded goods-lift concept / not autonomous deployment validated',liftGroup);
 const mast=group('Perception mast');mast.position.set(-1.5,1,0);box(.08,.67,.08,0,.33,0,mats.steel,null,mast);box(.24,.12,.2,0,.72,0,mats.black,'Perception package / sensor selection unresolved',mast);
 for(const x of [-1.5,1.5])for(const z of [-.55,.55]){const p=new T.Mesh(new T.TorusGeometry(.065,.015,8,16),mats.lift);p.position.set(x,1.0,z);p.rotation.x=Math.PI/2;p.visible=false;vehicle.add(p);points.push(p)}
 const assembly=new T.Group();scene.add(assembly);assembly.visible=false;assembly.position.set(0,0,-3.3);
 box(3.7,.10,1.9,0,.06,0,mats.edge,'Independent assembly pallet',assembly);
 for(const x of [-1.8,1.8])for(const z of [-1.15,1.15]){box(.2,2.6,.2,x,1.3,z,mats.lift,'Independent grounded gantry / preliminary 500 kg WLL target',assembly);box(.6,.1,.6,x,.05,z,mats.steel,null,assembly)}
 for(const x of [-1.8,1.8])box(.24,.24,2.6,x,2.7,0,mats.lift,null,assembly);box(3.85,.25,.22,0,2.85,0,mats.lift,null,assembly);
 const load=box(.8,.25,.65,0,1.5,0,mats.battery,'Heavy module lifted by independent gantry, never by summed arm capacities',assembly);const rope=strut(new T.Vector3(0,2.72,0),new T.Vector3(0,1.63,0),.018,mats.steel,assembly);
 const ray=new T.Raycaster(),pointer=new T.Vector2();let down;renderer.domElement.addEventListener('pointerdown',e=>down={x:e.clientX,y:e.clientY});renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down.x,e.clientY-down.y)>5)return;const b=host.getBoundingClientRect();pointer.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(selectable).find(h=>{let o=h.object;while(o){if(!o.visible)return false;o=o.parent}return true});if(hit)onSelect(hit.object.userData.label)});
 let exploded=false,step=-1,state={},phase=0;function resize(){renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix()}new ResizeObserver(resize).observe(host);resize();
 renderer.setAnimationLoop(()=>{controls.update();phase+=.006;for(const m of modules){const target=m.base.clone().addScaledVector(m.offset,exploded?1:0);m.obj.position.lerp(target,.08)}if(step>=0){load.position.y=step===2?1.4:step>=3?.3:.15;}renderer.render(scene,camera)});
 return {renderer,update(s){state=s;platform.rotation.z=step>=0?0:s.slope*Math.PI/180;liftGroup.visible=s.variant==='field';modules.filter(m=>m.battery!==undefined).forEach(m=>m.obj.visible=s.variant==='field'||m.battery<8);document.querySelector('#scene-title').textContent=(s.variant==='field'?'Field-capable concept':'Workshop-assisted')+' / 6×6'},explode(){exploded=!exploded;return exploded},liftpoints(){points.forEach(p=>p.visible=!p.visible)},view(v){const a=v==='top'?[0,10,.01]:v==='side'?[0,2.0,8.8]:[6.7,5.7,7.9];camera.position.set(...a);controls.target.set(0,.65,0);controls.update()},assembly(n){step=n;assembly.visible=n>=0;platform.rotation.z=0;if(n>=0){camera.position.set(8,7,9);controls.target.set(0,.8,-1.3)}else controls.target.set(0,.65,0)}};
}
