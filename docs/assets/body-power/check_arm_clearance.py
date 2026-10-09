from pathlib import Path
import json,struct,numpy as np,math
P=Path(__file__).parent;R=Path('/workspace/shared/ugv-rover-integration/app/docs/assets/robots')
def origin(o):
 x,y,z=o.get('rpy',[0,0,0]);tx,ty,tz=o.get('xyz',[0,0,0]);m=np.eye(4)
 rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]])
 ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
 rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
 m[:3,:3]=rz@ry@rx;m[:3,3]=[tx,ty,tz];return m
def rotation(a,q):
 a=np.asarray(a,float);a/=np.linalg.norm(a);x,y,z=a;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);m=np.eye(4);m[:3,:3]=np.eye(3)+math.sin(q)*K+(1-math.cos(q))*(K@K);return m
def fk(g,q):
 v={};f={g['root']:np.eye(4)};todo=list(g['joints'])
 def value(j):
  if j['name'] in v:return v[j['name']]
  if 'mimic' in j:
   mm=j['mimic'];jj=next(x for x in g['joints'] if x['name']==mm['joint']);vv=value(jj)*mm.get('multiplier',1)+mm.get('offset',0)
  else:vv=q.get(j['name'],0)
  v[j['name']]=vv;return vv
 while todo:
  for j in todo[:]:
   if j['parent'] not in f:continue
   f[j['child']]=f[j['parent']]@origin(j.get('origin',{}))@(rotation(j.get('axis',[0,0,1]),value(j)) if j['type'] in ['revolute','continuous'] else np.eye(4));todo.remove(j)
 return f

def glbverts(path):
 b=Path(path).read_bytes();n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);blen,_=struct.unpack_from('<II',b,20+n);data=b[28+n:28+n+blen];pts=[]
 def accessor(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dt={5126:np.float32,5125:np.uint32,5123:np.uint16}[a['componentType']];nc={'VEC3':3,'SCALAR':1}[a['type']];stride=v.get('byteStride',nc*np.dtype(dt).itemsize)
  return np.ndarray((a['count'],nc),dtype=dt,buffer=data,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).astype(float)
 def walk(i,m):
  node=d['nodes'][i];local=np.asarray(node.get('matrix',np.eye(4).flatten(order='F')),float).reshape((4,4),order='F')
  if 'translation'in node:local[:3,3]=node['translation']
  if 'scale'in node:local[:3,:3]=local[:3,:3]@np.diag(node['scale'])
  if 'rotation'in node:raise ValueError('Unhandled quaternion; refusing to ignore node rotation')
  m=m@local
  if 'mesh'in node:
   for p in d['meshes'][node['mesh']]['primitives']:
    vv=accessor(p['attributes']['POSITION']);pts.append(vv@m[:3,:3].T+m[:3,3])
  for c in node.get('children',[]):walk(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return np.vstack(pts)
def clearance(a,b):return float(np.linalg.norm(np.maximum(0,np.maximum(a[0]-b[1],b[0]-a[1]))))
meta=json.loads((R/'robot-kinematics.json').read_text());g=meta['ur20'];names=[j['name'] for j in g['joints'] if j['type']=='revolute'];home=[.3,-1.2,1.5,-.8,1,.2];arm_fk=fk(g,dict(zip(names,home)));body=json.loads((P/'verification.json').read_text())['parts'];bounds=[];candidates=[]
for side,y in [('left',.3),('right',-.3)]:
 root=origin({'xyz':[.9,y,.13]})
 for model,frames,base in [(g,arm_fk,root),(meta['robotiq'],fk(meta['robotiq'],{}),root@arm_fk['tool0']@origin({'rpy':[0,0,math.pi],'xyz':[0,0,.0345]}))]:
  for l in model['links']:
   if 'visual'not in l:continue
   vis=l['visual'];m=base@frames[l['name']]@origin(vis.get('origin',{}));v=glbverts(R/vis['asset'])*np.asarray(vis.get('scale',[1,1,1]));v=v@m[:3,:3].T+m[:3,3];bb=np.array([v.min(0),v.max(0)]);mind=100
   for p in body:
    pb=np.array(p['bounds_m']).reshape(2,3);d=clearance(bb,pb);mind=min(d,mind)
    if d<=1e-6:candidates.append({'arm':side,'link':l['name'],'part':p['name'],'status':'AABB overlap only; narrow phase required'})
   bounds.append({'arm':side,'link':l['name'],'actual_source_vertex_bounds_m':bb.tolist(),'minimum_AABB_separation_lower_bound_m':mind})
report={'method':'Actual source GLB vertices transformed through source FK and visual origins, compared to exact body B-rep axis-aligned bounds. AABB non-overlap proves no intersection; overlap is inconclusive.','pose_joint_rad':home,'bases_m':[[.9,.3,.13],[.9,-.3,.13]],'gripper_driver_rad':0,'qualified':False,'motion_sweep_performed':False,'body_collision_candidates':candidates,'source_link_bounds':bounds}
(P/'arm_clearance_screen.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
