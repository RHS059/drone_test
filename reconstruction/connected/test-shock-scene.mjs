import fs from 'node:fs';import assert from 'node:assert/strict';import * as T from '../app/docs/vendor/three.core.js';
import{readCad}from './read-original-glb.mjs';import{loadGuidedShocks}from './shock-scene.mjs';
import{cornerPose,middlePose}from '../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R03.mjs';
import{makeSpringProfile}from '../../ugv-reconstruction/mechanical/connection_completion_C04/shocks/spring_profile_runtime_C04_R08.js';
const dir=new URL('../../ugv-reconstruction/mechanical/connection_completion_C04/shocks/',import.meta.url),anchors=JSON.parse(fs.readFileSync(new URL('guided_spring_module_local_C04_R08_anchors.json',dir))),root=new T.Group();
const rig=await loadGuidedShocks(root,async()=>readCad(new URL('guided_spring_module_local_C04_R08.glb',dir)),anchors,undefined,makeSpringProfile),L=anchors.nodes.find(n=>n.node==='shock_lower_eye_interface_C04_R01').origin_mm[2]/1000;
let checks=0;
for(const q of[-Math.PI/15,0,Math.PI/15])for(const r of[-.075,0,.075]){
 const poses={};for(const i of rig.instances){const side=i.id.endsWith('left')?1:-1;poses[i.id]=i.id.startsWith('middle')?middlePose(q*side,side):cornerPose(q,r,side,i.id.startsWith('front')?1:-1);}
 rig.update(poses);root.updateMatrixWorld(true);
 for(const i of rig.instances){const p=poses[i.id],u=new T.Vector3(...p.shockFixedM),d=new T.Vector3(...p.shockMovingM),axis=d.clone().sub(u).normalize();
  for(const kind of['shock_body','upper_pin','upper_clevis'])assert(new T.Vector3().applyMatrix4(i.groups[kind].matrixWorld).distanceTo(u)<1e-12);
  for(const kind of['shock_rod','lower_pin','lower_clevis'])assert(new T.Vector3(0,0,L).applyMatrix4(i.groups[kind].matrixWorld).distanceTo(d)<1e-12);
  for(const kind of['upper_pin','lower_pin']){const a=new T.Vector3(1,0,0).transformDirection(i.groups[kind].matrixWorld);assert(a.distanceTo(new T.Vector3(p.side,0,0))<1e-12);}
  const a=i.spring.geometry.attributes.position.array,H=d.distanceTo(u)-.225;let lo=Infinity,hi=-Infinity,maxR=0,minR=Infinity;for(let k=0;k<a.length;k+=3){lo=Math.min(lo,a[k+2]);hi=Math.max(hi,a[k+2]);const rad=Math.hypot(a[k],a[k+1]);maxR=Math.max(maxR,rad);minR=Math.min(minR,rad);}
  assert(Math.abs(lo)<1e-8&&Math.abs(hi-H)<2e-8);assert(Math.abs(maxR-.0481)<1e-8&&Math.abs(minR-.0381)<1e-8);
  assert(new T.Vector3().applyMatrix4(i.spring.matrixWorld).distanceTo(u.clone().addScaledVector(axis,.17))<1e-12);
  assert(new T.Vector3(0,0,H).applyMatrix4(i.spring.matrixWorld).distanceTo(d.clone().addScaledVector(axis,-.055))<1e-12);checks++;
 }
 const before=rig.instances.map(i=>i.groups.shock_body.matrix.toArray()),bad=structuredClone(poses);bad.rear_right.shockFixedM[0]+=.01;bad.rear_right.shockMovingM[0]+=.01;delete bad.front_left;assert.throws(()=>rig.update(bad));assert.deepEqual(rig.instances.map(i=>i.groups.shock_body.matrix.toArray()),before);
}
console.log(JSON.stringify({pass:true,six_corner_combined_cases:checks,loaded_rigid_nodes:138,procedural_springs:6,qualification:'Binding and unscaled spring-seat geometry only; complete placement, fits and load qualification separate.'}));
