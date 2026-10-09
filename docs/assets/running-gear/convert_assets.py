import pathlib,json,hashlib,numpy as np,trimesh
p=pathlib.Path(__file__).parent
report={}
for f in p.glob('*.stl'):
 m=trimesh.load(f,process=False)
 # Preserve all OEM triangle vertices. Reorientation only, no rescaling or smoothing.
 raw_bounds=m.bounds.tolist()
 if f.name in ['wheel.stl','rocker.stl','fenders.stl']:
  m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,0,1]))
 color=[45,48,51,255] if f.name in ['wheel.stl','rocker.stl'] else [128,139,145,255]
 m.visual.vertex_colors=color
 out=p/(f.stem+'-zup-m.glb');m.export(out)
 report[f.name]={'triangles':len(m.faces),'source_bounds_m':raw_bounds,'output_bounds_m':m.bounds.tolist(),'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'rotation_z_rad':float(np.pi/2) if f.name in ['wheel.stl','rocker.stl','fenders.stl'] else 0,'units':'metres','scale':1,'glb':out.name,'watertight_after_exact_vertex_merge':bool(trimesh.Trimesh(vertices=m.vertices,faces=m.faces,process=True).is_watertight)}
(p/'geometry-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
