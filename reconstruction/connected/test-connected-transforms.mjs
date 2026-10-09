import assert from'node:assert/strict';import{Matrix4,Vector3}from'../app/docs/vendor/three.core.js';
import{cornerPose}from'../../ugv-reconstruction/mechanical/connection_completion_C04/kinematics_C04_R01.mjs';
import{connectedCornerTransforms}from'./connected-transforms.mjs';
const point=(m,p)=>new Vector3(...p).applyMatrix4(new Matrix4().fromArray(m));let cases=0;
for(const q of[-Math.PI/15,0,Math.PI/15])for(const r of[-.075,0,.075])for(const side of[-1,1])for(const fore of[-1,1])for(const angle of[0,Math.PI/2,Math.PI,2*Math.PI]){
 const s=connectedCornerTransforms(cornerPose,q,r,side,fore,angle),p=s.pose;
 assert(point(s.wheel,[0,0,0]).distanceTo(new Vector3(...p.wheelCenterM))<1e-12);
 // Spinning the hub must leave every point on the common axle unchanged.
 const hubNominal=[fore*1.35,side*.928,-.25];assert(point(s.spin,hubNominal).distanceTo(point(s.upright,hubNominal))<1e-12);
 // An off-axis hub witness and its coincident wheel witness remain attached.
 const worldWitness=[fore*1.35+.05,side*.998,-.25];const localWitness=side>0?[.05,0,0]:[-.05,0,0];assert(point(s.spin,worldWitness).distanceTo(point(s.wheel,localWitness))<1e-12);
 const wheelAxis=new Vector3(0,1,0).transformDirection(new Matrix4().fromArray(s.wheel));assert(wheelAxis.distanceTo(new Vector3(...p.wheelAxis))<1e-12);
 for(const kind of['fixed','upper','lower','upright','spin','tie','rack','wheel'])assert(Math.abs(new Matrix4().fromArray(s[kind]).determinant()-1)<1e-12);
 cases++;
}
assert.throws(()=>connectedCornerTransforms(cornerPose,0,0,1,1,NaN));
console.log('PASS',cases,'combined C04 q/r/side/end/wheel-rotation transform states: selected wheel centers, common hub axis, coincident interface witnesses and positive determinants. Actual new mesh/contact/retention acceptance remains separate.');
