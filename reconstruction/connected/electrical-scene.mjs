import * as T from '../app/docs/vendor/three.core.js';
import{applyNamedPartPatch}from'./named-part-patch.mjs';import{assertRigidMatrix}from'./rigid-matrix.mjs';
export async function loadConnectedElectrical(root,asset,{contract,basePath='./assets/connected-electrical/'}={}){
 if(!contract?.selected_modules)throw Error('Missing electrical component contract');
 const files=['carriers','deck-fasteners','lynx','isolators','breakout','breakout-fasteners','ur-cases','controllers'];
 const [carriers,deck,lynx,isolators,breakout,fasteners,reservations,controllers]=await Promise.all(files.map(n=>asset(basePath+n+'.glb.gz','Electrical interface: source and qualification details available')));
 const patch=contract.selected_modules.find(m=>m.module==='lynx_E04');applyNamedPartPatch(carriers,lynx,patch.changes);
 const assembly=new T.Group();assembly.name='electrical_components';assembly.add(carriers,deck,isolators,controllers);
 const ur=new T.Group();ur.name='unretained_UR_controller_cases';for(const name of contract.unretained_UR_case_names){const n=reservations.getObjectByName(name);if(!n)throw Error('Missing UR controller dimensional case');const c=n.clone(true);c.traverse(x=>{if(x.isMesh)x.userData.label='UR controller case: mounting and cable interfaces unresolved';});ur.add(c);}assembly.add(ur);
 const moving=[];
 for(const x of[-1.35,0,1.35])for(const side of[-1,1]){
  const id=(x<0?'rear':x>0?'front':'middle')+'_'+(side>0?'left':'right');
  const motion=new T.Group();motion.name=id+'_electrical_breakout';motion.matrixAutoUpdate=false;
  const source=new T.Group();source.matrixAutoUpdate=false;source.matrix.makeTranslation(x,0,0).multiply(new T.Matrix4().makeRotationZ(side<0?Math.PI:0));
  source.add(breakout.clone(true),fasteners.clone(true));motion.add(source);assembly.add(motion);moving.push({id,motion,source});
 }
 root.add(assembly);return{assembly,moving,carriers,update(solution){const changes=moving.map(i=>{const a=solution.corners?.[i.id]?.upright;if(!a)throw Error('Missing breakout pose');const m=new T.Matrix4().fromArray(a);assertRigidMatrix(m);return[i.motion,m];});for(const[n,m]of changes){n.matrix.copy(m);n.matrixWorldNeedsUpdate=true;}},snapshot(){return{breakouts:moving.length,unretainedURCases:2,fullHarnessComplete:false,physicalElectricalContinuityVerified:false};}};
}
