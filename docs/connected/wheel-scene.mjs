import {assertRigidMatrix} from './rigid-matrix.mjs';
import * as T from '../vendor/three.core.js';
export async function loadDirectWheels(root,asset,contract,file){
  if(contract.nominal_radius_m!==.4155||contract.mount_face_center_m?.[1]!==-.07||contract.drive_adapter_required!==false)throw Error('Unexpected direct wheel contract');
  const prototype=await asset(file), named=new Set();prototype.traverse(n=>{if(contract.named_components.includes(n.name)){if(named.has(n.name))throw Error('Duplicate wheel component');named.add(n.name);}});
  if(named.size!==2)throw Error('Wheel must include the actual rim and tire');
  const assembly=new T.Group();assembly.name='six_direct_wheels';root.add(assembly);const instances=[];
  for(const x of [-1.35,0,1.35])for(const side of[-1,1]){
    const id=(x<0?'rear':x>0?'front':'middle')+'_'+(side>0?'left':'right');
    const moving=new T.Group();moving.name=id+'_wheel_spin';moving.matrixAutoUpdate=false;
    const local=prototype.clone(true);local.name=id+'_wheel';local.matrixAutoUpdate=false;
    const sourceToC=new T.Matrix4().makeTranslation(x,side*.998,-.25).multiply(new T.Matrix4().makeRotationZ(side<0?Math.PI:0));
    local.matrix.copy(sourceToC);moving.add(local);assembly.add(moving);instances.push({id,x,side,moving,local,sourceToC});
  }
  return {assembly,instances,update(transforms){
    const pending=instances.map(i=>{const v=transforms[i.id]?.spin;if(!v)throw Error('Missing wheel pose');const m=new T.Matrix4().fromArray(v);assertRigidMatrix(m);return[i.moving,m];});
    for(const [node,matrix]of pending){node.matrix.copy(matrix);node.matrixWorldNeedsUpdate=true;}
  }};
}
