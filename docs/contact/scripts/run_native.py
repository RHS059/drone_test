import pathlib,json,sys
import mujoco,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
assert mujoco.__version__=='3.15.0'
s=json.loads((R/'scenario.json').read_text())
def target(t):
 u=min(1,max(0,(t-2)/1.5));return [.1*(3*u*u-2*u*u*u),0,.1512]
def controls(t): return 0 if t>=4 else 200*min(1,max(0,(t-.2)))
all=[]
for case in s['case_parameters']:
 m=mujoco.MjModel.from_xml_path(str(R/f"assets/{case['id']}.xml")); d=mujoco.MjData(m)
 obj=m.body('coupon').id;g=m.geom('coupon_collision').id;eq=m.equality('initial_world_fixture').id
 pads={m.geom(n).id for n in ['left_pad1','left_pad2','right_pad1','right_pad2']}
 mujoco.mj_forward(m,d);rows=[]
 for i in range(5500):
  t=i*.001;d.ctrl[0]=controls(t);d.eq_active[eq]=t<1.5;d.mocap_pos[0,0]=target(t)[0]
  mujoco.mj_step(m,d)
  if (i+1)%10==0:
   forces=[];grip=[]
   for j,c in enumerate(d.contact):
    if g in (c.geom1,c.geom2):
     f=np.zeros(6);mujoco.mj_contactForce(m,d,j,f);forces.append(float(f[0]))
     if c.geom1 in pads or c.geom2 in pads:grip.append(float(f[0]))
   p=d.xpos[obj].copy();tar=target(d.time)
   rows.append(dict(t=float(d.time),position=p.tolist(),target=tar,error_m=float(np.linalg.norm(p-tar)),normal_force_N=sum(forces),grip_normal_force_N=sum(grip),contacts=len(forces),fixture_active=bool(d.eq_active[eq]),ctrl=float(d.ctrl[0]),qpos=d.qpos.tolist()))
 maxerr=max(r['error_m'] for r in rows if 1.6<=r['t']<4)
 held_at_release=next(r for r in reversed(rows) if r['t']<3.999)['position'][2]>.1
 release=held_at_release and rows[-1]['position'][2]<.05
 all.append(dict(case=case['id'],samples=rows,metrics=dict(max_transport_error_m=maxerr,strict_10mm_pass=maxerr<.01,release_fall_observed=release,dropped_before_commanded_release=not held_at_release,peak_contact_normal_force_N=max(r['normal_force_N'] for r in rows),peak_grip_normal_force_N=max(r['grip_normal_force_N'] for r in rows))))
 print(case['id'],all[-1]['metrics'])
(R/'results/native.json').write_text(json.dumps({'engine':mujoco.__version__,'runs':all}))
