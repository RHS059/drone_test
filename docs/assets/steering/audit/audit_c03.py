#!/usr/bin/env python3
"""Independent contract-coordinate root finding and GLB alignment audit.

No analytic steering-root formula is reproduced. The reference solver constructs
both suspension-arm endpoints with rigid Rx matrices, solves the Euclidean tie
closure residual with bracketed Brent roots over a complete turn, and selects the
neutral-nearest assembly branch. Reads frozen original C03 sources only.
"""
from pathlib import Path
import argparse, json, math, hashlib, struct, subprocess, datetime
import numpy as np
from scipy.optimize import brentq

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,default=Path('mechanical/running_gear_C03'),
    help='Directory containing the extracted C03 contract, solver, manifest, GLB and README (default: ./mechanical/running_gear_C03).')
parser.add_argument('--output-dir',type=Path,default=Path('steering-audit-output'),
    help='Directory for newly generated fixtures and evidence (default: ./steering-audit-output).')
args=parser.parse_args()
ROOT=args.source_root.expanduser().resolve()
OUT=args.output_dir.expanduser().resolve()
for required in ['interface_contract_C03_R01.json','kinematics_C03_R01.js','original_steering_C03_R01_manifest.json','original_steering_C03_R01.glb','README_C03_R01.md']:
    if not (ROOT/required).is_file():
        parser.error(f'Missing source file: {ROOT/required}. Extract the public source and GLB packages into the same directory, or set --source-root.')
OUT.mkdir(parents=True,exist_ok=True)
contract=json.loads((ROOT/'interface_contract_C03_R01.json').read_text())
manifest=json.loads((ROOT/'original_steering_C03_R01_manifest.json').read_text())
CORNERS={x['id']:x for x in contract['corners']}
SEED=20261009
rng=np.random.default_rng(SEED)


def rx(t):
    c,s=math.cos(t),math.sin(t)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def rz(t):
    c,s=math.cos(t),math.sin(t)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def array(x):return np.array(x,dtype=float)
def as_json(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)
def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=as_json)+'\n')
def norm(x):return float(np.linalg.norm(x))

angles=np.linspace(-math.pi,math.pi,513)
cosines=np.cos(angles);sines=np.sin(angles)

def independent_pose(c,q,r):
    side,fore=c['side'],c['fore']
    K0=array(c['nominal_kingpin_m']);Pup=array(c['nominal_upper_pivot_m']);Plo=array(c['nominal_lower_pivot_m'])
    # The kingpin origin is midway between the vertically separated arm joints.
    half=(Pup-Plo)/2
    U0=K0+half;L0=K0-half
    armR=rx(side*q)
    U=Pup+armR@(U0-Pup);L=Plo+armR@(L0-Plo)
    K=(U+L)/2;delta=K-K0
    I0=array(c['nominal_tie_inner_m']);O0=array(c['nominal_tie_outer_m']);I=I0+array([0,r,0])
    A=O0-K0;T=O0-I0;tie_length=norm(T)
    def residual(theta):return norm(K+rz(theta)@A-I)**2-tie_length**2
    rotated=np.column_stack([cosines*A[0]-sines*A[1],sines*A[0]+cosines*A[1],np.full(len(angles),A[2])])
    differences=K+rotated-I
    residuals=np.sum(differences*differences,axis=1)-tie_length**2
    roots=[]
    for j in range(len(angles)-1):
        if abs(residuals[j])<1e-16:roots.append(float(angles[j]))
        if residuals[j]*residuals[j+1]<0:
            roots.append(float(brentq(residual,float(angles[j]),float(angles[j+1]),xtol=5e-15,rtol=1e-14)))
    roots=sorted(set(round(x,14) for x in roots))
    if not roots:raise RuntimeError(f'No closure root: {c["id"]} {q} {r}')
    theta=min(roots,key=abs)
    if abs(theta)<1e-13:theta=0.
    R=rz(theta);O=K+R@A;W=K+R@(array(c['nominal_wheel_center_m'])-K0)
    pin=array(c['inner_pin_axis']);wheel0=array([0,side,0])
    # Source lower-arm shock eye is at 65% of the outer-joint link vector.
    shock=Plo+.65*(L-Plo)
    pose={'q':q,'rackM':r,'side':side,'fore':fore,'steerRad':theta,'armWorldRx':side*q,
      'nominalKingpinM':K0,'kingpinM':K,'uprightDeltaM':delta,'tieInnerM':I,'tieOuterM':O,'tieLengthM':tie_length,
      'wheelCenterM':W,'upperPivotM':Pup,'lowerPivotM':Plo,
      'shockFixedM':[fore*1.35,side*.56,.17],'shockMovingM':shock,
      'innerTiePinAxis':pin,'outerTiePinAxis':R@pin,'wheelAxis':R@wheel0,'kingpinAxis':[0,0,1],
      'actuatorFixedM':[fore*1.084,-.34,-.25],'actuatorMovingM':[fore*1.084,.15+r,-.25],
      'actuatorPinDistanceM':.49+r,'actuatorExtensionM':.1+r}
    return pose,{'all_closure_roots_rad':roots,'closure_residual_m':norm(O-I)-tie_length,
        'upper_joint_m':U,'lower_joint_m':L,'kingpin_vertical_error_m':norm((U-L)-(U0-L0))}

