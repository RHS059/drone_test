from pathlib import Path
import hashlib,json,zipfile
P=Path(__file__).resolve().parent
names=['README.md','reference_evidence_S01.json','SOURCES.json','parameters.json','service_interface_contract_S01.json','build_fixtures.py','verify_interfaces.py','write_contract.py','preview_fixtures.py','package_release.py','parts_S01.csv','chassis_trestles_S01.step','chassis_trestles_S01.glb','chassis_trestles_S01_verification.json','corner_cradle_S01.step','corner_cradle_S01.glb','corner_cradle_S01_verification.json','service_fixtures_S01.glb','interface_verification_S01.json','service_fixtures_S01_preview.png']
for n in names:assert (P/n).is_file(),n
v=json.loads((P/'interface_verification_S01.json').read_text())
def no_clash(x):
 if isinstance(x,dict):
  if 'positive_volume_intersections_mm3'in x:assert not x['positive_volume_intersections_mm3'],x
  for y in x.values():no_clash(y)
 elif isinstance(x,list):
  for y in x:no_clash(y)
no_clash(v)
for t in v['export_roundtrip']:
 assert t['STEP_valid'] and t['STEP_solid_count']==t['GLB_nodes'] and t['bounds_max_delta_mm']<.001,t
for n in ['chassis_trestles_S01_verification.json','corner_cradle_S01_verification.json']:
 d=json.loads((P/n).read_text());assert d['all_single_valid_solids'];no_clash(d)
manifest={'revision':'S01','original_fixture_geometry_only':True,'fabrication_release':False,'files':[{'path':n,'bytes':(P/n).stat().st_size,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()}for n in names]}
(P/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(P/'original_workshop_fixtures_S01.zip','w',zipfile.ZIP_DEFLATED,9)as z:
 for n in names+['SHA256SUMS.json']:z.write(P/n,n)
receipt={'archive':'original_workshop_fixtures_S01.zip','bytes':(P/'original_workshop_fixtures_S01.zip').stat().st_size,'sha256':hashlib.sha256((P/'original_workshop_fixtures_S01.zip').read_bytes()).hexdigest(),'file_count':len(names)+1,'geometry_checks':'passed as scoped in interface_verification_S01.json','load_rating':None,'not_fabrication_released':True}
(P/'package_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
