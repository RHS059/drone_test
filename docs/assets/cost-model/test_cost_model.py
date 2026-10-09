#!/usr/bin/env python3
"""Read-only consistency and anti-double-counting checks for the cost package."""
from pathlib import Path
from decimal import Decimal
import csv,json,math,unittest
HERE=Path(__file__).resolve().parent
M=json.loads((HERE/'cost_model.json').read_text())
S={x['id']:x for x in json.loads((HERE/'sources.json').read_text())['observations']}
P={x['id']:x for x in M['parts']}

class CostModelChecks(unittest.TestCase):
    def test_unknown_build_total(self):
        self.assertIsNone(M['build_summary']['complete_build_cost'])
        self.assertGreater(len(M['build_summary']['essential_unpriced_line_ids']),0)
        for k in ['drives','arms','arm_controllers','frame_R07','body_R01']:
            self.assertIsNone(P[k]['unit_price'])
            self.assertIsNone(P[k]['extended_price'])
    def test_null_is_not_zero(self):
        for p in M['parts']:
            self.assertNotEqual(p['unit_price'],0)
            self.assertNotEqual(p['unit_mass_kg'],0)
            self.assertNotEqual(p['quantity'],0)
    def test_exact_quantities(self):
        for id,n in [('tires',6),('rims',6),('drives',6),('batteries',4),('arms',2),('arm_controllers',2),('grippers',2),('couplings',2),('wheel_nuts',30)]:
            self.assertEqual(P[id]['quantity'],n)
    def test_native_currency_baskets(self):
        bs=M['build_summary']['public_price_baskets']
        self.assertEqual({x['currency'] for x in bs},{'USD','EUR'})
        for b in bs:
            total=Decimal(0)
            for id in b['line_ids']:
                p=P[id]
                self.assertEqual(p['currency'],b['currency'])
                self.assertIsNotNone(p['unit_price'])
                total+=Decimal(str(p['unit_price']))*Decimal(str(p['quantity']))
            self.assertEqual(total,Decimal(str(b['reference_subtotal'])))
            self.assertFalse(b['complete_build_total'])
        self.assertEqual({x['currency']:x['reference_subtotal'] for x in bs},{'USD':20019.9,'EUR':2891.34})
    def test_sources_and_prices_match(self):
        for p in M['parts']:
            for id in p['source_ids']:
                self.assertIn(id,S)
            if p['unit_price'] is not None:
                s=S[p['price_source_id']]
                self.assertEqual(p['unit_price'],s['price'])
                self.assertEqual(p['currency'],s['currency'])
                self.assertTrue(s['exact_sku_match'])
                self.assertEqual(s['retrieved_on'],M['as_of'])
    def test_no_bundle_or_alternative_double_count(self):
        self.assertEqual(P['wheel_nuts']['included_in_cost_of'],'rims')
        self.assertIsNone(P['wheel_nuts']['unit_price'])
        self.assertEqual(P['couplings']['sku'],'GRP-CPL-062')
        for a in M['alternatives']:
            self.assertFalse(a['baseline_included'])
            self.assertNotIn(a['id'],P)
        self.assertFalse(S['drive_rejected_price']['exact_sku_match'])
    def test_mass_pinning(self):
        self.assertEqual(M['configuration']['corner_revision'],'C02_R06')
        known=sum(p['unit_mass_kg']*p['quantity'] for p in M['parts'] if p['included_in_pinned_mass_subtotal'])
        self.assertAlmostEqual(known,976.3493556219631,places=8)
        self.assertAlmostEqual(known,M['mass_context']['pinned_known_subset_kg'],places=8)
        self.assertIsNone(M['mass_context']['whole_vehicle_mass_kg'])
        self.assertFalse(P['wheel_nuts']['included_in_pinned_mass_subtotal'])
    def test_recall_is_serial_specific(self):
        s=S['battery_recall']
        self.assertEqual(s['affected_model'],'48V030-GC2')
        self.assertEqual(len(s['affected_serial_ranges']),3)
        self.assertEqual(M['procurement_gates'][0]['status'],'unresolved_no_serials')
    def test_measured_operating_inputs_remain_unknown(self):
        o=M['operating_cost']
        self.assertIsNone(o['actual_cost_per_operating_hour'])
        self.assertIsNone(o['whole_rover_runtime_hours'])
        for k in ['measured_grid_kwh_per_operating_hour','measured_battery_kwh_per_operating_hour','site_tariff_per_kwh','validated_cycle_life','complete_build_cost']:
            self.assertIsNone(o['actual_inputs'][k])
    def test_scenarios_arithmetic(self):
        for s in M['operating_cost']['scenarios']:
            i,o=s['inputs'],s['outputs']
            energy=i['assumed_mean_battery_kw']/i['assumed_charging_efficiency']*i['assumed_tariff_usd_per_kwh']
            labor=i['assumed_supervision_hours_per_robot_hour']*i['assumed_supervisor_usd_per_hour']+i['assumed_maintenance_labor_hours_per_robot_hour']*i['assumed_technician_usd_per_hour']
            cycle=i['module_replacement_public_reference_usd']*i['assumed_mean_battery_kw']/(6.144*i['assumed_cycle_depth']*i['assumed_cycle_life'])
            calendar=i['module_replacement_public_reference_usd']/(i['assumed_calendar_life_years']*i['assumed_annual_operating_hours'])
            partial=energy+labor+max(cycle,calendar)
            self.assertAlmostEqual(energy,o['energy_only_usd_per_operating_hour'])
            self.assertAlmostEqual(partial,o['modeled_partial_usd_per_operating_hour'])
            self.assertAlmostEqual(partial*i['assumed_annual_operating_hours'],o['modeled_partial_usd_per_assumed_year'])
            self.assertIsNone(o['complete_operating_cost_usd_per_hour'])
            self.assertIsNone(o['fully_burdened_cost_usd_per_hour'])
            self.assertIsNone(o['whole_rover_runtime_hours'])
    def test_csv_matches_json(self):
        with (HERE/'BOM.csv').open(newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),len(M['parts']))
        self.assertEqual({r['id'] for r in rows},set(P))
        for r in rows:
            p=P[r['id']]
            for k,v in r.items():
                actual=p[k]
                expected='null' if actual is None else '|'.join(actual) if isinstance(actual,list) else str(actual).lower() if isinstance(actual,bool) else str(actual)
                self.assertEqual(v,expected,(r['id'],k))
    def test_no_legacy_configuration_in_current_scenarios(self):
        self.assertEqual(M['electrical_context']['battery_count'],4)
        self.assertEqual(M['electrical_context']['nominal_bank_kwh'],6.144)
        self.assertFalse(M['electrical_context']['DC_bus_current_basis_verified'])
        self.assertIsNone(M['electrical_context']['system_current_rating_A'])

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CostModelChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (HERE/'validation.json').write_text(json.dumps(dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),configuration=M['configuration'],scope='Cost arithmetic,CSV/JSON agreement,quantity/source/null/bundle/revision safeguards;not supplier or engineering qualification.'),indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
