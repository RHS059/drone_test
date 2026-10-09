import fs from 'node:fs';import assert from 'node:assert/strict';import * as T from '../app/docs/vendor/three.core.js';
import {loadDriveInterfaces}from './drive-scene.mjs';import{loadDirectWheels}from './wheel-scene.mjs';import{readCad}from './read-original-glb.mjs';
import {connectedCornerTransforms,connectedMiddleTransforms}from './connected-transforms.mjs';
import{cornerPose,middlePose}from '../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R02.mjs';
const d=new URL('../../ugv-reconstruction/mechanical/connection_completion_C04/drive/',import.meta.url),w=new URL('../wheel-drive-hardware/model-16p5/',import.meta.url);
const dc=JSON.parse(fs.readFileSync(new URL('direct_drive_contract_C04_R03.json',d))),wc=JSON.parse(fs.readFileSync(new URL('interface_contract.json',w))),root=new T.Group();
const drive=await loadDriveInterfaces(root,async()=>readCad(new URL('direct_drive_connections_C04_R03.glb',d)),dc),wheels=await loadDirectWheels(root,async()=>readCad(new URL('wheel_W16_R01.glb',w)),wc);
let checks=0;
for(const q of[-Math.PI/15,0,Math.PI/15])for(const f of[-.075,0,.075])for(const r of[-.075,0,.075])for(const spin of[0,.73,Math.PI]){
 const poses=Object.fromEntries(wheels.instances.map(i=>[i.id,i.x===0?connectedMiddleTransforms(middlePose,q*i.side,i.side,spin):connectedCornerTransforms(cornerPose,q,i.x>0?f:r,i.side,Math.sign(i.x),spin)]));
 drive.update(poses);wheels.update(poses);root.updateMatrixWorld(true);
 for(const wi of wheels.instances){const di=drive.instances.find(i=>i.id===wi.id);
  const face=new T.Vector3(...wc.mount_face_center_m).applyMatrix4(wi.local.matrixWorld),hub=new T.Vector3().applyMatrix4(di.groups.spin.local.matrixWorld);assert(face.distanceTo(hub)<1e-12);checks++;
  for(let j=0;j<5;j++){
   const s=dc.nodes.find(n=>n.node===`drive_input_stud_${j}_C04_R02`),b=s.bounds_mm;
   const stud=new T.Vector3((b[0]+b[3])/2000,(b[1]+b[4])/2000,0).applyMatrix4(di.groups.spin.local.matrixWorld);
   const hole=new T.Vector3(...wc.lug_centers_mount_face_m[j]).applyMatrix4(wi.local.matrixWorld);assert(stud.distanceTo(hole)<1e-12);checks++;
  }
 }
 // A late missing corner must not update any earlier corner partially.
 const before=drive.instances.map(i=>i.groups.spin.moving.matrix.toArray());const bad=structuredClone(poses);for(const kind of ['steer','spin']){const m=new T.Matrix4().fromArray(bad.rear_right[kind]);m.elements[12]+=.123;bad.rear_right[kind]=m.toArray();}delete bad.front_left;
 assert.throws(()=>drive.update(bad));assert.deepEqual(drive.instances.map(i=>i.groups.spin.moving.matrix.toArray()),before);
 const wb=wheels.instances.map(i=>i.moving.matrix.toArray());assert.throws(()=>wheels.update(bad));assert.deepEqual(wheels.instances.map(i=>i.moving.matrix.toArray()),wb);
}
console.log(JSON.stringify({pass:true,actual_asset_face_and_five_stud_bindings:checks,atomic_update_failures_checked:162,qualification:'Nominal render attachment only; source seat application, tolerances, threads and loads remain open.'}));
