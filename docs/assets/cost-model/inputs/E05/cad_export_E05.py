"""Original source-dimension maximum housing/interface models, not supplier CAD.
Separate local datum files for revised vehicle packaging; no WD220 geometry.
"""
from pathlib import Path
import cadquery as cq,numpy as np,json,struct,hashlib
P=Path(__file__).resolve().parent
COLORS={'housing':[.21,.23,.25,1],'copper':[.71,.39,.17,1],'steel':[.69,.71,.74,1],'cover':[.31,.34,.37,.8],'label':[.62,.61,.55,1]}
def box(x,y,z,c):return cq.Workplane('XY').box(x,y,z).translate(c).val()
def bore(s,x,y,r,z,length):return s.cut(cq.Workplane('XY').center(x,y).circle(r).extrude(length).translate((0,0,z)).val())
def cyl(r,h,p):return cq.Workplane('XY').circle(r).extrude(h).translate(p).val()
def export(name,parts,contract):
 asm=cq.Assembly(name=name);data=bytearray();views=[];acc=[];meshes=[];nodes=[];mats=list(COLORS)
 def buf(a,typ,comp):
  a=np.asarray(a,dtype=np.float32 if comp==5126 else np.uint32);data.extend(b'\0'*((-len(data))%4));off=len(data);data.extend(a.tobytes());ix=len(views);views.append({'buffer':0,'byteOffset':off,'byteLength':a.nbytes});d={'bufferView':ix,'componentType':comp,'count':len(a),'type':typ}
  if typ=='VEC3':d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  acc.append(d);return len(acc)-1
 for nm,shape,mat,note in parts:
  assert shape.isValid(),nm;asm.add(shape,name=nm)
  ve,tr=CUSTOM_TESS[nm] if nm in CUSTOM_TESS else shape.tessellate(.3,.45);v=np.array([[q.x,q.y,q.z] for q in ve])/1000;v=v[np.asarray(tr)].reshape(-1,3);n=np.cross(v[1::3]-v[::3],v[2::3]-v[::3]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);n=np.repeat(n,3,axis=0)
  meshes.append({'name':nm,'primitives':[{'attributes':{'POSITION':buf(v,'VEC3',5126),'NORMAL':buf(n,'VEC3',5126)},'indices':buf(np.arange(len(v)),'SCALAR',5125),'material':mats.index(mat)}]});nodes.append({'name':nm,'mesh':len(meshes)-1,'extras':{'classification':'original_source_dimensional_interface','qualified':False,'source':contract['source'],'note':note}})
 doc={'asset':{'version':'2.0','generator':'Original catalogue datum CAD E01'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':[{'name':k,'pbrMetallicRoughness':{'baseColorFactor':v,'metallicFactor':.6 if k in ['copper','steel'] else 0,'roughnessFactor':.6},**({'alphaMode':'BLEND','doubleSided':True} if k=='cover' else {})} for k,v in COLORS.items()],'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':acc,'extras':{'unit':'metre','up':'Z','electrically_qualified':False,'vehicle_placed':contract.get('vehicle_placed',False)}}
 js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);data+=b'\0'*((-len(data))%4)
 (P/(name+'.glb')).write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(data))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(data),0x004e4942)+data);asm.save(str(P/(name+'.step')))
 contract.update(files=[name+'.glb',name+'.step'],original_named_parts=len(parts),geometry_valid=True,source_CAD_read=contract.get('source_CAD_read',False),vehicle_placed=contract.get('vehicle_placed',False),supplier_contours_exact=False,electrical_qualified=False)
 bounds=[]
 for _,sh,_,_ in parts:
  b=sh.BoundingBox();bounds.append([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
 contract['actual_model_bounds_mm']=np.array(bounds).min(axis=0)[:3].tolist()+np.array(bounds).max(axis=0)[3:].tolist();return contract

CUSTOM_TESS={}
def route_mesh(r):
 import math
 pts=[]
 for seg in r['points_by_segment_C_mm']:
  for p in seg:
   if not pts or np.linalg.norm(np.array(p)-pts[-1])>1e-7:pts.append(np.array(p))
 pts=np.array(pts);d=np.diff(pts,axis=0);d/=np.linalg.norm(d,axis=1)[:,None];t=np.vstack((d[0],d[:-1]+d[1:],d[-1]));t/=np.linalg.norm(t,axis=1)[:,None];t[0]=[-1,0,0];t[-1]=[0,1,0];ve=[];tr=[];N=24
 for p,a in zip(pts,t):
  u=np.cross(a,[0,0,1]);u/=np.linalg.norm(u);v=np.cross(a,u)
  for k in range(N):ve.append(cq.Vector(*(p+7.1*(u*math.cos(2*math.pi*k/N)+v*math.sin(2*math.pi*k/N)))))
 for i in range(len(pts)-1):
  for k in range(N):a=i*N+k;b=i*N+(k+1)%N;c=(i+1)*N+(k+1)%N;d=(i+1)*N+k;tr.extend([(a,b,c),(a,c,d)])
 for end in [0,-1]:
  center=len(ve);ve.append(cq.Vector(*pts[end]));base=0 if end==0 else(len(pts)-1)*N
  for k in range(N):a=base+k;b=base+(k+1)%N;tr.append((center,b,a)if end==0 else(center,a,b))
 return ve,tr
