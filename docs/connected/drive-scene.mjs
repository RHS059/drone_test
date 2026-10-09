import {assertRigidMatrix} from './rigid-matrix.mjs';
import * as T from '../vendor/three.core.js';

// Original external drive-interface CAD, local +Z inboard and wheel face Z=0.
// The purchased drive's internal rotor/bearing geometry is not supplied here.
export async function loadDriveInterfaces(root, asset, contract, file) {
  const prototype = await asset(file);
  const specifications = new Map(contract.nodes.map(n => [n.node, n]));
  if (specifications.size !== 20) throw Error('Expected the selected 20-part direct-drive interface');
  if(contract.nodes.some(n=>!['steer','spin'].includes(n.group)))throw Error('Unknown drive motion group');
  const sourceNodes = new Map();
  prototype.traverse(node => {
    if (specifications.has(node.name)) {
      if (sourceNodes.has(node.name)) throw Error('Duplicate drive node: '+node.name);
      sourceNodes.set(node.name,node);
    }
  });
  if (sourceNodes.size !== specifications.size) throw Error('Drive CAD does not match its contract');
  const assembly = new T.Group(); assembly.name='six_direct_drive_interfaces';
  const instances=[];
  for (const x of [-1.35,0,1.35]) for (const side of [-1,1]) {
    const id=(x<0?'rear':x>0?'front':'middle')+'_'+(side>0?'left':'right');
    const sourceToC = new T.Matrix4().makeTranslation(x,0,0)
      .multiply(new T.Matrix4().makeRotationZ(side<0?Math.PI:0))
      .multiply(new T.Matrix4().makeTranslation(0,.928,-.25))
      .multiply(new T.Matrix4().makeRotationX(Math.PI/2));
    const groups={};
    for(const kind of ['steer','spin']) {
      const moving=new T.Group();moving.name=id+'_drive_'+kind; moving.matrixAutoUpdate=false;
      const local=new T.Group();local.matrixAutoUpdate=false;local.matrix.copy(sourceToC);
      moving.add(local);assembly.add(moving);groups[kind]={moving,local};
    }
    for(const [name,spec] of specifications) {
      if(!groups[spec.group])throw Error('Unknown drive motion group: '+spec.group);
      const part=sourceNodes.get(name).clone(true);part.name=id+'_'+name;
      groups[spec.group].local.add(part);
    }
    instances.push({id,x,side,groups,sourceToC});
  }
  root.add(assembly);
  return {assembly,instances,
    update(transforms) {
      const pending=[];
      for(const instance of instances) {
        const matrices=transforms[instance.id];
        if(!matrices?.steer||!matrices?.spin)throw Error('Missing drive pose: '+instance.id);
        for(const kind of ['steer','spin']) {
          const m=new T.Matrix4().fromArray(matrices[kind]);
          assertRigidMatrix(m);
          pending.push([instance.groups[kind].moving,m]);
        }
      }
      for(const [node,matrix] of pending){node.matrix.copy(matrix);node.matrixWorldNeedsUpdate=true;}
    }
  };
}
