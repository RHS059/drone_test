#!/usr/bin/env python3
"""Standard-library regression tests. No network, original-directory or CAD writes."""
from pathlib import Path
import copy,csv,hashlib,io,json,math,shutil,struct,subprocess,sys,tempfile,unittest
import build_cost_model as B
HERE=Path(__file__).resolve().parent
B.build()
M=B.load('cost_model.json');BASE=B.load(B.C04+'cost_model.json');D=B.load('delta_summary.json');L=B.load('material_mass_ledger_E05.json');R=B.load('replacement_map.json');BODY=B.load('body_composition.json');OLD_BODY=B.load(B.C04+'body_composition.json');PARTS={p['id']:p for p in M['parts']};E=[p for p in M['parts'] if p['id'].startswith('E05:')]
def glb_names(path):
 raw=path.read_bytes();assert raw[:4]==b'glTF'
 n,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
 return [n['name'] for n in json.loads(raw[20:20+n])['nodes'] if n.get('name')]
class PatchTests(unittest.TestCase):
 def test_01_input_hashes(self):B.validate_inputs()
 def test_02_baseline_mass(self):self.assertAlmostEqual(D['baseline_known_subset_kg'],1268.0641640992537,10)
 def test_03_exact_two_replacements(self):self.assertEqual(R['replace_by_name'],['controller_battery_partition','battery_tool_partition']);self.assertEqual(len(R['replacements']),2)
 def test_04_partition_values(self):
  expected={'controller_battery_partition':1.8943146236770079,'battery_tool_partition':1.959640700315806}
  for r in R['replacements']:self.assertAlmostEqual(r['new']['mass_kg'],expected[r['name']],12);self.assertAlmostEqual(r['known_mass_delta_kg'],-0.008079899844865,12)
 def test_05_four_cylindrical_cuts(self):
  removed=4*math.pi*(25.2/2)**2*3
  self.assertAlmostEqual(-D['partition_replacement_delta_kg'],removed*2700/1e9,10)
 def test_06_deck_byte_equivalent_object(self):
  old=next(r for r in OLD_BODY['parts'] if r['name']=='main_base_deck_3mm');self.assertEqual(R['deck'],old);self.assertTrue(R['deck_40_bores_unchanged'])
 def test_07_other_235_body_parts_unchanged(self):
  old={r['name']:r for r in OLD_BODY['parts']};new={r['name']:r for r in BODY['parts']};self.assertEqual(len(new),237)
  for n,r in old.items():
   if n not in R['replace_by_name']:self.assertEqual(r,new[n])
 def test_08_one_body_BOM_row(self):
  self.assertEqual([p['id'] for p in M['parts'] if p['mass_group']=='body'],['body_composed']);self.assertAlmostEqual(PARTS['body_composed']['unit_mass_kg'],BODY['modeled_original_mass_kg'],12)
 def test_09_98_named_added_nodes(self):
  self.assertEqual(len(E),98);self.assertEqual(len({p['id'] for p in E}),98);self.assertEqual(len(M['parts']),328)
  self.assertEqual({p['ledger_node'] for p in E},set(B.load(B.E05+'main_pair_graph_E05.json')['nodes']))
 def test_10_main_GLB_names(self):self.assertEqual(set(glb_names(HERE/B.E05/'main_pair_supported_E05.glb')),set(R['new_E05_nodes']))
 def test_11_partition_GLB_names(self):self.assertEqual(set(glb_names(HERE/B.E05/'partition_main_glands_E05.glb')),set(R['replace_by_name']))
 def test_12_explicit_aluminium_density(self):
  rows=[r for r in L['parts'] if r['category']=='original_aluminium_stand'];self.assertEqual(len(rows),8)
  for r in rows:self.assertEqual(r['density_kg_m3_assumed'],2700);self.assertIn('aluminium',r['actual_material']);self.assertAlmostEqual(r['accepted_known_mass_kg'],r['volume_mm3']*2700/1e9,12)
 def test_13_steel_palette_not_used(self):
  source=(HERE/'inputs/E05/build_main_pair_E05.py').read_text();self.assertIn("'_welded_stand',stand,'steel'",source)
  self.assertAlmostEqual(D['new_original_aluminium_stands_kg'],0.4274107601194724,12)
  self.assertNotAlmostEqual(D['new_original_aluminium_stands_kg'],0.4274107601194724*7850/2700,6)
 def test_14_fasteners_unknown(self):
  rows=[p for p in E if p['E05_category']=='commercial_fastener_unselected'];self.assertEqual(len(rows),64)
  self.assertEqual(sum('_M4x30_' in p['id'] for p in rows),16);self.assertEqual(sum('_washer_' in p['id'] for p in rows),32);self.assertEqual(sum('_M4nut_' in p['id'] for p in rows),16)
  for p in rows:self.assertIsNone(p['sku']);self.assertIsNone(p['unit_mass_kg']);self.assertIsNone(p['unit_price']);self.assertFalse(p['included_in_pinned_mass_subtotal'])
 def test_15_glands_unknown(self):
  rows=[p for p in E if p['E05_category'] in ['purchased_gland','purchased_locknut']];self.assertEqual(len(rows),8)
  self.assertEqual(sum(p['sku']=='53111030' for p in rows),4);self.assertEqual(sum(p['sku']=='53119030' for p in rows),4)
  for p in rows:self.assertIsNone(p['unit_mass_kg']);self.assertIsNone(p['unit_price'])
 def test_16_clamps_unknown(self):
  rows=[p for p in E if p['E05_category']=='original_clamp_material_unknown'];self.assertEqual(len(rows),16)
  for p in rows:self.assertIsNone(p['unit_mass_kg']);self.assertIsNone(p['unit_price'])
 def test_17_catalogue_weight_not_copper_index(self):
  obs=B.load('inputs/manufacturer_cable_observation.json');self.assertEqual(obs['article'],'0060001');self.assertEqual(obs['fields']['weight_kg_per_km'],724);self.assertEqual(obs['fields']['copper_index_kg_per_km'],672)
  for p in E:
   if p['E05_category']=='manufacturer_cable_length':self.assertEqual(p['unit_mass_kg'],0.724)
 def test_18_cut_lengths_and_mass(self):
  rows={r['route_id']:r for r in L['parts'] if r['route_id']};self.assertAlmostEqual(rows['MAIN_positive']['nominal_routed_length_m'],2.7697464313510465,12);self.assertAlmostEqual(rows['MAIN_negative']['nominal_routed_length_m'],2.8582812556571024,12)
  self.assertAlmostEqual(D['nominal_routed_cable_length_m'],5.628027687008149,12);self.assertAlmostEqual(D['nominal_routed_cable_mass_kg'],4.0746920453939,12)
  for r in rows.values():self.assertIsNone(r['procurement_cut_length_m']);self.assertIsNone(r['density_kg_m3_assumed']);self.assertIsNone(r['installed_mass_kg'])
 def test_19_no_optional_lead_term(self):
  o=R['optional_local_leads'];self.assertEqual(o['selected_runtime_occurrences'],0);self.assertEqual(o['selected_mass_ledger_occurrences'],0);self.assertEqual(o['mass_delta_kg'],0)
  for n in o['names']:self.assertFalse(any(n in p['id'] for p in M['parts']))
 def test_20_reused_terminal_hardware_unchanged(self):
  for p in BASE['parts']:
   if p['id'] not in ['body_composed','remaining_harness']:self.assertEqual(PARTS[p['id']],p)
 def test_21_mass_arithmetic(self):
  expected=1268.0641640992537-0.016159799689751956+0.4274107601194724+4.0746920453939
  self.assertAlmostEqual(D['candidate_known_subset_kg'],expected,10);self.assertAlmostEqual(D['known_subset_delta_kg'],4.48594300582362,11)
  self.assertAlmostEqual(sum(p['quantity']*p['unit_mass_kg'] for p in M['parts'] if p['included_in_pinned_mass_subtotal']),D['candidate_known_subset_kg'],10)
 def test_22_groups_preserved(self):
  for k,v in BASE['mass_context']['mass_groups_kg'].items():
   if k!='body':self.assertEqual(M['mass_context']['mass_groups_kg'][k],v)
 def test_23_USD_PLN_baskets_identical(self):
  self.assertEqual(M['build_summary']['public_price_baskets'],BASE['build_summary']['public_price_baskets']);self.assertEqual({x['currency']:x['reference_subtotal'] for x in M['build_summary']['public_price_baskets']},{'USD':17200.0,'PLN':6090.0})
 def test_24_all_added_costs_unknown(self):
  for p in E:
   for key in ['unit_price','extended_price','currency']:self.assertIsNone(p[key])
  self.assertIsNone(D['E05_complete_cost']);self.assertIsNone(M['build_summary']['complete_build_cost'])
 def test_25_operating_scenarios_unchanged(self):self.assertEqual(M['operating_cost'],BASE['operating_cost'])
 def test_26_actuals_null(self):
  self.assertIsNone(M['mass_context']['whole_vehicle_mass_kg']);self.assertIsNone(M['operating_cost']['actual_cost_per_operating_hour']);self.assertIsNone(M['operating_cost']['whole_rover_runtime_hours'])
  for s in M['operating_cost']['scenarios']:self.assertIsNone(s['outputs']['whole_rover_runtime_hours']);self.assertIsNone(s['outputs']['complete_operating_cost_usd_per_hour'])
 def test_27_only_two_geometric_routes(self):
  c=M['electrical_context'];self.assertEqual(c['E05_geometric_main_route_count'],2);self.assertFalse(c['E05_conductive_crimp_contact_verified']);self.assertFalse(c['E05_energizable']);self.assertFalse(c['electrical_end_to_end_complete']);self.assertFalse(c['cap_enforced'])
 def test_28_csv_roundtrip_nulls(self):
  with (HERE/'BOM.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),328)
  for p in rows[230:]:self.assertEqual(p['unit_price'],'null');self.assertEqual(p['extended_price'],'null');self.assertEqual(p['installed_mass_kg'],'null');self.assertEqual(p['procurement_cut_length_m'],'null')
 def test_29_12_upstream_hashes(self):
  d=B.load('dependency_manifest.json')['upstream_separately_supplied']['dependencies'];self.assertEqual(len(d),12)
  for r in d:self.assertEqual(r['sha256'],r['verified_sha256']);self.assertFalse(r['required_for_mass_replay'])
 def test_30_historical_files_resolve(self):
  for f in [M['historical_model']['file'],M['historical_model']['source_file'],M['electrical_context']['temperature_limits_file']]:self.assertTrue((HERE/f).is_file(),f)
 def test_31_deterministic_rebuild(self):
  before={f:(HERE/f).read_bytes() for f in B.OUTPUTS+['output-checksums.json']};B.build()
  for f,data in before.items():self.assertEqual(data,(HERE/f).read_bytes(),f)
 def test_32_tamper_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'patch';shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__'));p=target/'inputs/explicit_material_ledger_E05.json';p.write_text(p.read_text()+' ')
   out=subprocess.run([sys.executable,str(target/'build_cost_model.py')],capture_output=True,text=True);self.assertNotEqual(out.returncode,0);self.assertIn('Frozen input changed',out.stderr)
 def test_33_isolated_baseline_rebuild(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'C04';shutil.copytree(HERE/B.C04,target);before=(target/'cost_model.json').read_bytes()
   out=subprocess.run([sys.executable,str(target/'build_cost_model.py')],capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr);self.assertEqual(before,(target/'cost_model.json').read_bytes())
 def test_34_all_88_unknown_nodes(self):self.assertEqual(sum(r['accepted_known_mass_kg'] is None for r in L['parts']),88)
 def test_35_procurement_not_released(self):
  for r in L['parts']:self.assertFalse(r['procurement_released']);self.assertEqual(r['manufacturer_article_identified'],r['sku'] is not None)
 def test_36_baseline_input_bytes_unchanged(self):
  # Does not read outside this portable package; all immutable baseline pins survive replay.
  for f,h in B.load(B.C04+'checksums.json').items():self.assertEqual(B.sha(HERE/B.C04/f),h)
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(PatchTests);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);report=stream.getvalue();print(report,end='');(HERE/'test_run.log').write_text(report)
 B.write('validation.json',dict(revision='C04+E05_R01',tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),all_pass=result.wasSuccessful(),scope='Offline arithmetic, source/dependency hashes, exact replacements, unchanged body/deck, explicit materials, no duplication, price/unknown preservation, route scope, CSV and deterministic rebuild. No independent CAD-kernel rerun, weighed mass, procurement or engineering qualification.'))
 sys.exit(0 if result.wasSuccessful() else 1)
