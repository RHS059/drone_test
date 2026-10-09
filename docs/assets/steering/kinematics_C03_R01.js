/* Original C03 candidate kinematics, metres/radians. No dynamics or safety approval. */
export const limits = Object.freeze({ suspensionRad: 12*Math.PI/180, rackM: 0.075 });
const v=[0,.262,-.15], a=[-.289,-.090,-.085], king=[0,.812,-.25], T=[.072,.262,-.15];
const norm2=x=>x.reduce((s,n)=>s+n*n,0);
const add=(x,y)=>x.map((n,i)=>n+y[i]);
const sub=(x,y)=>x.map((n,i)=>n-y[i]);
const rz=(x,d)=>[x[0]*Math.cos(d)-x[1]*Math.sin(d),x[0]*Math.sin(d)+x[1]*Math.cos(d),x[2]];
export function cornerPose(q,r,side=1,fore=1) {
 if(!Number.isFinite(q)||!Number.isFinite(r))throw new TypeError('q and r must be finite numbers');
 if(Math.abs(q)>limits.suspensionRad+1e-10 || Math.abs(r)>limits.rackM+1e-10)throw new RangeError('Outside candidate checked domain');
 if(![-1,1].includes(side)||![-1,1].includes(fore))throw new RangeError('side/fore must be +/-1');
 const reflect=x=>[x[0],side*x[1],x[2]];
 const dv=[0,.262*Math.cos(q)+.15*Math.sin(q)-.262,.262*Math.sin(q)-.15*Math.cos(q)+.15];
 const K=reflect(add(king,dv)), A=reflect(a), I=add(reflect(sub(add(king,a),T)),[0,r,0]), S=sub(K,I);
 const C=S[0]*A[0]+S[1]*A[1],D=-S[0]*A[1]+S[1]*A[0];
 const E=(norm2(T)-norm2(S)-norm2(A))/2-S[2]*A[2],rat=E/Math.hypot(C,D);
 if(Math.abs(rat)>1+1e-10)throw new Error('No linkage closure');
 const p=Math.atan2(D,C), al=Math.acos(Math.max(-1,Math.min(1,rat)));
 const wrap=x=>Math.atan2(Math.sin(x),Math.cos(x));
 const roots=[wrap(p+al),wrap(p-al)];const d=Math.abs(roots[0])<Math.abs(roots[1])?roots[0]:roots[1];
 const world=x=>[fore*(1.35+x[0]),x[1],x[2]];
 const O=add(K,rz(A,d)), wheel=add(K,rz([0,side*.128,0],d));
 const low=[0,side*.55,-.27], shockMove=add(low,[0,side*.65*(v[1]*Math.cos(q)-v[2]*Math.sin(q)),.65*(v[1]*Math.sin(q)+v[2]*Math.cos(q))]);
 return {q, rackM:r, side,fore, steerRad:fore*d, armWorldRx:side*q,
   nominalKingpinM:[fore*1.35,side*.812,-.25],kingpinM:world(K), uprightDeltaM:reflect(dv),
   tieInnerM:world(I),tieOuterM:world(O),tieLengthM:Math.sqrt(norm2(T)),wheelCenterM:world(wheel),
   upperPivotM:[fore*1.35,side*.55,.07],lowerPivotM:[fore*1.35,side*.55,-.27],
   shockFixedM:[fore*1.35,side*.56,.17],shockMovingM:world(shockMove),
   innerTiePinAxis:[0,side*.4968521996651735,.8678351754151697],
   outerTiePinAxis:rz([0,side*.4968521996651735,.8678351754151697],fore*d),
   wheelAxis:rz([0,side,0],fore*d),kingpinAxis:[0,0,1],
   actuatorFixedM:[fore*1.084,-.34,-.25],actuatorMovingM:[fore*1.084,.15+r,-.25],
   actuatorPinDistanceM:.49+r,actuatorExtensionM:.1+r};
}
