"""Independent delivered-file checks; no assumption is elevated to an OEM verified fact."""
from pathlib import Path
import struct,json,math,hashlib
import numpy as np
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).resolve().parent

def bbox(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);return list(b.Get())
def glb_read(path):
 b=path.read_bytes();magic,ver,total=struct.unpack_from('<III',b)
 assert magic==0x46546c67 and ver==2 and total==len(b)
 jl,jt=struct.unpack_from('<II',b,12);assert jt==0x4e4f534a
 j=json.loads(b[20:20+jl]);o=20+jl;bl,bt=struct.unpack_from('<II',b,o);assert bt==0x004e4942
 data=b[o+8:o+8+bl]
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']]
  typ={5126:np.float32,5125:np.uint32}[a['componentType']];columns={'SCALAR':1,'VEC3':3}[a['type']]
  return np.frombuffer(data,dtype=typ,offset=v.get('byteOffset',0)+a.get('byteOffset',0),count=a['count']*columns).reshape(-1,columns)
 return j,acc

def main():
 tests={};details={}
 model={n:cq.importers.importStep(str(P/(n+'_C01.step'))).val() for n in ('tire','rim')}
 for n,s in model.items():
  tests[n+'_step_valid_single_solid']=s.isValid() and len(s.Solids())==1
  details[n+'_step_bounds_mm']=bbox(s)
 tests['step_tire_rim_clear']=model['tire'].intersect(model['rim']).Volume()<1e-4
 j,acc=glb_read(P/'wheel_C01.glb')
 tests['two_exact_node_names']=sorted(n['name'] for n in j['nodes'])==['rim','tire']
 tests['identity_source_scale']=all('scale' not in n and 'matrix' not in n and 'rotation' not in n for n in j['nodes'])
 tests['explicit_metre_Zup_Yaxle_contract']=j['extras']['units']=='metres' and j['extras']['upAxis']=='Z' and j['extras']['axleAxis']=='+Y'
 for mesh in j['meshes']:
  name=mesh['name'];pr=mesh['primitives'][0];v=acc(pr['attributes']['POSITION']);f=acc(pr['indices']).flatten().reshape(-1,3)
  tests[name+'_finite_and_valid_triangles']=bool(np.isfinite(v).all() and f.max()<len(v))
  details[name+'_glb_bounds_m']=[v.min(0).tolist(),v.max(0).tolist()]
  exact=np.array(details[name+'_step_bounds_mm']).reshape(2,3)/1000
  tests[name+'_glb_bounds_close_to_native']=bool(np.max(np.abs(np.array(details[name+'_glb_bounds_m'])-exact))<.00031)
  tests[name+'_nonzero_triangle_area']=bool((np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-13).all())
 iface=json.loads((P/'interface_contract.json').read_text());lug=np.array(iface['lug_centers_mount_face_m'])
 tests['pcd165_1_and_phase36']=bool(np.allclose(np.linalg.norm(lug[:,[0,2]],axis=1),.08255,atol=1e-10) and abs(math.degrees(math.atan2(lug[0,2],lug[0,0]))-36)<1e-7)
 tests['mount_face18mm']=bool(np.allclose(lug[:,1],.018,atol=1e-12))
 tests['tire_envelope876_3by317_5']=bool(np.allclose(np.diff(np.array(details['tire_step_bounds_mm']).reshape(2,3),axis=0)[0],[876.3,317.5,876.3],atol=1e-5))
 report={'tests':tests,'all_pass':all(tests.values()),'details':details,'scope':'File validity, dimensions and nominal interfaces only; not actual product/structural qualification.'}
 (P/'independent_verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2));assert report['all_pass']
if __name__=='__main__':main()
