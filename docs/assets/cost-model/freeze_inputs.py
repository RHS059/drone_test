#!/usr/bin/env python3
"""Explicit maintainer-only snapshot; refuse overwriting an existing freeze."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,x):(ROOT/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
if (ROOT/'input-manifest.json').exists():raise SystemExit('Existing freeze: inspect and deliberately version changes; automatic refresh prohibited.')
rows=[]
def copy(source,dest):
 d=ROOT/dest;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,d)
 rows.append(dict(file=dest,source=str(source.relative_to(BASE)),sha256=sha(d),bytes=d.stat().st_size))
for p in sorted((BASE/'cost-model-C04').rglob('*')):
 if p.is_file() and '__pycache__' not in p.parts:copy(p,'inputs/C04/'+str(p.relative_to(BASE/'cost-model-C04')))
e=BASE/'electrical-drive'; allow=json.loads((e/'main_routes_E05/PUBLIC_FILES_E05.json').read_text())
for path in allow['allowlist']:
 assert sha(e/path)==allow['sha256'][path],('E05 freeze changed',path)
 copy(e/path,'inputs/E05/'+path)
for f in ['FREEZE_E05.json','PUBLIC_FILES_E05.json']:copy(e/'main_routes_E05'/f,'inputs/E05/main_routes_E05/'+f)
for path in ['docs/connected/electrical-scene.mjs','docs/assets/connected-electrical/electrical-contract.json']:
 copy(BASE/'app-C04'/path,'inputs/runtime_C04/'+Path(path).name)
deps=json.loads((e/'main_routes_E05/INPUT_HASHES_E05.json').read_text())['existing_selected_source_dependencies']
upstream=[]
for path,expected in deps.items():
 p=(e/path).resolve();observed=sha(p);assert observed==expected,('upstream dependency drift',path)
 upstream.append(dict(path=path,source_relative_to_integration=str(p.relative_to(BASE)),sha256=expected,verified_sha256=observed,bundled=False,required_for_mass_replay=False))
write('inputs/upstream_dependency_verification.json',dict(as_of='2026-10-09',dependencies=upstream,note='Original upstream CAD stays separately supplied; hashes verified at freeze. Normal mass replay uses bundled source ledgers and does not rebuild CAD.'))
contract=json.loads((e/'main_routes_E05/main_pair_contract_E05.json').read_text());ledger=[]
for p in contract['parts']:
 n=p['name'];mat=p['actual_material'];density=None;sku=None
 if mat=='aluminium matched to selected deck; exact alloy/temper pending':category='original_aluminium_stand';density=2700
 elif mat=='source cable insulation envelope':category='manufacturer_cable_length';sku='0060001'
 elif mat=='original clamp polymer/liner unspecified':category='original_clamp_material_unknown'
 elif mat=='nominal steel hardware; grade and locking unspecified':category='commercial_fastener_unselected'
 elif mat=='purchased gland/locknut representation':category='purchased_gland' if n.endswith('53111030') else 'purchased_locknut';sku='53111030' if category=='purchased_gland' else '53119030'
 else:raise ValueError(mat)
 ledger.append(dict(name=n,category=category,actual_material=mat,density_kg_m3_assumed=density,sku=sku,display_palette_must_not_supply_material=True,material_source='E05/main_routes_E05/main_pair_contract_E05.json:parts.actual_material',density_basis='C04/body_composition.json:main_base_deck_3mm; 2700 kg/m3 assumed, exact alloy/temper unqualified' if density else None))
write('inputs/explicit_material_ledger_E05.json',dict(parts=ledger,policy='Exact source-name mapping. Display palette steel is never a material specification. Nominal fastener material is not a purchased mass source.'))
write('inputs/manufacturer_cable_observation.json',dict(id='lapp_0060001_mass',manufacturer='LAPP',article='0060001',family='ÖLFLEX HEAT 180 SiF',url='https://products.lappgroup.com/online-catalogue/power-and-control-cables/expanded-ambient-temperatures/silicone-single-cores/oelflex-heat-180-sif.html',verified_on='2026-10-09',method='Official manufacturer catalogue article table, header and exact SKU row checked using web reader.',fields=dict(conductor_cross_section_mm2=70,outside_diameter_nominal_mm=14.2,core_colour='black',copper_index_kg_per_km=672,weight_kg_per_km=724),source_locations=dict(table_header_line=145,article_row_line=263,nominal_values_note_line=327),mass_basis='Nominal manufacturer cable weight per km, includes cable construction. Copper index is a separate procurement index, not cable total weight.',unit_price=None,currency=None,is_supplier_quote=False,source_document_bundled=False))
guarded=[]
for d in ['cost-model-C04','publication-C04']:
 for p in sorted((BASE/d).rglob('*')):
  if p.is_file():guarded.append(dict(path=str(p.relative_to(BASE)),sha256=sha(p)))
for p in sorted((BASE/'app-C04').rglob('*')):
 if p.is_file() and '.git' not in p.parts and 'node_modules' not in p.parts:guarded.append(dict(path=str(p.relative_to(BASE)),sha256=sha(p)))
write('inputs/isolation_snapshot.json',dict(files=guarded,scope='Read-only source snapshot; no source/app/publication writes permitted. Normal builder does not inspect outside this folder.'))
for f in ['upstream_dependency_verification.json','explicit_material_ledger_E05.json','manufacturer_cable_observation.json','isolation_snapshot.json']:
 p=ROOT/'inputs'/f;rows.append(dict(file='inputs/'+f,source='locally authored factual snapshot',sha256=sha(p),bytes=p.stat().st_size))
write('input-manifest.json',dict(schema_version='1.0',revision='C04+E05_R01',as_of='2026-10-09',inputs=rows,normal_replay='Offline, bundled inputs only; never run freeze_inputs.py during a normal rebuild.'))
print('Frozen',len(rows),'inputs; verified',len(upstream),'upstream hashes.')
