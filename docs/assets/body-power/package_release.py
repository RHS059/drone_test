from pathlib import Path
import json,hashlib,zipfile,base64,datetime
P=Path(__file__).resolve().parent
r=json.loads((P/'verification.json').read_text())
assert r['individual_valid'] and all(x['solid_count']==1 for x in r['parts'])
assert not any(r[k] for k in ['positive_volume_body_intersections','frame_intersections','dimensional_reservation_intersections'])
a=json.loads((P/'arm_triangle_clearance_screen.json').read_text());assert not a['unresolved_pairs']
c=json.loads((P/'reservation_checks.json').read_text());assert all(x['body_intersection_mm3']<1e-3 for x in c['suspension_reservations'])
# An unexecuted, self-contained Colab notebook with original source/frame only.
# It explicitly distinguishes prepared notebook from completed remote execution.
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'colab':{'name':'Original rover body_power_R01.ipynb'}},'cells':[]}
def md(t):nb['cells'].append({'cell_type':'markdown','metadata':{},'source':t.splitlines(True)})
def code(t):nb['cells'].append({'cell_type':'code','metadata':{},'source':t.splitlines(True),'outputs':[],'execution_count':None})
md('# Original rover body/power R01\n\nPrepared portable notebook, not yet executed in Colab. These are original manufacturing-development solids, not a qualified vehicle or detailed supplier electronics CAD. Supplier envelopes are kept in a separate file. The embedded reference frame is original R06 engineering CAD. No restricted motor CAD is included.\n\nRunning all cells installs CadQuery from the normal Python package registry, reconstructs the original panels and hardware, checks interference against the original frame, then produces STEP/GLB and evidence. Colab may require restarting the runtime after the dependency cell. Native CAD is millimetres; GLB is metres, Z-up.\n')
code('%pip install -q cadquery==2.7.0 "numpy>=1.26,<3" "matplotlib>=3.8,<4"\n')
code("from pathlib import Path\nimport base64\nP=Path('/content/body_power_R01')\nP.mkdir(exist_ok=True)\n"+f"(P/'build_body_power.py').write_text({(P/'build_body_power.py').read_text()!r})\n"+f"(P/'reference_frame_R06.step').write_bytes(base64.b64decode({base64.b64encode((P/'reference_frame_R06.step').read_bytes()).decode()!r}))\n"+f"(P/'README.md').write_text({(P/'README.md').read_text()!r})\n"+f"(P/'SOURCES.json').write_text({(P/'SOURCES.json').read_text()!r})\n")
code("import subprocess, sys\nsubprocess.run([sys.executable, str(P/'build_body_power.py')], check=True)\n")
code("import json\nr=json.loads((P/'verification.json').read_text())\nassert r['individual_valid']\nassert not r['positive_volume_body_intersections']\nassert not r['frame_intersections']\nassert not r['dimensional_reservation_intersections']\nprint({k:r[k] for k in ['original_part_count','bounds_m','body_hardware_mass_kg','body_hardware_com_m']})\nprint('Geometric checks passed; no fabrication, electrical, motion, IP or safety qualification implied.')\n")
code("import shutil\narchive=shutil.make_archive('/content/body_power_R01_outputs','zip',P)\nfrom google.colab import files\nfiles.download(archive)\n")
(P/'body_power_R01_colab.ipynb').write_text(json.dumps(nb,indent=1))
# Record manifest only after final verification. Do not hash transient build/QA log files.
files=[f for f in P.iterdir() if f.is_file() and f.suffix in ['.py','.json','.csv','.md','.txt','.step','.glb','.png','.ipynb'] and f.name not in ['SHA256SUMS.json','contract_draft.json','write_evidence.py']]
manifest={'revision':'R01','portable_notebook_status':'prepared, not executed in Colab','geometry_part_count':r['original_part_count'],'files':[{'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(files)],'restricted_supplier_geometry_included':False}
(P/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(P/'original_body_power_R01.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files+[P/'SHA256SUMS.json']:z.write(f,f.name)
print(json.dumps({'archive':str(P/'original_body_power_R01.zip'),'bytes':(P/'original_body_power_R01.zip').stat().st_size,'parts':r['original_part_count'],'mass_kg':r['body_hardware_mass_kg'],'C02_shock_box_min_distance_m':c['minimum_clearance_m']}))
