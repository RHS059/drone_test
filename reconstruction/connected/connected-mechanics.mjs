import * as T from '../app/docs/vendor/three.core.js';
import{loadConnectedStructure}from './structure-scene.mjs';import{loadJointInterfaces}from './joint-scene.mjs';import{loadDriveInterfaces}from './drive-scene.mjs';import{loadDirectWheels}from './wheel-scene.mjs';import{loadGuidedShocks}from './shock-scene.mjs';import{solveConnectedMotion}from './connected-motion.mjs';
import{loadActuatorInterfaces}from '../steering-actuator/actuator-scene.mjs';
export async function loadConnectedMechanics(root,asset,source){
 const assembly=new T.Group();assembly.name='connected_six_corner_mechanics';
 const [structure,joints,drive,wheels,shocks,actuators]=await Promise.all([
  loadConnectedStructure(assembly,asset,source.structuralManifest,source.files.structure),
  loadJointInterfaces(assembly,asset,source.jointManifest,source.files.joints),
  loadDriveInterfaces(assembly,asset,source.driveContract,source.files.drive),
  loadDirectWheels(assembly,asset,source.wheelContract,source.files.wheel),
  loadGuidedShocks(assembly,asset,source.shockAnchors,source.files.shock,source.makeSpringProfile),
  loadActuatorInterfaces(assembly,asset,source.actuatorContract,{retentionOwner:'joints'})
 ]);
 let state;
 function update(inputs){
  const next=solveConnectedMotion(source.cornerPose,source.middlePose,inputs);
  // All modules are validated against their selected contracts at construction.
  // Invalid inputs fail in the solver before any component is updated.
  structure.update(next.groups);joints.update(next.groups);drive.update(next.corners);wheels.update(next.corners);shocks.update(next.poses);actuators.setRack('front',next.inputs.frontRack);actuators.setRack('rear',next.inputs.rearRack);state=next;
 }
 update({});root.add(assembly);
 return{assembly,structure,joints,drive,wheels,shocks,actuators,update,snapshot(){return{inputs:{...state.inputs},wheelCenters:Object.fromEntries(Object.entries(state.poses).map(([id,p])=>[id,p.wheelCenterM])),middleSuspension:state.middleSuspension,actuators:actuators.snapshot(),physicalOperationQualified:false};}};
}
