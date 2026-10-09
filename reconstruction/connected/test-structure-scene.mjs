import fs from 'node:fs';import assert from 'node:assert/strict';import * as T from '../app/docs/vendor/three.core.js';
import{readCad}from './read-original-glb.mjs';import{loadConnectedStructure,flattenConnectedGroups}from './structure-scene.mjs';import{connectedCornerTransforms,connectedMiddleTransforms}from './connected-transforms.mjs';
import{cornerPose,middlePose}from '../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R03.mjs';
const d=new URL('../../ugv-reconstruction/mechanical/connection_completion_C04/',import.meta.url),manifest=JSON.parse(fs.readFileSync(new URL('structural_connections_C04_R05_manifest.json',d))),root=new T.Group();
const rig=await loadConnectedStructure(root,async()=>readCad(new URL('structural_connections_C04_R05.glb',d)),manifest);let checks=0;
for(const q of[-Math.PI/15,0,Math.PI/15])for(const f of[-.075,0,.075])for(const r of[-.075,0,.075]){
 const poses={};for(const fore of[-1,0,1])for(const side of[-1,1]){const id=(fore<0?'rear':fore>0?'front':'middle')+'_'+(side>0?'left':'right');poses[id]=fore?connectedCornerTransforms(cornerPose,q,fore>0?f:r,side,fore):connectedMiddleTransforms(middlePose,q*side,side);}
 const groups=flattenConnectedGroups(poses,f,r);rig.update(groups);root.updateMatrixWorld(true);
 for(const b of rig.bindings){b.node.matrixWorld.elements.forEach((v,i)=>assert(Math.abs(v-groups[b.group][i])<1e-12));checks++;}
 const before=rig.bindings.map(b=>b.node.matrix.toArray()),bad=structuredClone(groups);bad.rear_right_fixed[12]+=.2;delete bad.front_rack;assert.throws(()=>rig.update(bad));assert.deepEqual(rig.bindings.map(b=>b.node.matrix.toArray()),before);
}
console.log(JSON.stringify({pass:true,actual_structural_nodes:rig.bindings.length,world_matrix_checks:checks,qualification:'Binding of R05 connected candidate; full assembly and visual review separate.'}));
