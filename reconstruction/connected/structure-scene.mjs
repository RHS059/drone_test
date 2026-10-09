import * as T from '../app/docs/vendor/three.core.js';import{assertRigidMatrix}from './rigid-matrix.mjs';
export async function loadConnectedStructure(root,asset,manifest,file){
 const assembly=await asset(file),specs=manifest.assembly_nodes;
 if(!Array.isArray(specs)||new Set(specs.map(s=>s.node)).size!==specs.length||assembly.children.length!==specs.length)throw Error('Structural CAD node schedule mismatch');
 const bindings=[];
 for(const s of specs){
  if(s.baked_geometry_frame!=='vehicle_C_nominal_mm')throw Error('Unsupported structure frame');
  const n=assembly.children.find(n=>n.name===s.node);if(!n)throw Error('Missing structural node');
  if(n.matrixAutoUpdate)n.updateMatrix();assertRigidMatrix(n.matrix);
  if(n.matrix.elements.some((v,i)=>Math.abs(v-(i%5===0?1:0))>1e-12))throw Error('Baked structural CAD must not carry an extra placement');
  bindings.push({node:n,group:s.motion_group});
 }
 for(const b of bindings)b.node.matrixAutoUpdate=false;
 assembly.name='connected_original_structure';root.add(assembly);
 return{assembly,bindings,update(groups){
  const matrices=new Map();for(const {group}of bindings){if(matrices.has(group))continue;if(!groups[group])throw Error('Missing structural motion group: '+group);const m=new T.Matrix4().fromArray(groups[group]);assertRigidMatrix(m);matrices.set(group,m);}
  for(const {node,group}of bindings){node.matrix.copy(matrices.get(group));node.matrixWorldNeedsUpdate=true;}
 }};
}
export function flattenConnectedGroups(corners,frontRack,rearRack){
 if(!Number.isFinite(frontRack)||!Number.isFinite(rearRack)||Math.abs(frontRack)>.075||Math.abs(rearRack)>.075)throw Error('Invalid rack displacement');
 const groups={};for(const[id,c]of Object.entries(corners))for(const k of['fixed','upper','lower','upright','steer','tie'])if(c[k])groups[id+'_'+k]=c[k];
 for(const[end,rack]of[['front',frontRack],['rear',rearRack]]){groups[end+'_rack']=new T.Matrix4().makeTranslation(0,rack,0).toArray();groups[end+'_rack_fixed']=new T.Matrix4().toArray();}
 return groups;
}
