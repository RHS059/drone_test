import{bindMainPairGraph}from'./connected/main-pair-graph.mjs';
import{loadConnectedElectrical}from'./connected/electrical-scene.mjs';
import{solveConnectedMotion}from'./connected/connected-motion.mjs';
import{loadConnectedBody}from'./connected/body-scene.mjs';
import{loadConnectedMechanics}from'./connected/connected-mechanics.mjs';
import{cornerPose,middlePose}from'./connected/kinematics_C04_R03.mjs';
import{makeSpringProfile}from'./connected/spring_profile_runtime_C04_R08.mjs';
// Connected development assembly; electrical qualification remains open.
export async function loadRover(root,asset){
 const get=async p=>{const r=await fetch(p);if(!r.ok)throw Error('Missing connected component contract: '+p);return r.json();},P='./assets/connected/';
 const [structuralManifest,jointManifest,driveContract,wheelContract,shockAnchors,actuatorContract]=await Promise.all(['structure.json','joints.json','drive.json','wheel.json','shock.json','actuator.json'].map(n=>get(P+n)));
 const rig=await loadConnectedMechanics(root,asset,{cornerPose,middlePose,makeSpringProfile,structuralManifest,jointManifest,driveContract,wheelContract,shockAnchors,actuatorContract,files:{structure:P+'structure.glb.gz',joints:P+'joints.glb.gz',drive:P+'drive.glb.gz',wheel:P+'wheel.glb.gz',shock:P+'shock.glb.gz'}});
 const bodyContract=await get('./assets/connected-body/body-contract.json');
 const connectedBody=await loadConnectedBody(root,asset,{contract:bodyContract});const body=connectedBody.assembly;
 const removable=connectedBody.snapshot().service.removable;
 const electricalContract=await get('./assets/connected-electrical/electrical-contract.json');const electrical=await loadConnectedElectrical(root,asset,{contract:electricalContract});
 const mainPairGraph=bindMainPairGraph(root,await get('./assets/main-pair-E05/main_routes_E05/main_pair_graph_E05.json'));
 for(const [module,label]of[[rig.structure.assembly,'Original connected suspension and rack support'],[rig.joints.assembly,'Retained bearing, rod end or fastener'],[rig.drive.assembly,'Source-dimensioned direct-drive external interface'],[rig.wheels.assembly,'Jantsa rim / Trelleborg tire dimensional model'],[rig.shocks.assembly,'Guided spring and damper mounting study']])module.traverse(n=>{if(n.isMesh)n.userData.label=label;});
 let q=0,frontRack=0,rearRack=0,wheelAngle=0,motionStudy=false,serviceOpen=false;
 function applyMotion(state){const solved=solveConnectedMotion(cornerPose,middlePose,state);rig.update(state);electrical.update(solved);}
 function update(){applyMotion({q,frontRack,rearRack,wheelAngle});root.position.z=motionStudy?.8655:.6655;}
 const steering={contract:{configuration:'C04 connected mechanical development'},assembly:rig.assembly,snapshot(){const s=rig.snapshot();return{rackPositionsM:{front:frontRack,rear:rearRack},suspensionRad:q,corners:Object.fromEntries(['front_left','front_right','rear_left','rear_right'].map(id=>{const side=id.endsWith('left')?1:-1,fore=id.startsWith('front')?1:-1;return[id,cornerPose(q,fore>0?frontRack:rearRack,side,fore)];}))};}};
 update();
 return{mainPairGraph,rig,steering,bodyContract,electrical,connectedBody,
  setRack(end,v){if(!['front','rear'].includes(end))throw Error('Unknown steering axle');const next={q,frontRack,rearRack,wheelAngle,[end+'Rack']:v};applyMotion(next);frontRack=next.frontRack;rearRack=next.rearRack;},
  setWheelAngle(v){applyMotion({q,frontRack,rearRack,wheelAngle:v});wheelAngle=v;},
  setMotionStudy(v){motionStudy=Boolean(v);if(!v)q=0;update();},
  setSuspension(v){if(v!==0&&!motionStudy)throw Error('Enable unloaded motion study first');applyMotion({q:v,frontRack,rearRack,wheelAngle});q=v;},
  homeSteering(){q=0;frontRack=0;rearRack=0;wheelAngle=0;motionStudy=false;update();},
  setWorkshop(v){if(v)throw Error('Revised workshop support placement has not been checked for this assembly');},
  setCradle(){},showBody(v){body.visible=v;},showCorners(v){rig.assembly.visible=v;},openService(v){serviceOpen=v;connectedBody.setServiceOpen(v);},
  snapshot(){return{mainPairGraph:mainPairGraph.snapshot(),electrical:electrical.snapshot(),body:connectedBody.snapshot(),assemblyRevision:'C04 connected development',wheelAngleRad:wheelAngle,workshop:false,workshopAvailable:false,motionStudy,chassisDisplayOffsetM:motionStudy?.2:0,cradleStation:'left_1',fixtureLoadRating:null,nominalWheelCentersC:[...rig.wheels.instances].map(i=>[i.x,i.side*.998,-.25]),wheelCentersC:Object.values(rig.snapshot().wheelCenters),wheelDiameter:.831,groundLift:root.position.z,cornerCount:6,serviceOpen,removableNodes:removable.length,steering:steering.snapshot(),suspensionTravel:motionStudy?'four steering corners: unloaded kinematic study; middle pair held neutral':'held at neutral',physicalOperationQualified:false};}
 };
}
