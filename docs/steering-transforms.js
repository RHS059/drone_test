import{cornerPose}from'./assets/steering/kinematics_C03_R01.js';
import{identity,origin,rotation,multiply}from'./kinematics.js';
const add=(a,b)=>a.map((x,i)=>x+b[i]),sub=(a,b)=>a.map((x,i)=>x-b[i]);
const norm=a=>Math.hypot(...a),dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const translate=v=>origin({xyz:v});
export function pivotRotation(axis,angle,pivot){return multiply(multiply(translate(pivot),rotation(axis,angle)),translate(pivot.map(x=>-x)));}
export function alignVectors(a,b){const u=a.map(x=>x/norm(a)),v=b.map(x=>x/norm(b)),c=Math.max(-1,Math.min(1,dot(u,v))),axis=cross(u,v);if(norm(axis)<1e-12){if(c>0)return identity();const basis=Math.abs(u[0])<.8?[1,0,0]:[0,1,0];return rotation(cross(u,basis),Math.PI)}return rotation(axis,Math.acos(c));}
export function steeringTransforms(q,r,side,fore){
 const pose=cornerPose(q,r,side,fore),zero=cornerPose(0,0,side,fore);
 const upright=multiply(translate(pose.uprightDeltaM),pivotRotation([0,0,1],pose.steerRad,pose.nominalKingpinM));
 const tie=multiply(multiply(translate(pose.tieInnerM),alignVectors(sub(zero.tieOuterM,zero.tieInnerM),sub(pose.tieOuterM,pose.tieInnerM))),translate(zero.tieInnerM.map(x=>-x)));
 const wheel=multiply(upright,origin({xyz:[fore*1.35,side*.94,-.25],rpy:[0,0,side<0?Math.PI:0]}));
 return{pose,zero,fixed:identity(),upper:pivotRotation([1,0,0],pose.armWorldRx,pose.upperPivotM),lower:pivotRotation([1,0,0],pose.armWorldRx,pose.lowerPivotM),steer:upright,spin:upright,tie,rack:translate([0,r,0]),wheel};
}
export function transformPoint(m,p){return[0,1,2].map(i=>m[i]*p[0]+m[4+i]*p[1]+m[8+i]*p[2]+m[12+i]);}
