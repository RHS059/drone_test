// Lightweight CI regression pinned to the independently measured STEP report.
// Regenerate the Python B-rep report after geometry changes; do not edit its hash.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const [step,contractPath,reportPath]=process.argv.slice(2);
if(!step||!contractPath||!reportPath)throw Error('Provide STEP, contract and measured report paths');
const c=JSON.parse(fs.readFileSync(contractPath)),r=JSON.parse(fs.readFileSync(reportPath));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(step)).digest('hex'),r.adapter_sha256);
assert.equal(r.actual_counterbore_floors.length,6);
assert(Math.abs(r.actual_ur_face.z_mm-c.ur_face_z_mm)<1e-7);
assert(r.actual_ur_face.area_mm2>1000);
const grips=r.actual_counterbore_floors.map(s=>s.z_mm-r.actual_ur_face.z_mm);
assert(grips.every(g=>Math.abs(g-r.actual_nominal_grip_mm)<1e-8));
assert.equal(c.manufacturer_max_protrusion_mm,7);
const protrusions=grips.map(g=>c.candidate_underhead_length_mm-g);
assert(protrusions.every(p=>p<=c.manufacturer_max_protrusion_mm&&p>=c.proposed_minimum_nominal_protrusion_mm));
assert.equal(r.effective_thread_engagement_verified,false);
assert.equal(r.proposed_minimum_is_manufacturer_requirement,false);
assert.equal(r.fabrication_approved,false);
const nominal=L=>L-r.actual_nominal_grip_mm;
assert.equal(nominal(16),4.5);assert.equal(nominal(18),6.5);
assert(nominal(20)>7);assert(nominal(14)<4);
assert((18+.5)-(r.actual_nominal_grip_mm-.2)>7);
console.log('PASS: exact STEP identity and measured six-seat grip bound nominal screw protrusion; project minimum and unknown effective engagement remain explicit.');
