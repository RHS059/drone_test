from pathlib import Path
import json,struct,numpy as np,math
import check_arm_clearance as c
P=Path(__file__).parent;R=c.R

def triangles(path):
 b=Path(path).read_bytes();n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);blen,_=struct.unpack_from('<II',b,20+n);data=b[28+n:28+n+blen];tri=[]
 def ac(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dt={5126:np.float32,5125:np.uint32,5123:np.uint16,5121:np.uint8}[a['componentType']];nc={'VEC3':3,'SCALAR':1}[a['type']];stride=v.get('byteStride',nc*np.dtype(dt).itemsize)
  return np.ndarray((a['count'],nc),dtype=dt,buffer=data,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
 def walk(i,m):
  node=d['nodes'][i];local=np.asarray(node.get('matrix',np.eye(4).flatten(order='F')),float).reshape((4,4),order='F')
  if 'translation'in node:local[:3,3]=node['translation']
  if 'scale'in node:local[:3,:3]=local[:3,:3]@np.diag(node['scale'])
  assert 'rotation'not in node,'Quaternion must not be ignored'
  m=m@local
  if 'mesh'in node:
   for p in d['meshes'][node['mesh']]['primitives']:
    assert p.get('mode',4)==4
    vv=ac(p['attributes']['POSITION']);vv=vv@m[:3,:3].T+m[:3,3]
    ix=ac(p['indices']).ravel().reshape(-1,3) if 'indices'in p else np.arange(len(vv)).reshape(-1,3)
    tri.append(vv[ix])
  for ch in node.get('children',[]):walk(ch,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return np.vstack(tri)

body={p['name']:np.array(p['bounds_m']).reshape(2,3) for p in c.body};results=[]
for hit in c.candidates:
 side=hit['arm'];base=c.origin({'xyz':[.9,.3 if side=='left' else -.3,.13]});l=next(x for x in c.g['links'] if x['name']==hit['link']);v=l['visual'];M=base@c.arm_fk[l['name']]@c.origin(v.get('origin',{}));tr=triangles(R/v['asset'])*np.array(v.get('scale',[1,1,1]));tr=tr@M[:3,:3].T+M[:3,3]
 lo=tr.min(axis=1);hi=tr.max(axis=1);bb=body[hit['part']];mask=np.all(lo<=bb[1]+1e-7,axis=1)&np.all(hi>=bb[0]-1e-7,axis=1)
 # If all source triangle bounds are disjoint from the exact part box, the surface cannot intersect it.
 # Also reject possibility of a body enclosed in arm via tested geometric lower bounds: each part lies
 # below arm triangles near its X-Y footprint, but this report limits claim to mesh surface separation.
 sep=np.linalg.norm(np.maximum(0,np.maximum(lo-bb[1],bb[0]-hi)),axis=1)
 results.append({**hit,'status':'no source-mesh triangle can intersect exact part bounding box' if not np.any(mask) else 'unresolved triangle-box candidates','candidate_triangle_count':int(mask.sum()),'minimum_triangle_AABB_separation_lower_bound_m':float(sep.min()),'triangles_checked':len(tr)})
report={'method':'Conservative per-triangle AABB broad phase, after source FK; all arm triangle boxes checked against exact B-rep part bounds. Positive separation proves surface nonintersection; no smooth-surface/motion or manufacturing tolerance claim.','pose_joint_rad':c.home,'pair_results':results,'unresolved_pairs':[x for x in results if x['candidate_triangle_count']],'qualified':False,'source_mesh_only':True,'motion_sweep_performed':False}
(P/'arm_triangle_clearance_screen.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
