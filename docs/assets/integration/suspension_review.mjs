// Suspension behaviour review for C04 (Claude). Uses the same kinematics module the viewer runs. Run: node docs/assets/integration/suspension_review.mjs
import {cornerPose, middlePose, limits} from '../../connected/kinematics_C04_R03.mjs';
const deg=Math.PI/180, len=v=>Math.hypot(...v), sub=(a,b)=>a.map((x,i)=>x-b[i]);
// 1. Wheel path through travel (front-left corner, straight ahead)
console.log('q(deg)  wheel dz(mm)  track dy(mm)  shock len(mm)');
const rows=[];for(const qd of [-12,-8,-4,0,4,8,12]){const p=cornerPose(qd*deg,0,1,1),p0=cornerPose(0,0,1,1);
 const dz=(p.wheelCenterM[2]-p0.wheelCenterM[2])*1e3, dy=(p.wheelCenterM[1]-p0.wheelCenterM[1])*1e3, L=len(sub(p.shockMovingM,p.shockFixedM))*1e3;rows.push([qd,dz,dy,L]);
 console.log(`${qd.toString().padStart(4)}   ${dz.toFixed(1).padStart(7)}      ${dy.toFixed(1).padStart(7)}      ${L.toFixed(1)}`);}
const MR=(rows[4][3]-rows[2][3])/(rows[4][1]-rows[2][1]); console.log('motion ratio (spring/wheel) about ride:',Math.abs(MR).toFixed(3));
console.log('scrub: lateral wheel shift per mm vertical near ride:',Math.abs((rows[4][2]-rows[2][2])/(rows[4][1]-rows[2][1])).toFixed(2));
const p0=cornerPose(0,0,1,1); console.log('kingpin->wheel centre lateral offset (scrub-radius proxy, mm):',((p0.wheelCenterM[1]-p0.kingpinM[1])*1e3).toFixed(0),' kingpin axis',p0.kingpinAxis);
// 2. Steered tyre vs shock/spring envelope clearance: tyre as cylinder r=.4155 half-width .145 about wheelAxis at wheelCenter
const R=.4155,HW=.145,SPR=.055;
function segDist(P,A,B){const AB=sub(B,A),t=Math.max(0,Math.min(1,sub(P,A).reduce((s,v,i)=>s+v*AB[i],0)/AB.reduce((s,v)=>s+v*v,0)));return len(sub(P,A.map((a,i)=>a+t*AB[i])));}
let worst=[9,null];
for(let qd=-12;qd<=12;qd+=3)for(let r=-limits.rackM;r<=limits.rackM+1e-9;r+=limits.rackM/6){const p=cornerPose(qd*deg,r,1,1);const c=p.wheelCenterM,ax=p.wheelAxis;
 const u=[0,0,1];const w=[ax[1]*u[2]-ax[2]*u[1],ax[2]*u[0]-ax[0]*u[2],ax[0]*u[1]-ax[1]*u[0]];const wn=len(w);const e1=w.map(x=>x/wn),e2=[0,0,1];
 for(let s=-1;s<=1;s+=.5)for(let a=0;a<360;a+=5){const th=a*deg;const P=c.map((ci,i)=>ci+ax[i]*HW*s+R*(Math.cos(th)*e1[i]+Math.sin(th)*e2[i]));
  const d=segDist(P,p.shockFixedM,p.shockMovingM)-SPR; if(d<worst[0])worst=[d,{q:qd,steerDeg:(p.steerRad/deg).toFixed(1),rack:r.toFixed(3)}];}}
console.log('min tyre-to-spring envelope clearance over travel x steer (mm):',(worst[0]*1e3).toFixed(0),JSON.stringify(worst[1]));
let maxSteer=0;for(let r=-limits.rackM;r<=limits.rackM+1e-9;r+=.0125)maxSteer=Math.max(maxSteer,Math.abs(cornerPose(0,r,1,1).steerRad/deg));console.log('max steer angle (deg):',maxSteer.toFixed(1));
// 3. Spring balance (Eibach 1800.300.0200S: 200 lb/in = 35.0 N/mm, free 457.2 mm, block 161 mm)
const k=35.03, free=457.2;
console.log('spring rate at wheel (N/mm):',(k*MR*MR).toFixed(1));
for(const M of [1300,1600,2000,2920,3935]){const unspr=6*90, m=(M-unspr)/6, F=m*9.81/Math.abs(MR);const comp=F/k; console.log(`vehicle ${M} kg: spring force ${(F/1000).toFixed(2)} kN, spring compressed ${comp.toFixed(0)} mm -> length ${(free-comp).toFixed(0)} mm (screened seat range 300-370, block 161)`);}
// 4. Lever: spring load point vs lower-arm pivot bushings
console.log('lower eye X',p0.shockMovingM[0].toFixed(3),'| lower-arm pivot station X',(1.35).toFixed(3),'| bushing pair at X 1.18/1.52 (±170 mm)');
