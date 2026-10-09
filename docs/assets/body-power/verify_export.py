from pathlib import Path
import cadquery as cq,numpy as np,json,struct
P=Path(__file__).parent;r=json.loads((P/'verification.json').read_text())
s=cq.importers.importStep(str(P/'body_power_R01.step')).val();bb=s.BoundingBox();step_bounds=np.array([[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]])/1000
raw=(P/'body_power_R01.glb').read_bytes();magic,version,size=struct.unpack_from('<III',raw);assert magic==0x46546C67 and version==2 and size==len(raw)
jlen,jtype=struct.unpack_from('<II',raw,12);assert jtype==0x4E4F534A;doc=json.loads(raw[20:20+jlen]);globb=[]
for m in doc['meshes']:
 for q in m['primitives']:
  a=doc['accessors'][q['attributes']['POSITION']];globb.append([a['min'],a['max']])
globb=np.array(globb);glb_bounds=np.array([globb[:,0,:].min(0),globb[:,1,:].max(0)])
expected=np.array(r['bounds_m']);out={'step_solids':len(s.Solids()),'expected_solids':r['original_part_count'],'step_reimport_valid':s.isValid(),'step_bounds_m':step_bounds.tolist(),'GLB_mesh_count':len(doc['meshes']),'GLB_node_count':len(doc['nodes']),'GLB_bounds_m':glb_bounds.tolist(),'maximum_bound_error_m':float(max(np.abs(step_bounds-expected).max(),np.abs(glb_bounds-expected).max())),'metres_Z_up_explicit':doc['extras']['units']=='metres' and doc['extras']['upAxis']=='Z'}
assert out['step_solids']==r['original_part_count'];assert out['step_reimport_valid'];assert out['maximum_bound_error_m']<1e-6;assert out['metres_Z_up_explicit'];assert len(doc['nodes'])==r['original_part_count']
(P/'export_roundtrip.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
