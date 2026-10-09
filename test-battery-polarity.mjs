#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { applyBatteryPolarity, validateBatteryPolarityContract } from './docs/connected/apply-battery-polarity.mjs';

// Use existing viewer dependencies read-only. Do not vendor them into this patch.
const dependencyURL = (env, fallback) => env ? pathToFileURL(env).href : new URL(fallback, import.meta.url).href;
const T = await import(dependencyURL(process.env.THREE_MODULE, './docs/vendor/three.core.js'));
const { readCad } = await import(dependencyURL(process.env.CAD_READER_MODULE, './test-support/read-original-glb.mjs'));
const glbPath = process.env.BA02_GLB || new URL('./docs/assets/connected-body/battery.glb.gz', import.meta.url);
const contract = JSON.parse(fs.readFileSync(new URL('./docs/assets/battery-polarity/battery-polarity-contract.json', import.meta.url)));
const checks = [];
const test = (name, fn) => { fn(); checks.push(name); };
const digest = array => crypto.createHash('sha256').update(Buffer.from(array.buffer, array.byteOffset, array.byteLength)).digest('hex');
function geometrySnapshot(body) {
  const result = [];
  body.traverse(n => {
    const geometry = n.geometry;
    result.push({
      object: n, name: n.name, parent: n.parent, children: [...n.children],
      position: n.position.toArray(), quaternion: n.quaternion.toArray(), scale: n.scale.toArray(),
      matrix: [...n.matrix.elements], matrixWorld: [...n.matrixWorld.elements],
      matrixAutoUpdate: n.matrixAutoUpdate, matrixWorldNeedsUpdate: n.matrixWorldNeedsUpdate,
      visible: n.visible, geometry,
      attributes: geometry ? Object.fromEntries(Object.entries(geometry.attributes).map(([k,a]) => [k, digest(a.array)])) : null,
      index: geometry?.index ? digest(geometry.index.array) : null
    });
  });
  return result;
}
function stateSnapshot(body) {
  const state = [];
  body.traverse(n => state.push({
    object: n, userDataReference: n.userData, userDataText: JSON.stringify(n.userData),
    material: n.material,
    colors: n.isMesh ? (Array.isArray(n.material) ? n.material : [n.material]).map(m => m?.color?.getHex()) : null
  }));
  return { geometry: geometrySnapshot(body), state };
}
function fixture({ multiMaterial = false } = {}) {
  const body = readCad(glbPath);
  // A shared original metal also used on unrelated fittings, proving isolation.
  const metal = new T.MeshStandardMaterial({ color: '#a67a33', roughness: 0.34, metalness: 0.91 });
  body.traverse(n => {
    n.userData = { existingMetadata: true, label: 'Original asset label' };
    if (n.isMesh) n.material = metal;
  });
  if (multiMaterial) body.getObjectByName(contract.terminals[3].source_node_name).children[0].material = [metal, metal];
  body.updateMatrixWorld(true);
  return { body, metal };
}

