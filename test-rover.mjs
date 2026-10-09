import fs from 'node:fs';
import assert from 'node:assert/strict';
const read=p=>JSON.parse(fs.readFileSync(p));
const glb=p=>{const b=fs.readFileSync(p);assert.equal(b.toString('ascii',0,4),'glTF');assert.equal(b.readUInt32LE(4),2);assert.equal(b.readUInt32LE(8),b.length);return JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());};
const root='docs/assets/';
const body=glb(root+'body-power/body_power_R01.glb');
const service=read(root+'body-power/interface_contract.json').service_access;
const names=new Set(body.nodes.map(n=>n.name));
let serviceCount=0;
for(const s of service)for(const n of [...s.cover_nodes,...(s.associated_gasket_nodes||[]),...(s.associated_removable_fastener_nodes||[])]){assert(names.has(n),`Missing service node ${n}`);serviceCount++;}
assert.equal(service.length,8);assert.equal(names.size,175);
const wheel=glb(root+'wheels/wheel_C01.glb');assert.deepEqual(wheel.nodes.map(n=>n.name).sort(),['rim','tire']);
assert(wheel.nodes.every(n=>!n.scale&&!n.rotation&&!n.matrix),'Wheel source transforms must remain identity');
const source=fs.readFileSync('docs/rover.js','utf8');
const match=source.match(/assets\/corners\/(interface_contract_[^']+\.json)/);assert(match);
const c=read(root+'corners/'+match[1]);assert.equal(c.wheel_stations_m.length,6);
for(const station of c.wheel_stations_m){assert([-1,1].includes(station.side));assert(Math.abs(station.wheel_center[1]-station.side*.94)<1e-10);assert(Math.abs(station.wheel_center[2]+.25)<1e-10);assert(Math.abs(.68815+station.wheel_center[2]-.8763/2)<1e-10);}
for(const m of c.meshes){const model=glb(root+'corners/'+m.file);assert(model.meshes.length>0);}
assert(source.includes('Math.PI : 0'),'Right corners must use proper rotation');
assert(!source.includes('scale.set'),'No wheel or corner rescaling');
console.log(`PASS: six nominal wheel centers and unloaded ground contacts, ${serviceCount} service nodes, 175 body solids, source GLB contracts. No dynamic, structural or collision qualification.`);

const fixture=read(root+'service-fixtures/service_interface_contract_S01.json');
assert.equal(fixture.safe_working_load_kg,null);assert.equal(fixture.static_pose_only,true);
assert(Math.abs(-fixture.illustrative_floor_Z_C_m-.78815)<1e-10);
assert(Math.abs(.78815-.25-.8763/2-.1)<1e-10);
let fixtureMeshes=0;for(const spec of fixture.assets)fixtureMeshes+=glb(root+'service-fixtures/'+spec.file).meshes.length;
assert.equal(fixtureMeshes,116);assert.equal(fixture.chassis_bearing_points_C_m.length,4);
console.log('PASS:116 original fixture meshes and declared static floor/support datum. No load rating or lifting sequence qualification.');
