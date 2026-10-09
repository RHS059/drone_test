#!/usr/bin/env python3
"""Independent validation using pycollada, NumPy and SciPy (no Blender).
Reads GLB via separate decoder; compares complete vertex streams, normals, UVs,
material diffuse values and embedded texture digests with the upstream source.
FK tested against independent standard-DH arm equations and analytic 2F85 chain.
"""
import sys,pathlib,json,struct,hashlib,math,xml.etree.ElementTree as ET
root=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.deps'))
import numpy as np,collada
from scipy.spatial.transform import Rotation as Rotation
P=root/'dist';meta=json.loads((P/'robot-kinematics.json').read_text());plan=json.loads((root/'conversion-plan.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def glb(path):
 b=path.read_bytes();magic,version,length=struct.unpack_from('<4sII',b);assert (magic,version,length)==(b'glTF',2,len(b));n,typ=struct.unpack_from('<II',b,12);assert typ==0x4e4f534a;g=json.loads(b[20:20+n]);ln,tp=struct.unpack_from('<II',b,20+n);assert tp==0x004e4942;data=b[28+n:];assert len(data)==ln
 def acc(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];assert a['componentType']==5126 and not v.get('byteStride');d={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.frombuffer(data,dtype='<f4',count=a['count']*d,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,d)
 prim=[]
 def walk(i,T):
  n=g['nodes'][i];mat=np.array(n.get('matrix',np.eye(4).T.ravel())).reshape(4,4).T;T=T@mat
  if 'mesh' in n:
   for p in g['meshes'][n['mesh']]['primitives']:
    a={k:acc(v) for k,v in p['attributes'].items()};a['POSITION']=a['POSITION']@T[:3,:3].T+T[:3,3]
    if 'NORMAL' in a:a['NORMAL']=a['NORMAL']@np.linalg.inv(T[:3,:3])
    a['material']=g['materials'][p['material']];prim.append(a)
  for j in n.get('children',[]):walk(j,T)
 for i in g['scenes'][g.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return g,data,prim
report=[]
for item in plan:
 source=root/item['source'];assert sha(source.read_bytes())==item['sha256']
 g,data,actual=glb(P/item['output']);m=collada.Collada(str(source));expected=[]
 for geom in m.scene.objects('geometry'):
  for prim in geom.primitives():
   if hasattr(prim,'triangleset'):prim=prim.triangleset()
   expected.append(prim)
 assert len(actual)==len(expected),(item['link'],len(actual),len(expected))
 vmax=nmax=uvmax=0
 for a,e in zip(actual,expected):
  verts=e.vertex[e.vertex_index].reshape(-1,3);assert verts.shape==a['POSITION'].shape
  err=float(np.max(abs(verts-a['POSITION'])));vmax=max(vmax,err);assert err<2e-7,(item['link'],err)
  norms=e.normal[e.normal_index].reshape(-1,3); norm=a['NORMAL']; norms/=np.linalg.norm(norms,axis=1)[:,None];norm/=np.linalg.norm(norm,axis=1)[:,None];err=float(np.max(abs(norms-norm)));nmax=max(nmax,err);assert err<2e-6,(item['link'],'normal',err)
  if e.texcoordset:
   uv=e.texcoordset[0][e.texcoord_indexset[0]].reshape(-1,2).copy();uv[:,1]=1-uv[:,1];err=float(np.max(abs(uv-a['TEXCOORD_0'])));uvmax=max(uvmax,err);assert err<1e-6
  diffuse=e.material.effect.diffuse;pbr=a['material']['pbrMetallicRoughness']
  if isinstance(diffuse,collada.material.Map):
   tex=g['textures'][pbr['baseColorTexture']['index']];im=g['images'][tex['source']];v=g['bufferViews'][im['bufferView']];raw=data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];assert sha(raw)==sha((source.parent/diffuse.sampler.surface.image.path).read_bytes())
  else:assert np.allclose(pbr['baseColorFactor'],diffuse,atol=1e-8)
 report.append({'asset':item['output'],'triangles':sum(len(e) for e in expected),'source_vertex_max_error_m':vmax,'source_normal_max_error':nmax,'uv_max_error':uvmax,'material_diffuse_verified':True,'texture_bytes_sha256_verified':True if g.get('images') else None,'sha256':sha((P/item['output']).read_bytes())})
for f in json.loads((P/'source-manifest.json').read_text())['files']:assert sha((P/f['path']).read_bytes())==f['sha256']
assert len(meta['ur20']['links'])==12 and len(meta['ur20']['joints'])==11
assert len(meta['robotiq']['links'])==9 and len(meta['robotiq']['joints'])==8
assert sum(j['type']=='revolute' for j in meta['robotiq']['joints'])==6
assert sum('mimic' in j for j in meta['robotiq']['joints'])==5
assert abs(meta['ur20']['source_mass_total_kg']-64.96)<1e-8

def origin(o):
 T=np.eye(4);T[:3,3]=o['xyz'];T[:3,:3]=Rotation.from_euler('xyz',o['rpy']).as_matrix();return T
def axis(a,q):
 T=np.eye(4);T[:3,:3]=Rotation.from_rotvec(np.array(a)*q).as_matrix();return T
def fk(model,q):
 frames={model['root']:np.eye(4)};todo=list(model['joints']);values=dict(q)
 for j in todo:
  if j.get('mimic'):mi=j['mimic'];values[j['name']]=values.get(mi['joint'],0)*mi['multiplier']+mi['offset']
 while todo:
  n=len(todo)
  for j in todo[:]:
   if j['parent'] not in frames:continue
   T=origin(j['origin'])
   if j['type']=='revolute':T=T@axis(j['axis'],values.get(j['name'],0))
   frames[j['child']]=frames[j['parent']]@T;todo.remove(j)
  assert len(todo)<n
 return frames,values
# Independent standard-DH serial chain. These dimensions are the UR20 source
# defaults, intentionally not robot-specific calibration or catalogue rounding.
def dh(theta,a,d,alpha):
 c,s,ca,sa=np.cos(theta),np.sin(theta),np.cos(alpha),np.sin(alpha)
 return np.array([[c,-s*ca,s*sa,a*c],[s,c*ca,-c*sa,a*s],[0,sa,ca,d],[0,0,0,1]])
def dh_tool(q):
 T=axis([0,0,1],math.pi)
 for vals in zip(q,[0,-.862,-.7287,0,0,0],[.2363,0,0,.201,.1593,.1543],[math.pi/2,0,0,math.pi/2,-math.pi/2,0]):T=T@dh(*vals)
 return T
names=[j['name'] for j in meta['ur20']['joints'] if j['type']=='revolute'];fixtures=[]
for label,angles in [('zero',[0]*6),('ready',[0,-math.pi/2,math.pi/2,-math.pi/2,-math.pi/2,0]),('folded',[0,-1.4,2.1,-2.2,-1.57,0.5]),('random',[0.34,-.83,1.15,-.61,.92,-.26])]:
 q=dict(zip(names,angles));frames,_=fk(meta['ur20'],q);err=float(np.max(abs(frames['tool0']-dh_tool(angles))));assert err<1e-8,(label,'DH mismatch',err)
 assert np.max(abs(frames['wrist_3_link']-frames['tool0']))<1e-12
 fixtures.append({'name':label,'joint_values':q,'link_matrices_row_major':{k:v.ravel().tolist() for k,v in frames.items()},'independent_dh_max_error':err})
gfixtures=[]
for q in [0,.4,.8]:
 frames,values=fk(meta['robotiq'],{'robotiq_85_left_knuckle_joint':q})
 # Independent signed two-pivot formula for parallel fingertip orientation.
 for sign,side in [(1,'left'),(-1,'right')]:
  R=Rotation.from_rotvec([0,-sign*q,0]).as_matrix(); pos=np.array([sign*.03060114,0,.05490452])+R@np.array([sign*(.03152616+.00563134),0,-.00376347+.04718515]);f=frames[f'robotiq_85_{side}_finger_tip_link'];assert np.max(abs(f[:3,3]-pos))<1e-12;assert np.max(abs(f[:3,:3]-np.eye(3)))<1e-12
 for j in meta['robotiq']['joints']:
  if j['type']=='revolute':assert j['limit']['lower']-1e-10<=values[j['name']]<=j['limit']['upper']+1e-10
 gfixtures.append({'driver_radians':q,'joint_values':values,'link_matrices_row_major':{k:v.ravel().tolist() for k,v in frames.items()}})
(P/'fk-fixtures.json').write_text(json.dumps({'matrix_format':'row-major 4x4; Three Matrix4.fromArray expects transpose/column-major conversion','ur20':fixtures,'robotiq':gfixtures,'mount_chain':meta['mount_chain']},indent=2)+'\n')
output={'status':'passed','geometry_checks':report,'fk':{'arm_poses':len(fixtures),'arm_standard_dh_independently_matched':True,'wrist3_to_tool0_identity_verified':True,'gripper_poses':len(gfixtures),'six_moving_joints_five_mimics_verified':True,'parallel_fingertip_analytic_verified':True},'source_hashes_verified':True,'manufacturing_fit':'not certified; project adapter seating and skirt clearance need separate mechanical audit','libraries':{'pycollada':collada.__version__,'numpy':np.__version__}}
(P/'validation-report.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'status':'passed','geometry_assets':len(report),'arm_poses':len(fixtures),'gripper_poses':len(gfixtures),'max_source_vertex_error_m':max(r['source_vertex_max_error_m'] for r in report)}))