def case(c,q,r,kind):return {'corner_id':c['id'],'q_rad':float(q),'rack_m':float(r),'side':c['side'],'fore':c['fore'],'kind':kind}
inputs=[]
for c in CORNERS.values():
    for qd in [-12,0,12]:
        for rm in [-75,0,75]:inputs.append(case(c,math.radians(qd),rm/1000,'boundary_grid'))
for q,r in rng.uniform([-math.radians(12),-.075],[math.radians(12),.075],size=(1024,2)):
    for c in CORNERS.values():inputs.append(case(c,q,r,'random_bounded'))
for q in np.linspace(-math.radians(12),math.radians(12),241):
    for c in CORNERS.values():inputs.append(case(c,q,0,'zero_rack_sweep'))
# Mirror-aware L/R verification requires opposite global-Y rack translation.
for q,r in rng.uniform([-math.radians(12),-.075],[math.radians(12),.075],size=(128,2)):
    for c in CORNERS.values():inputs.append(case(c,q,r if c['side']==1 else -r,'mirror_pairs'))
save('inputs.json',inputs)
js_runner=r'''import fs from 'node:fs';
const source=fs.readFileSync(process.argv[2],'utf8');
const {cornerPose,limits}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const inputs=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const poses=inputs.map(p=>cornerPose(p.q_rad,p.rack_m,p.side,p.fore));
const tests=[];
function check(name,args,expected){let actual='accepted',result;try{result=cornerPose(...args)}catch(e){actual=e.constructor.name};tests.push({name,expected,actual,pass:expected===actual});}
for(const [label,value] of [['NaN',NaN],['+Infinity',Infinity],['-Infinity',-Infinity],['null',null],['undefined',undefined],['string','0'],['array',[]],['object',{}],['boolean',false]]){
 check('q '+label,[value,0,1,1],'TypeError');check('rack '+label,[0,value,1,1],'TypeError');
}
for(const sign of [-1,1]){
 check('q at limit '+sign,[sign*limits.suspensionRad,0,1,1],'accepted');
 check('rack at limit '+sign,[0,sign*limits.rackM,1,1],'accepted');
 check('q outside '+sign,[sign*(limits.suspensionRad+1e-8),0,1,1],'RangeError');
 check('rack outside '+sign,[0,sign*(limits.rackM+1e-8),1,1],'RangeError');
 check('q roundoff allowance '+sign,[sign*(limits.suspensionRad+0.5e-10),0,1,1],'accepted');
 check('rack roundoff allowance '+sign,[0,sign*(limits.rackM+0.5e-10),1,1],'accepted');
}
for(const bad of [0,2,-2,NaN,Infinity,null,'1']){
 check('invalid side '+String(bad),[0,0,bad,1],'RangeError');check('invalid fore '+String(bad),[0,0,1,bad],'RangeError');
}
check('defaults',[0,0],'accepted');
console.log(JSON.stringify({limits,poses,input_validation:tests}));
'''
(OUT/'run_source.mjs').write_text(js_runner)
source_result=json.loads(subprocess.check_output(['node',str(OUT/'run_source.mjs'),str(ROOT/'kinematics_C03_R01.js'),str(OUT/'inputs.json')],text=True))
fixtures=[];errors={};max_closure=0.;max_root_error=0.;max_zero=0.;max_arm_error=0.;max_axis_norm_error=0.;max_wheel_offset_error=0.;max_transform_error=0.;steer_extreme={'rad':0.};min_branch_separation=math.inf

