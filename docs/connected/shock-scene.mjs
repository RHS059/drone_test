import * as T from '../vendor/three.core.js';
import {assertRigidMatrix}from './rigid-matrix.mjs';
export function shockMatrices(pose,nominalLength){
 const upper=new T.Vector3(...pose.shockFixedM),lower=new T.Vector3(...pose.shockMovingM),z=lower.clone().sub(upper),length=z.length();
 if(!Number.isFinite(length)||length<.525-1e-9||length>.595+1e-9)throw Error('Shock outside guide-stop domain');
 z.normalize();const x=new T.Vector3(pose.side,0,0),y=new T.Vector3().crossVectors(z,x);
 const body=new T.Matrix4().makeBasis(x,y,z).setPosition(upper),rod=body.clone().multiply(new T.Matrix4().makeTranslation(0,0,length-nominalLength));
 const handed=new T.Matrix4().makeRotationZ(pose.side<0?Math.PI:0);
 const upperPin=new T.Matrix4().makeTranslation(...pose.shockFixedM).multiply(handed);
 const lowerPin=new T.Matrix4().makeTranslation(...pose.shockMovingM).multiply(new T.Matrix4().makeRotationX(pose.side*pose.q)).multiply(handed).multiply(new T.Matrix4().makeTranslation(0,0,-nominalLength));
 const matrices={shock_body:body,shock_rod:rod,upper_pin:upperPin,upper_clevis:upperPin,lower_pin:lowerPin,lower_clevis:lowerPin};
 for(const matrix of Object.values(matrices))assertRigidMatrix(matrix);
 return {matrices,length,spring:body.clone().multiply(new T.Matrix4().makeTranslation(0,0,.17))};
}
export async function loadGuidedShocks(root,asset,anchors,file,makeSpringProfile){
 const prototype=await asset(file),specs=new Map(anchors.nodes.map(n=>[n.node,n])),nodes=new Map();
 prototype.traverse(n=>{if(specs.has(n.name)){if(nodes.has(n.name))throw Error('Duplicate shock node');nodes.set(n.name,n);}});
 if(nodes.size!==24||specs.size!==24)throw Error('Expected24 selected guided shock nodes');
 const nominalLength=specs.get('shock_lower_eye_interface_C04_R01').origin_mm[2]/1000;
 const valid=new Set(['shock_body','shock_rod','upper_pin','upper_clevis','lower_pin','lower_clevis','spring_deformable']);
 if([...specs.values()].some(n=>!valid.has(n.motion_group)))throw Error('Unexpected shock motion group');
 const assembly=new T.Group(),instances=[];assembly.name='six_guided_spring_modules';
 for(const end of['rear','middle','front'])for(const side of[-1,1]){
  const id=end+'_'+(side>0?'left':'right'),groups={};
  for(const kind of valid){if(kind==='spring_deformable')continue;const g=new T.Group();g.name=id+'_'+kind;g.matrixAutoUpdate=false;groups[kind]=g;assembly.add(g);}
  for(const [name,spec]of specs){if(spec.motion_group==='spring_deformable')continue;const n=nodes.get(name).clone(true);n.name=id+'_'+name;groups[spec.motion_group].add(n);}
  const profile=makeSpringProfile(),geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.BufferAttribute(profile.positions,3));geometry.setAttribute('normal',new T.BufferAttribute(profile.normals,3));geometry.setIndex(new T.BufferAttribute(profile.indices,1));
  const spring=new T.Mesh(geometry,new T.MeshStandardMaterial({color:0x29488a,metalness:.6,roughness:.4}));spring.name=id+'_source_dimensioned_spring';spring.matrixAutoUpdate=false;assembly.add(spring);
  instances.push({id,groups,spring,profile});
 }
 root.add(assembly);
 return {assembly,instances,update(poses){
  const pending=instances.map(i=>{const pose=poses[i.id];if(!pose)throw Error('Missing shock pose');return[i,shockMatrices(pose,nominalLength)];});
  for(const [i,p]of pending){for(const [kind,m]of Object.entries(p.matrices)){i.groups[kind].matrix.copy(m);i.groups[kind].matrixWorldNeedsUpdate=true;}i.spring.matrix.copy(p.spring);i.spring.matrixWorldNeedsUpdate=true;i.profile.setSeatLengthM(p.length-.225);i.spring.geometry.attributes.position.needsUpdate=true;i.spring.geometry.attributes.normal.needsUpdate=true;i.spring.geometry.computeBoundingSphere();}
 }};
}
