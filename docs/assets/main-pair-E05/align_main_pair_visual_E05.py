"""Keep original visual cable end planes exactly aligned to source lug mouths.
STEP geometry is unchanged; this refreshes only the original lightweight GLB.
"""
from pathlib import Path
import json,struct,hashlib,numpy as np
import cad_export_E05 as ce
P=Path(__file__).resolve().parent;O=P/'main_routes_E05';p=O/'main_pair_supported_E05.glb';b=p.read_bytes();jl=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+jl]);data=bytearray(b[28+jl:]);c=json.loads((O/'main_pair_contract_E05.json').read_text());checks=[]
for r in c['routes']:
 node=next(n for n in j['nodes']if n['name']==r['id']+'_70mm2_routed_jacket');pr=j['meshes'][node['mesh']]['primitives'][0];ve,tr=ce.route_mesh(r);v=np.array([[q.x,q.y,q.z]for q in ve])/1000;v=v[np.asarray(tr)].reshape(-1,3);nn=np.cross(v[1::3]-v[::3],v[2::3]-v[::3]);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-30);nn=np.repeat(nn,3,axis=0)
 for field,arr in [('POSITION',v),('NORMAL',nn)]:
  ac=j['accessors'][pr['attributes'][field]];bv=j['bufferViews'][ac['bufferView']];ar=arr.astype(np.float32);assert len(ar)==ac['count']and ar.nbytes==bv['byteLength'];off=bv.get('byteOffset',0)+ac.get('byteOffset',0);data[off:off+ar.nbytes]=ar.tobytes();ac['min']=ar.min(axis=0).tolist();ac['max']=ar.max(axis=0).tolist()
 # Last24 triangles are the actual planar destination cap.
 cap=v[-72:]*1000;err=float(np.max(np.abs(cap[:,1]-r['end_C_mm'][1])));checks.append({'route':r['id'],'end_plane_Y_error_mm':err,'pass':err<1e-8})
js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);data+=b'\0'*((-len(data))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(data))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(data),0x004e4942)+data)
out={'revision':'E05','source_STEP_unchanged_SHA256':hashlib.sha256((O/'main_pair_supported_E05.step').read_bytes()).hexdigest(),'GLB_SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'destination_cap_checks':checks,'pass':all(r['pass']for r in checks),'visual_not_metrology_mesh':True};(O/'visual_endplane_check_E05.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
