import fs from'node:fs';import assert from'node:assert/strict';import{solveConnectedMotion}from'./connected-motion.mjs';
import{cornerPose,middlePose}from'../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R03.mjs';
const d=new URL('../../ugv-reconstruction/mechanical/connection_completion_C04/',import.meta.url),j=JSON.parse(fs.readFileSync(new URL('joints/rover_joint_hardware_nominal_C04_R02_manifest.json',d))),s=JSON.parse(fs.readFileSync(new URL('structural_connections_C04_R05_manifest.json',d)));
let checks=0;for(const q of[-Math.PI/15,0,Math.PI/15])for(const f of[-.075,0,.075])for(const r of[-.075,0,.075]){
 const state=solveConnectedMotion(cornerPose,middlePose,{q,frontRack:f,rearRack:r,wheelAngle:.5});
 for(const spec of[...j.nodes,...s.assembly_nodes]){assert(state.groups[spec.motion_group]);checks++;}
 for(const side of['left','right'])assert.equal(state.poses['middle_'+side].q,0);
}
for(const field of['q','frontRack','rearRack','wheelAngle'])assert.throws(()=>solveConnectedMotion(cornerPose,middlePose,{[field]:NaN}));
console.log(JSON.stringify({pass:true,selected_joint_and_structure_group_checks:checks,middle_held_at_neutral:true}));