for inp,js in zip(inputs,source_result['poses']):
    ref,diag=independent_pose(CORNERS[inp['corner_id']],inp['q_rad'],inp['rack_m'])
    for key in ref:
        err=float(np.max(np.abs(array(ref[key])-array(js[key]))))
        errors[key]=max(errors.get(key,0.),err)
    max_root_error=max(max_root_error,abs(js['steerRad']-ref['steerRad']))
    max_closure=max(max_closure,abs(norm(array(js['tieOuterM'])-array(js['tieInnerM']))-ref['tieLengthM']),abs(diag['closure_residual_m']))
    max_arm_error=max(max_arm_error,diag['kingpin_vertical_error_m'])
    if inp['rack_m']==0:max_zero=max(max_zero,abs(js['steerRad']))
    if abs(ref['steerRad'])>steer_extreme['rad']:steer_extreme={'rad':abs(ref['steerRad']),'degrees':abs(math.degrees(ref['steerRad'])),'input':inp}
    for field in ['innerTiePinAxis','outerTiePinAxis','wheelAxis','kingpinAxis']:
        max_axis_norm_error=max(max_axis_norm_error,abs(norm(js[field])-1))
    max_wheel_offset_error=max(max_wheel_offset_error,norm(array(js['wheelCenterM'])-array(js['kingpinM'])-.128*array(js['wheelAxis'])))
    max_transform_error=max(max_transform_error,norm(array(js['tieOuterM'])-(array(js['uprightDeltaM'])+array(js['nominalKingpinM'])+rz(js['steerRad'])@(array(CORNERS[inp['corner_id']]['nominal_tie_outer_m'])-array(js['nominalKingpinM'])))))
    roots=diag['all_closure_roots_rad']
    other=[abs(x) for x in roots if abs(x-ref['steerRad'])>1e-10]
    if other:min_branch_separation=min(min_branch_separation,min(other)-abs(ref['steerRad']))
    if inp['kind'] in ['boundary_grid','random_bounded']:
        fixtures.append({'input':inp,'expected':ref,'independent_closure':diag})

