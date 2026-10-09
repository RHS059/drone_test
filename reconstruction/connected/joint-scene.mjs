import {assertRigidMatrix} from './rigid-matrix.mjs';
import * as T from '../app/docs/vendor/three.core.js';

// Each source node already carries its prototype-to-nominal-Vehicle-C matrix.
// Apply the solved motion on the LEFT of that matrix, preserving the source
// placement. Balls and races deliberately use distinct motion groups.
export async function loadJointInterfaces(root,asset,manifest,file){
 const assembly=await asset(file);assembly.name='connected_joint_hardware';
 const specs=manifest.nodes,names=new Set(specs.map(n=>n.node));
 if(specs.some(n=>n.include===false)||assembly.children.length!==specs.length)throw Error('Joint payload must match the complete selected node schedule');
 if(names.size!==specs.length)throw Error('Duplicate joint contract names');
 const bindings=[];
 for(const spec of specs){
   const node=assembly.getObjectByName(spec.node);
   if(!node||node.parent!==assembly)throw Error('Missing or nested joint node: '+spec.node);
   if(node.matrixAutoUpdate)node.updateMatrix();const nominal=node.matrix.clone();
   assertRigidMatrix(nominal);
   node.matrixAutoUpdate=false;
   bindings.push({node,nominal,group:spec.motion_group});
 }
 root.add(assembly);
 return{assembly,bindings,update(groups){
   const prepared=new Map();
   for(const {group} of bindings){
     if(prepared.has(group))continue;
     if(!groups[group])throw Error('Missing joint motion group: '+group);
     const matrix=new T.Matrix4().fromArray(groups[group]);
     assertRigidMatrix(matrix);
     prepared.set(group,matrix);
   }
   for(const {node,nominal,group} of bindings){node.matrix.copy(prepared.get(group)).multiply(nominal);node.matrixWorldNeedsUpdate=true;}
 }};
}
