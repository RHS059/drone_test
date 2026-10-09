import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as T from '../app/docs/vendor/three.core.js';
import {loadDriveInterfaces} from './drive-scene.mjs';
import {readCad} from './read-original-glb.mjs';
import {connectedCornerTransforms,connectedMiddleTransforms} from './connected-transforms.mjs';
import {cornerPose,middlePose} from '../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R02.mjs';
const directory=new URL('../../ugv-reconstruction/mechanical/connection_completion_C04/drive/',import.meta.url);
const contract=JSON.parse(fs.readFileSync(new URL('direct_drive_contract_C04_R03.json',directory)));
const root=new T.Group();
const rig=await loadDriveInterfaces(root,async()=>readCad(new URL('direct_drive_connections_C04_R03.glb',directory)),contract);
assert.equal(rig.instances.length,6);
let meshes=0;root.traverse(n=>{if(n.isMesh){assert(n.geometry.attributes.position.count>0);meshes++;}});assert.equal(meshes,120);
let checks=0;
for(const q of [-Math.PI/15,0,Math.PI/15])for(const front of [-.075,0,.075])for(const rear of [-.075,0,.075])for(const angle of [0,.7,Math.PI]) {
  const poses={};
  for(const i of rig.instances)poses[i.id]=i.x===0?connectedMiddleTransforms(middlePose,q*i.side,i.side,angle):connectedCornerTransforms(cornerPose,q,i.x>0?front:rear,i.side,Math.sign(i.x),angle);
  rig.update(poses);root.updateMatrixWorld(true);
  for(const i of rig.instances) {
    for(const spec of contract.nodes) {
      const node=root.getObjectByName(i.id+'_'+spec.node);assert(node);
      const expected=new T.Matrix4().fromArray(poses[i.id][spec.group]).multiply(i.sourceToC);
      node.matrixWorld.elements.forEach((x,j)=>assert(Math.abs(x-expected.elements[j])<1e-12));
      checks++;
    }
    // Shared wheel-plane center is invariant under rotor spin, including steer.
    const a=new T.Vector3(0,0,0).applyMatrix4(i.groups.steer.local.matrixWorld);
    const b=new T.Vector3(0,0,0).applyMatrix4(i.groups.spin.local.matrixWorld);
    assert(a.distanceTo(b)<1e-12);
    if(i.x===0){
      const expected=middlePose(q*i.side,i.side);
      assert(a.distanceTo(new T.Vector3(0,i.side*.928,-.25).add(new T.Vector3(...expected.uprightDeltaM)))<1e-12);
    }
  }
}
assert.throws(()=>rig.update({}));
const badContract=structuredClone(contract);badContract.nodes.at(-1).group='invalid';const cleanRoot=new T.Group();await assert.rejects(()=>loadDriveInterfaces(cleanRoot,async()=>readCad(new URL('direct_drive_connections_C04_R03.glb',directory)),badContract));assert.equal(cleanRoot.children.length,0);
console.log('PASS: 120 actual drive-interface CAD nodes,',checks,'world-matrix bindings across combined steering/suspension/spin cases, including opposite middle suspension angles. Stators and mounting screws remain upright-bound; hubs, studs and nuts rotate together. This is binding evidence, not clearance, UI travel approval or bearing/load qualification.');