# Numerical reflection assertions are taken from source outputs, not reference equations.
mirror_errors={'fore_aft_positions_m':0.,'fore_aft_axes':0.,'fore_aft_steer_rad':0.,'left_right_positions_m':0.,'left_right_axes':0.,'left_right_steer_rad':0.}
position_fields=['nominalKingpinM','kingpinM','uprightDeltaM','tieInnerM','tieOuterM','wheelCenterM','upperPivotM','lowerPivotM','shockFixedM','shockMovingM','actuatorFixedM','actuatorMovingM']
axis_fields=['innerTiePinAxis','outerTiePinAxis','wheelAxis','kingpinAxis']
for n in range(36,len(inputs),4):
    group=inputs[n:n+4]
    if len(group)!=4:continue
    poses=source_result['poses'][n:n+4]
    if len(set(x['kind'] for x in group))!=1:continue
    # Order front_left, front_right, rear_left, rear_right.
    for a,b in [(0,2),(1,3)]:
        if group[a]['q_rad']!=group[b]['q_rad'] or group[a]['rack_m']!=group[b]['rack_m']:continue
        for f in position_fields:mirror_errors['fore_aft_positions_m']=max(mirror_errors['fore_aft_positions_m'],norm(array(poses[a][f])*[-1,1,1]-poses[b][f]))
        for f in axis_fields:mirror_errors['fore_aft_axes']=max(mirror_errors['fore_aft_axes'],norm(array(poses[a][f])*[-1,1,1]-poses[b][f]))
        mirror_errors['fore_aft_steer_rad']=max(mirror_errors['fore_aft_steer_rad'],abs(poses[a]['steerRad']+poses[b]['steerRad']))
    if group[0]['kind'] in ['mirror_pairs','zero_rack_sweep']:
        for a,b in [(0,1),(2,3)]:
            for f in position_fields:
                # Actuator layout is intentionally asymmetric in Y, shared by both corners.
                if f.startswith('actuator'):continue
                mirror_errors['left_right_positions_m']=max(mirror_errors['left_right_positions_m'],norm(array(poses[a][f])*[1,-1,1]-poses[b][f]))
            for f in axis_fields:mirror_errors['left_right_axes']=max(mirror_errors['left_right_axes'],norm(array(poses[a][f])*[1,-1,1]-poses[b][f]))
            mirror_errors['left_right_steer_rad']=max(mirror_errors['left_right_steer_rad'],abs(poses[a]['steerRad']+poses[b]['steerRad']))

source_names=['interface_contract_C03_R01.json','kinematics_C03_R01.js','original_steering_C03_R01_manifest.json','original_steering_C03_R01.glb','README_C03_R01.md']
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in source_names}
summary={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Original C03 geometric/FK only; no physical, load, motor, actuator, service or safety qualification. Private OEM source excluded.',
 'method':'Contract world coordinates; independent Rx suspension reconstruction, Euclidean tie residual scanned through a complete turn, bracketed Brent roots, neutral-nearest branch. No analytic source formula duplicated.',
 'source_sha256':hashes,'sample_counts':{kind:sum(x['kind']==kind for x in inputs) for kind in ['boundary_grid','random_bounded','zero_rack_sweep','mirror_pairs']},
 'random_seed':SEED,'fixture_count':len(fixtures),'maximum_errors_by_pose_field':errors,'maximum_root_disagreement_rad':max_root_error,'maximum_tie_closure_error_m':max_closure,'maximum_zero_rack_bump_steer_rad':max_zero,
 'maximum_parallel_arm_joint_separation_error_m':max_arm_error,'maximum_axis_norm_error':max_axis_norm_error,'maximum_wheel_center_axis_consistency_error_m':max_wheel_offset_error,'maximum_baked_upright_transform_error_m':max_transform_error,
 'mirror_errors':mirror_errors,'maximum_sampled_steer':steer_extreme,'minimum_selected_vs_other_root_abs_angle_margin_rad':min_branch_separation,'input_validation':source_result['input_validation'],
 'pass':max(errors.values())<1e-10 and max_closure<1e-10 and max_zero<1e-10 and max(mirror_errors.values())<1e-10 and all(x['pass'] for x in source_result['input_validation'])}
save('independent_fixtures_C03_R01.json',{'schema_version':1,'source_sha256':hashes,'method':summary['method'],'units':{'length':'m','angle':'rad'},'random_seed':SEED,'fixtures':fixtures})
save('audit_summary.json',summary)
for fixture_kind,filename in [('boundary_grid','boundary_fixtures_C03_R01.json'),('random_bounded','random_fixtures_C03_R01.json')]:
    save(filename,{'schema_version':1,'source_sha256':hashes,'method':summary['method'],'units':{'length':'m','angle':'rad'},'random_seed':SEED,'fixtures':[f for f in fixtures if f['input']['kind']==fixture_kind]})
print(json.dumps(summary,indent=2))
if not summary['pass']:raise SystemExit(1)
