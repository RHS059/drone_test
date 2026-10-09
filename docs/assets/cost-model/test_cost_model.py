#!/usr/bin/env python3
"""Independent arithmetic, selection and null checks for the public C04 cost package."""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json,subprocess,sys,unittest
HERE=Path(__file__).resolve().parent
M=json.loads((HERE/'cost_model.json').read_text());PARTS={x['id']:x for x in M['parts']}
S=json.loads((HERE/'sources.json').read_text());B=json.loads((HERE/'body_composition.json').read_text());E=json.loads((HERE/'electrical_mass_selection.json').read_text())
def inp(name):return json.loads((HERE/'inputs'/name).read_text())
class Costs(unittest.TestCase):
 def test_mechanical_freeze_binding(self):
  freeze=inp('PUBLIC_SOURCE_FREEZE_C04_R02.json');self.assertEqual(freeze['file_count'],575)
  index={r['path']:r['sha256'] for r in freeze['files']}
  for name in ['mechanical_mass_BOM_C04_R01.json','structural_connections_C04_R05_manifest.json']:self.assertEqual(hashlib.sha256((HERE/'inputs'/name).read_bytes()).hexdigest(),index['mechanical/connection_completion_C04/'+name])
 def test_ids_are_unique(self):self.assertEqual(len(PARTS),len(M['parts']))
 def test_frozen_inputs(self):
  for r in json.loads((HERE/'input-manifest.json').read_text())['inputs']:self.assertEqual(hashlib.sha256((HERE/r['file']).read_bytes()).hexdigest(),r['sha256'],r['file'])
 def test_complete_and_actual_unknown(self):
  self.assertIsNone(M['build_summary']['complete_build_cost']);self.assertIsNone(M['mass_context']['whole_vehicle_mass_kg'])
  self.assertIsNone(M['operating_cost']['actual_cost_per_operating_hour']);self.assertIsNone(M['operating_cost']['whole_rover_runtime_hours'])
  self.assertTrue(all(v is None for v in M['operating_cost']['actual_inputs'].values()))
  for s in M['operating_cost']['scenarios']:
   for k in ['complete_operating_cost_usd_per_hour','fully_burdened_cost_usd_per_hour','whole_rover_runtime_hours']:self.assertIsNone(s['outputs'][k])
 def test_replacement_skus(self):
  self.assertEqual(PARTS['rims']['sku'],'10005240');self.assertEqual(PARTS['batteries']['sku'],'BAT548110620');self.assertEqual(PARTS['wheel_nuts']['sku'],'22095')
  for r in M['parts']:
   self.assertFalse(any(x in (r['sku'] or '') for x in ['SE5240060141','CM0750180040','48V030-GC2','72204','B045']),r['id'])
  self.assertFalse(any('adapter' in r['id'].lower() for r in M['parts'] if r['id']!='adapter_R04'))
 def test_quantities(self):
  for id in ['rims','tires','drives','dampers','springs']:self.assertEqual(PARTS[id]['quantity'],6)
  for id in ['arms','arm_controllers','grippers','couplings','adapter_R04','batteries','steering_actuators']:self.assertEqual(PARTS[id]['quantity'],2)
  self.assertEqual(PARTS['wheel_nuts']['quantity'],30);self.assertEqual(PARTS['spherical_bearings']['quantity'],56)
  self.assertEqual(PARTS['motor_mount_screws']['quantity'],48)
 def test_unknown_purchased_masses(self):
  for id in ['drives','tires','wheel_nuts','dampers','battery_strap_pairs','grippers','couplings']:
   self.assertIsNone(PARTS[id]['unit_mass_kg']);self.assertFalse(PARTS[id]['included_in_pinned_mass_subtotal'])
 def test_price_extensions(self):
  for p in M['parts']:
   if p['unit_price'] is None or p['quantity'] is None:self.assertIsNone(p['extended_price'])
   else:self.assertEqual(Decimal(str(p['extended_price'])),Decimal(str(p['unit_price']))*Decimal(str(p['quantity'])))
 def test_currency_baskets(self):
  baskets={x['currency']:x for x in M['build_summary']['public_price_baskets']};self.assertEqual(set(baskets),{'PLN','USD'})
  self.assertEqual(baskets['PLN']['reference_subtotal'],6090);self.assertEqual(baskets['USD']['reference_subtotal'],17200)
  for currency,b in baskets.items():
   self.assertEqual(sum(Decimal(str(PARTS[x]['extended_price'])) for x in b['line_ids']),Decimal(str(b['reference_subtotal'])))
   self.assertTrue(all(PARTS[x]['currency']==currency for x in b['line_ids']));self.assertFalse(b['complete_build_total']);self.assertIsNone(b['shipping_total'])
 def test_no_invented_quote(self):
  for p in M['parts']:self.assertIsNone(p['quote_date']);self.assertFalse(p['is_supplier_quote'])
  for id in ['rims','wheel_nuts','battery_strap_pairs']:self.assertIsNone(PARTS[id]['unit_price'])
  for id in ['batteries','battery_bms']:self.assertEqual(PARTS[id]['price_reference_period'],'2026 Q2')
 def test_price_source_links(self):
  sources={s['id']:s for s in S['observations']}
  for p in M['parts']:
   for id in p['source_ids']:self.assertIn(id,sources)
   if p['unit_price'] is not None:self.assertIn(p['price_source_id'],sources);self.assertTrue(p['price_source_url'].startswith('https://'))
 def test_straps_are_two_pairs(self):
  p=PARTS['battery_strap_pairs'];self.assertEqual(p['quantity'],2);self.assertEqual(p['quantity_unit'],'retail pair');self.assertEqual(p['physical_strap_count'],4)
  self.assertEqual(p['sku'],'60027.01.112');self.assertIsNone(p['unit_price']);self.assertIsNone(p['unit_mass_kg'])
  self.assertEqual(inp('battery_strap_source.json')['exact_variant_price'],None)
 def test_mass_arithmetic(self):
  total=sum(p['quantity']*p['unit_mass_kg'] for p in M['parts'] if p['included_in_pinned_mass_subtotal'])
  self.assertAlmostEqual(total,M['mass_context']['pinned_known_subset_kg'],8)
  self.assertAlmostEqual(total,sum(M['mass_context']['mass_groups_kg'].values()),8)
  for p in M['parts']:
   if p['included_in_pinned_mass_subtotal']:self.assertIsNotNone(p['unit_mass_kg']);self.assertIsNotNone(p['quantity'])
 def test_mechanical_subtotals(self):
  g=M['mass_context']['mass_groups_kg'];self.assertAlmostEqual(g['structure'],347.91233280933164,8);self.assertAlmostEqual(g['joint_details'],14.017320451359337,8);self.assertAlmostEqual(g['shock_details'],16.939269948424055,8)
  self.assertAlmostEqual(g['mechanical_purchased'],6*19.5+2*7+6*3.54,8)
  self.assertEqual(sum(p['quantity'] for p in M['parts'] if p.get('mass_group')=='structure'),126)
 def test_spring_count_once(self):
  self.assertEqual(PARTS['springs']['unit_mass_kg'],3.54)
  self.assertFalse(any('original_profile' in p['id'] and p['included_in_pinned_mass_subtotal'] for p in M['parts']))
 def test_body_composition(self):
  self.assertEqual([x['part_count'] for x in B['history']],[267,267,271,237]);self.assertEqual(len({x['name'] for x in B['parts']}),len(B['parts']))
  names={x['name'] for x in B['parts']};ba=inp('battery_BA02_manifest.json')
  self.assertEqual(len(ba['remove_names']),34);self.assertEqual(len(ba['remove_external_proxy_names']),4)
  self.assertFalse(names.intersection(ba['remove_names']));self.assertTrue(set(ba['replace_names']).issubset(names))
  self.assertAlmostEqual(sum(x['mass_kg'] for x in B['parts'] if x['mass_kg'] is not None),PARTS['body_composed']['unit_mass_kg'],9)
 def test_body_densities_and_replacement(self):
  body={x['name']:x for x in B['parts']}
  for r in B['parts']:
   if r['mass_kg'] is not None:self.assertAlmostEqual(r['volume_mm3']*r['density_kg_m3']/1e9,r['mass_kg'],9)
  for x in inp('body_SO02_E04P_parts.json')['parts']:self.assertAlmostEqual(body[x['name']]['volume_mm3'],x['volume_mm3'],6)
  for n in body:
   if '_nutplate_' in n or n.endswith('_tapped_boss'):self.assertEqual(body[n]['density_kg_m3'],2700)
 def test_battery_mass_separate_from_floor(self):
  ba=inp('battery_BA02_manifest.json');self.assertEqual(ba['battery_mass_kg'],74)
  self.assertAlmostEqual(PARTS['battery_mount_BA02']['unit_mass_kg'],ba['mass_accounting']['original_hardware_kg_excluding_replacement_floor'],9)
  floor=next(x for x in B['parts'] if x['name']=='battery_well_floor_3mm')['mass_kg']
  self.assertAlmostEqual(floor+PARTS['battery_mount_BA02']['unit_mass_kg'],ba['mass_accounting']['original_hardware_kg_including_replacement_floor'],8)
 def test_electrical_proxy_exclusion(self):
  for r in E['parts']:
   if not r['selected_after_overlay'] or r['name']=='LYNX1000_original_max_housing_and_mount_interface' or 'approximate copper contact' in (r['material_basis'] or '') or 'dimensioned copper lug' in (r['material_basis'] or ''):
    self.assertFalse(r['accepted_into_C04_known_subset']);self.assertIsNone(r['accepted_mass_kg'])
  self.assertEqual(PARTS['battery_bms']['unit_mass_kg'],2.7)
  self.assertAlmostEqual(sum(r['mass_kg'] for r in E['trough_parts'] if r['mass_kg'] is not None),1.9642608,9)
 def test_no_electrical_trough_double_count(self):
  total=sum(r['accepted_mass_kg'] for r in E['parts'] if r['accepted_mass_kg'] is not None and not r['asset'].endswith('aligned_trough_and_glands_E04'))
  self.assertAlmostEqual(total,PARTS['electrical_original']['unit_mass_kg'],9)
 def test_operating_model(self):
  self.assertEqual(M['electrical_context']['nominal_bank_kwh'],2*51.2*100/1000)
  self.assertEqual(M['electrical_context']['development_current_cap_A'],180);self.assertFalse(M['electrical_context']['cap_enforced']);self.assertFalse(M['electrical_context']['DC_bus_current_basis_verified']);self.assertIsNone(M['electrical_context']['system_current_rating_A'])
  old={x['id']:x for x in inp('historical_C03_model.json')['operating_cost']['scenarios']}
  for s in M['operating_cost']['scenarios']:
   i=s['inputs'];o=s['outputs'];prev=old[s['id']]['inputs']
   for key,value in prev.items():
    if key!='module_replacement_public_reference_usd':self.assertEqual(i[key],value)
   self.assertEqual(i['module_replacement_public_reference_usd'],4482)
   energy=i['assumed_mean_battery_kw']/i['assumed_charging_efficiency']*i['assumed_tariff_usd_per_kwh']
   cycle=4482*i['assumed_mean_battery_kw']/(10.24*i['assumed_cycle_depth']*i['assumed_cycle_life']);calendar=4482/(i['assumed_calendar_life_years']*i['assumed_annual_operating_hours'])
   self.assertAlmostEqual(o['battery_module_reserve_usd_per_operating_hour'],max(cycle,calendar),10);self.assertAlmostEqual(o['modeled_partial_usd_per_operating_hour'],energy+60+max(cycle,calendar),10)
 def test_thermal_regen_gates(self):
  t=inp('electrical_temperature_limits.json');self.assertFalse(t['implemented_vehicle_enforcement']);self.assertFalse(t['motion_enable']);self.assertFalse(M['electrical_context']['regen_permission_path']['complete'])
  self.assertFalse(M['electrical_context']['load_permission_path']['fast_vehicle_stop_implemented'])
 def test_csv_matches(self):
  with (HERE/'BOM.csv').open(newline='') as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),len(PARTS))
  for r in rows:
   p=PARTS[r['id']]
   for k in ['quantity','unit_mass_kg','unit_price','extended_price']:
    self.assertEqual(r[k],'null' if p[k] is None else str(p[k]))
 def test_reproducible(self):
  files=['cost_model.json','sources.json','BOM.csv','body_composition.json','mass_reconciliation.json','electrical_mass_selection.json'];before={p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in files}
  subprocess.run([sys.executable,str(HERE/'build_cost_model.py')],check=True,capture_output=True)
  self.assertEqual(before,{p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in files})
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Costs))
 report={'revision':'C04_R01','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'all_pass':result.wasSuccessful(),'scope':'Arithmetic, frozen-source consistency, name-replacement, unknown preservation, no-proxy/double counting and reproducibility. No hardware, supplier quote or operational qualification.'}
 (HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 sys.exit(0 if result.wasSuccessful() else 1)
