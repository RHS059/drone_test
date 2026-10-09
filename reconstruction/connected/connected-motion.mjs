import{connectedCornerTransforms,connectedMiddleTransforms}from './connected-transforms.mjs';
import{flattenConnectedGroups}from './structure-scene.mjs';
// One authoritative state drives every connected subsystem. Middle travel is
// held at neutral in the current viewer study; wheel spin is a kinematic input.
export function solveConnectedMotion(cornerPose,middlePose,{q=0,frontRack=0,rearRack=0,wheelAngle=0}={}){
 if(![q,frontRack,rearRack,wheelAngle].every(Number.isFinite))throw Error('Motion inputs must be finite');
 const corners={},poses={};
 for(const fore of[-1,0,1])for(const side of[-1,1]){
  const id=(fore<0?'rear':fore>0?'front':'middle')+'_'+(side>0?'left':'right');
  corners[id]=fore?connectedCornerTransforms(cornerPose,q,fore>0?frontRack:rearRack,side,fore,wheelAngle):connectedMiddleTransforms(middlePose,0,side,wheelAngle);
  poses[id]=corners[id].pose;
 }
 return{corners,poses,groups:flattenConnectedGroups(corners,frontRack,rearRack),inputs:{q,frontRack,rearRack,wheelAngle},middleSuspension:'held_at_neutral'};
}
