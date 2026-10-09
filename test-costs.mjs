import fs from 'node:fs';
import assert from 'node:assert/strict';
import {operatingScenario} from './docs/cost-math.js';
const m=JSON.parse(fs.readFileSync('docs/assets/cost-model/cost_model.json'));
assert.equal(m.build_summary.complete_build_cost,null);assert.equal(m.operating_cost.actual_cost_per_operating_hour,null);assert.equal(m.operating_cost.whole_rover_runtime_hours,null);
for(const basket of m.build_summary.public_price_baskets){let sum=0;for(const id of basket.line_ids){const p=m.parts.find(p=>p.id===id);assert(p&&p.currency===basket.currency&&Number.isFinite(p.unit_price));assert(Math.abs(p.quantity*p.unit_price-p.extended_price)<1e-8);sum+=p.extended_price}assert(Math.abs(sum-basket.reference_subtotal)<1e-8)}
for(const id of m.build_summary.essential_unpriced_line_ids){const p=m.parts.find(p=>p.id===id);assert(p&&p.unit_price===null&&p.extended_price===null)}
let example;
for(const scenario of m.operating_cost.scenarios){const i=scenario.inputs;const x={power:i.assumed_mean_battery_kw,tariff:i.assumed_tariff_usd_per_kwh,efficiency:i.assumed_charging_efficiency,supervision:i.assumed_supervision_hours_per_robot_hour,supervisorRate:i.assumed_supervisor_usd_per_hour,maintenance:i.assumed_maintenance_labor_hours_per_robot_hour,technicianRate:i.assumed_technician_usd_per_hour,annualHours:i.assumed_annual_operating_hours,cycles:i.assumed_cycle_life,depth:i.assumed_cycle_depth,calendarYears:i.assumed_calendar_life_years,replacementCost:i.module_replacement_public_reference_usd};const y=operatingScenario(x,m.electrical_context.nominal_bank_kwh);assert(Math.abs(y.partial-scenario.outputs.modeled_partial_usd_per_operating_hour)<1e-9);assert(Math.abs(y.energy-scenario.outputs.energy_only_usd_per_operating_hour)<1e-9);assert.equal(y.complete,null);example=x;}
assert.equal(operatingScenario({...example,replacementCost:null},6.144).partial,null);
assert.throws(()=>operatingScenario({...example,efficiency:0},6.144),RangeError);
assert.throws(()=>operatingScenario({...example,power:NaN},6.144),RangeError);
assert.throws(()=>operatingScenario({...example,tariff:-1},6.144),RangeError);
assert.throws(()=>operatingScenario({...example,depth:2},6.144),RangeError);
console.log('PASS: exact-currency source baskets, null unknowns, three declared scenario fixtures and invalid-input gates. No actual operating-cost or full-build claim.');
