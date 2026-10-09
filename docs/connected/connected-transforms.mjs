import {identity,origin,rotation,multiply} from '../kinematics.js';
const translation=v=>origin({xyz:v});
const sub=(a,b)=>a.map((n,i)=>n-b[i]);
const norm=a=>Math.hypot(...a),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export function pivot(axis,angle,point){return multiply(multiply(translation(point),rotation(axis,angle)),translation(point.map(v=>-v)));}
function align(a,b){const u=a.map(v=>v/norm(a)),v=b.map(x=>x/norm(b)),axis=cross(u,v),dot=Math.max(-1,Math.min(1,u.reduce((s,x,i)=>s+x*v[i],0)));if(norm(axis)<1e-12)return dot>0?identity():rotation(cross(u,Math.abs(u[0])<.8?[1,0,0]:[0,1,0]),Math.PI);return rotation(axis,Math.acos(dot));}
// Solver supplied by the selected source revision. All returned matrices act on
// already-baked nominal Vehicle-C coordinates. Mesh instances keep proper local
// source transforms outside this function; there are no negative scales.
export function connectedCornerTransforms(cornerPose,q,r,side,fore,wheelAngle=0){
 if(!Number.isFinite(wheelAngle))throw new TypeError('Wheel rotation must be finite');
 const pose=cornerPose(q,r,side,fore),zero=cornerPose(0,0,side,fore);
 const upright=multiply(translation(pose.uprightDeltaM),pivot([0,0,1],pose.steerRad,zero.nominalKingpinM));
 // Positive wheelAngle rotates about nominal global+Y on BOTH sides. A right
 // source wheel uses Rz(pi), so its local axle angle is correspondingly reversed.
 const spin=multiply(upright,pivot([0,1,0],wheelAngle,zero.wheelCenterM));
 const tie=multiply(multiply(translation(pose.tieInnerM),align(sub(zero.tieOuterM,zero.tieInnerM),sub(pose.tieOuterM,pose.tieInnerM))),translation(zero.tieInnerM.map(v=>-v)));
 return{pose,zero,fixed:identity(),upper:pivot([1,0,0],pose.armWorldRx,zero.upperPivotM),lower:pivot([1,0,0],pose.armWorldRx,zero.lowerPivotM),upright,steer:upright,spin,tie,rack:translation([0,r,0]),wheel:multiply(spin,origin({xyz:zero.wheelCenterM,rpy:[0,0,side<0?Math.PI:0]}))};
}
export function connectedMiddleTransforms(middlePose,q,side,wheelAngle=0){
 if(!Number.isFinite(wheelAngle))throw new TypeError('Wheel rotation must be finite');
 const pose=middlePose(q,side),zero=middlePose(0,side),upright=translation(pose.uprightDeltaM);
 const spin=multiply(upright,pivot([0,1,0],wheelAngle,zero.wheelCenterM));
 return{pose,zero,fixed:identity(),upper:pivot([1,0,0],pose.armWorldRx,zero.upperPivotM),lower:pivot([1,0,0],pose.armWorldRx,zero.lowerPivotM),upright,steer:upright,spin,wheel:multiply(spin,origin({xyz:zero.wheelCenterM,rpy:[0,0,side<0?Math.PI:0]}))};
}