test('Source-mark and asymmetric-fitting contract validation', () => {
  assert.deepEqual(validateBatteryPolarityContract(contract), { drawingFittingOffset: 52.5, rightToY: -1 });
});
test('Real BA02 GLB terminal/fitting positions agree with source-derived polarity', () => {
  const { body } = fixture();
  for (const terminal of contract.terminals) {
    const bounds = new T.Box3().setFromObject(body.getObjectByName(terminal.source_node_name));
    const expected = terminal.axis_top_C_mm.map(n => n / 1000);
    const actual = [(bounds.min.x + bounds.max.x) / 2, (bounds.min.y + bounds.max.y) / 2, bounds.max.z];
    actual.forEach((n,i) => assert(Math.abs(n - expected[i]) < 1e-5));
  }
  for (const name of contract.fitting_source_nodes) {
    const bounds = new T.Box3().setFromObject(body.getObjectByName(name));
    assert(Math.abs((bounds.min.y + bounds.max.y) * 500 - (-52.5)) < 1e-3);
  }
});
test('Four corrected labels/colors preserve all names, geometry and matrices', () => {
  const { body, metal } = fixture({ multiMaterial: true });
  const before = geometrySnapshot(body);
  const originalColor = metal.color.getHex();
  const result = applyBatteryPolarity(body, contract);
  assert.equal(result.terminalsCorrected, 4);
  assert.equal(result.meshesCorrected, 4);
  assert.equal(result.fullHarnessComplete, false);
  assert.equal(result.physicalElectricalContinuityVerified, false);
  assert.equal(result.terminalHardwareQualified, false);
  assert.deepEqual(geometrySnapshot(body), before);
  assert.equal(metal.color.getHex(), originalColor);
  const correctedMaterials = new Set();
  for (const terminal of contract.terminals) {
    const node = body.getObjectByName(terminal.source_node_name);
    assert.equal(node.userData.label, terminal.display_label);
    assert.equal(node.userData.batteryPolarity.functionalPolarity, terminal.functional_polarity);
    assert.equal(node.name, terminal.source_node_name);
    node.traverse(n => {
      assert.equal(n.userData.existingMetadata, true);
      assert.equal(n.userData.label, terminal.display_label);
      assert.equal(n.userData.displayLabel, terminal.display_label);
      assert.deepEqual(n.userData.batteryPolarity.sourceAliases, [terminal.source_node_name]);
      if (!n.isMesh) return;
      for (const m of Array.isArray(n.material) ? n.material : [n.material]) {
        assert.notEqual(m, metal);
        assert(!correctedMaterials.has(m));
        correctedMaterials.add(m);
        assert.equal(m.color.getHexString(), terminal.color.slice(1));
        assert.equal(m.roughness, metal.roughness);
        assert.equal(m.metalness, metal.metalness);
      }
    });
  }
  for (const name of contract.fitting_source_nodes) {
    const mesh = body.getObjectByName(name).children[0];
    assert.equal(mesh.material, metal);
    assert.equal(mesh.userData.label, 'Original asset label');
  }
  assert.equal(correctedMaterials.size, 5);
});
test('Missing fourth source node fails atomically before all mutation', () => {
  const { body } = fixture();
  body.remove(body.getObjectByName(contract.terminals[3].source_node_name));
  const before = stateSnapshot(body);
  assert.throws(() => applyBatteryPolarity(body, contract), /missing scene node/);
  assert.deepEqual(stateSnapshot(body), before);
});
test('Duplicate source name fails atomically', () => {
  const { body } = fixture();
  body.add(body.getObjectByName(contract.terminals[0].source_node_name).clone(true));
  const before = stateSnapshot(body);
  assert.throws(() => applyBatteryPolarity(body, contract), /duplicate scene node/);
  assert.deepEqual(stateSnapshot(body), before);
});
test('Late material preparation failure leaves entire scene unchanged', () => {
  const { body } = fixture();
  const mesh = body.getObjectByName(contract.terminals[3].source_node_name).children[0];
  const bad = new T.MeshStandardMaterial({color:'#998877'});
  bad.clone = () => { throw Error('Injected late clone failure'); };
  mesh.material = bad;
  const before = stateSnapshot(body);
  assert.throws(() => applyBatteryPolarity(body, contract), /Injected late clone failure/);
  assert.deepEqual(stateSnapshot(body), before);
});
test('Clone with shared color is rejected before source color mutation', () => {
  const { body, metal } = fixture();
  const realClone = metal.clone.bind(metal);
  metal.clone = () => { const c = realClone(); c.color = metal.color; return c; };
  const before = stateSnapshot(body);
  assert.throws(() => applyBatteryPolarity(body, contract), /isolate its color/);
  assert.deepEqual(stateSnapshot(body), before);
});
for (const [name, change] of [
  ['Reversed drawing marks rejected', c => { c.source.drawing_terminal_marks = {left:'negative',right:'positive'}; }],
  ['Opposite installed fitting sign rejected', c => { c.datum.installed_fitting_C_y_mm = 52.5; }],
  ['Legacy incorrect terminal polarity rejected', c => { c.terminals[0].functional_polarity = 'negative'; }],
  ['Incorrect terminal location rejected', c => { c.terminals[0].axis_top_C_mm[1] *= -1; }],
  ['Unverified drawing hash rejected', c => { c.source.sha256 = '0'.repeat(64); }],
  ['Unjustified harness-complete gate rejected', c => { c.gates.full_harness_complete = true; }]
]) {
  test(name, () => {
    const c = structuredClone(contract); change(c);
    const { body } = fixture();
    const before = stateSnapshot(body);
    assert.throws(() => applyBatteryPolarity(body, c), /Battery polarity:/);
    assert.deepEqual(stateSnapshot(body), before);
  });
}
test('Repeated application keeps functional metadata and geometry stable', () => {
  const { body } = fixture();
  const before = geometrySnapshot(body);
  applyBatteryPolarity(body, contract);
  const labels = contract.terminals.map(t => JSON.stringify(body.getObjectByName(t.source_node_name).userData));
  applyBatteryPolarity(body, contract);
  assert.deepEqual(contract.terminals.map(t => JSON.stringify(body.getObjectByName(t.source_node_name).userData)), labels);
  assert.deepEqual(geometrySnapshot(body), before);
});
console.log(JSON.stringify({ pass: true, revision: contract.revision, tests: checks.length, checks,
  realFrozenBA02GlbUsed: true, geometryAndMatricesUnchanged: true, missingNodeFailureAtomic: true,
  sharedMaterialsUnchanged: true, fullHarnessComplete: false, terminalHardwareQualified: false }, null, 2));
