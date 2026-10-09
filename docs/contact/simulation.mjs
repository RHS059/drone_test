import loadMujoco from './vendor/mujoco.js';
export const targetAt=t=>{const u=Math.min(1,Math.max(0,(t-2)/1.5));return [.1*(3*u*u-2*u*u*u),0,.1512]};
export const controlAt=t=>t>=4?0:200*Math.min(1,Math.max(0,t-.2));
export async function createEngine(readBytes){
 const mj=await loadMujoco();
 if(mj.mj_versionString()!=='3.15.0')throw Error('MuJoCo version mismatch');
 const read=readBytes|| (async p=>{const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error(`Missing asset ${p}`);return new Uint8Array(await r.arrayBuffer())});
 const files=['assets/nominal.xml','assets/low-friction.xml','assets/heavy.xml',...['base_mount','base','driver','coupler','follower','pad','silicone_pad','spring_link'].map(n=>`assets/robotiq_2f85/assets/${n}.stl`)];
 for(const p of files){const dir='/'+p.substring(0,p.lastIndexOf('/'));mj.FS.mkdirTree(dir);mj.FS.writeFile('/'+p,await read(p));}
 return {mj,createCase(name='nominal'){
  if(!['nominal','low-friction','heavy'].includes(name))throw Error('Unknown case');
  const model=mj.MjModel.from_xml_path(`/assets/${name}.xml`),data=new mj.MjData(model);
  const obj=model.body('coupon').id, geom=model.geom('coupon_collision').id,fixture=model.eq('initial_world_fixture').id;
  const pads=new Set(['left_pad1','left_pad2','right_pad1','right_pad2'].map(n=>model.geom(n).id));
  let step=0;mj.mj_forward(model,data);
  return {model,data,mj,name,get stepCount(){return step},step(){const t=step*.001;data.ctrl[0]=controlAt(t);data.eq_active[fixture]=t<1.5?1:0;data.mocap_pos[0]=targetAt(t)[0];mj.mj_step(model,data);step++},sample(){
   let normal=0,grip=0,contacts=0;const buffer=new mj.DoubleBuffer(6);
   for(let j=0;j<data.ncon;j++){const c=data.contact.get(j);if(c.geom1===geom||c.geom2===geom){mj.mj_contactForce(model,data,j,buffer);const f=buffer.GetView();normal+=f[0];contacts++;if(pads.has(c.geom1)||pads.has(c.geom2))grip+=f[0];}c.delete();}
   buffer.delete();
   const position=Array.from(data.xpos.slice(obj*3,obj*3+3)),target=targetAt(data.time);
   return {t:data.time,position,target,error_m:Math.hypot(...position.map((x,i)=>x-target[i])),normal_force_N:normal,grip_normal_force_N:grip,contacts,fixture_active:!!data.eq_active[fixture],ctrl:data.ctrl[0],qpos:Array.from(data.qpos)};
  },dispose(){data.delete();model.delete();}};
 }};
}
export function summarize(samples){const max=Math.max(...samples.filter(r=>r.t>=1.6&&r.t<4).map(r=>r.error_m));return {max_transport_error_m:max,strict_10mm_pass:max<.01,release_fall_observed:samples.findLast(r=>r.t<3.999).position[2]>.1&&samples.at(-1).position[2]<.05,dropped_before_commanded_release:samples.findLast(r=>r.t<3.999).position[2]<=.1,peak_contact_normal_force_N:Math.max(...samples.map(r=>r.normal_force_N)),peak_grip_normal_force_N:Math.max(...samples.map(r=>r.grip_normal_force_N))};}
export function validateParameters({mass_kg,friction}){if(!Number.isFinite(mass_kg)||mass_kg<=0)throw new RangeError('mass_kg must be finite and positive');if(!Number.isFinite(friction)||friction<0)throw new RangeError('friction must be finite and nonnegative');return true;}
