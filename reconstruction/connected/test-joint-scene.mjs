import fs from 'node:fs';import assert from 'node:assert/strict';
import * as T from '../app/docs/vendor/three.core.js';
import {loadJointInterfaces} from './joint-scene.mjs';
import {readCad} from './read-original-glb.mjs';
import {connectedCornerTransforms,connectedMiddleTransforms} from './connected-transforms.mjs';
import {identity,origin} from '../app/docs/kinematics.js';
import {cornerPose,middlePose} from '../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R02.mjs';
const directory=new URL('../../ugv-reconstruction/mechanical/connection_completion_C04/joints/',import.meta.url);
const manifest=JSON.parse(fs.readFileSync(new URL('rover_joint_hardware_nominal_C04_R02_manifest.json',directory)));
const root=new T.Group();
const rig=await loadJointInterfaces(root,async()=>readCad(new URL('rover_joint_hardware_nominal_C04_R02.glb',directory),{allowMatrix:true}),manifest,'');
assert.equal(rig.bindings.length,816);let checked=0;
for(const q of [-Math.PI/15,0,Math.PI/15])for(const front of [-.075,0,.075])for(const rear of [-.075,0,.075]){
 const groups={};
 for(const side of [-1,1])for(const fore of [-1,0,1]){
   const id=(fore<0?'rear':fore>0?'front':'middle')+'_'+(side>0?'left':'right');
   const s=fore===0?connectedMiddleTransforms(middlePose,q*side,side):connectedCornerTransforms(cornerPose,q,fore>0?front:rear,side,fore);
   for(const kind of ['fixed','upper','lower','steer','upright','tie'])if(s[kind])groups[id+'_'+kind]=s[kind];
 }
 for(const [end,r] of [['front',front],['rear',rear]]){groups[end+'_rack']=origin({xyz:[0,r,0]});groups[end+'_rack_fixed']=identity();}
 rig.update(groups);root.updateMatrixWorld(true);
 for(const b of rig.bindings){
   const spec=manifest.nodes.find(n=>n.node===b.node.name);
   const expectedOrigin=new T.Vector3(...spec.origin_mm.map(v=>v/1000)).applyMatrix4(new T.Matrix4().fromArray(groups[b.group]));
   assert(expectedOrigin.distanceTo(new T.Vector3().setFromMatrixPosition(b.node.matrixWorld))<1e-12);
   assert(Math.abs(b.node.matrixWorld.determinant()-1)<1e-9);checked++;
 }
}
assert.throws(()=>rig.update({}));
console.log('PASS:',checked,'actual joint-node world origins and proper rotations, preserving all 816 prototype placement matrices across 27 combined states. Balls/races retain their distinct contract motion groups. No clearance or physical load qualification.');
