/** Original BA02 polarity semantics patch. No geometry or transform changes. */
const REVISION = 'BA02_POLARITY_R01';
const SOURCE_SHA256 = 'd153636d0bb1cb84ea4c3c339746618c97fd02859398404febbc8a92a2a27d4b';
const COLORS = { positive: '#e53935', negative: '#20252b' };
const near = (a, b) => Number.isFinite(a) && Math.abs(a - b) < 1e-7;
const requireValue = (condition, message) => { if (!condition) throw Error(`Battery polarity: ${message}`); };

/** Validate source-mark/fitting-sign derivation independently of cable connectivity. */
export function validateBatteryPolarityContract(contract) {
  requireValue(contract?.revision === REVISION, 'unsupported correction revision');
  const source = contract.source;
  const datum = contract.datum;
  requireValue(source?.sha256 === SOURCE_SHA256, 'unexpected source drawing hash');
  requireValue(source.drawing_terminal_marks?.left === 'positive' &&
    source.drawing_terminal_marks?.right === 'negative', 'drawing polarity marks changed');
  requireValue(near(source.drawing_width_mm, 647.6) && near(source.fitting_from_drawing_left_mm, 376.3) &&
    near(source.terminal_pitch_mm, 550.5) && near(source.depth_mm, 161.5) &&
    near(source.terminal_from_depth_edge_mm, 26.7), 'drawing dimensions changed');
  const drawingFittingOffset = source.fitting_from_drawing_left_mm - source.drawing_width_mm / 2;
  requireValue(near(drawingFittingOffset, 52.5) && near(datum?.installed_fitting_C_y_mm, -52.5),
    'asymmetric fitting no longer establishes frozen orientation');
  const rightToY = datum.installed_fitting_C_y_mm / drawingFittingOffset;
  requireValue(near(rightToY, -1) && datum.drawing_right_to_C_y_sign === -1,
    'drawing-right must map to CAD -Y');
  requireValue(Array.isArray(contract.terminals) && contract.terminals.length === 4,
    'exactly four terminal mappings are required');
  const bySource = new Map();
  for (const terminal of contract.terminals) {
    requireValue(!bySource.has(terminal.source_node_name), 'duplicate source terminal alias');
    bySource.set(terminal.source_node_name, terminal);
  }
  for (let pack = 1; pack <= 2; pack++) {
    for (const [legacy, functional, side] of [
      ['negative', 'positive', 'left'], ['positive', 'negative', 'right']
    ]) {
      const name = `BA02_pack_${pack}_${legacy}_M8_interface`;
      const terminal = bySource.get(name);
      requireValue(terminal?.pack === pack && terminal.legacy_name_polarity === legacy &&
        terminal.functional_polarity === functional && terminal.drawing_side === side,
        `incorrect functional mapping for ${name}`);
      const expectedY = (side === 'left' ? -1 : 1) * rightToY * source.terminal_pitch_mm / 2;
      const expectedX = [-975, -625][pack - 1] - (source.depth_mm / 2 - source.terminal_from_depth_edge_mm);
      requireValue(terminal.axis_top_C_mm?.length === 3 && near(terminal.axis_top_C_mm[0], expectedX) &&
        near(terminal.axis_top_C_mm[1], expectedY) && near(terminal.axis_top_C_mm[2], 169.6),
        `incorrect terminal coordinates for ${name}`);
      requireValue(terminal.symbol === (functional === 'positive' ? '+' : '-') &&
        terminal.color === COLORS[functional] &&
        terminal.functional_name === `BA02_pack_${pack}_${functional}_M8_interface_VERIFIED_R01` &&
        terminal.display_label === `Battery ${pack} ${functional} (${terminal.symbol}) terminal interface; source-verified polarity, hardware/lug unqualified`,
        `incorrect display semantics for ${name}`);
    }
  }
  requireValue(contract.gates?.terminal_hardware_qualified === false &&
    contract.gates?.full_harness_complete === false &&
    contract.gates?.physical_electrical_continuity_verified === false,
    'polarity correction must not close hardware or wiring qualification');
  return { drawingFittingOffset, rightToY };
}

/**
 * Call after BA02 named body patches and ordinary asset labels are assigned.
 * Keep node.name unchanged as the frozen source trace alias. All four aliases
 * must resolve uniquely and every clone must be staged before scene mutation.
 * No three.js import is required; uses Object3D.traverse and Material.clone.
 */
export function applyBatteryPolarity(body, contract) {
  validateBatteryPolarityContract(contract);
  requireValue(typeof body?.traverse === 'function', 'body must support Object3D.traverse');
  const wanted = new Set(contract.terminals.map(t => t.source_node_name));
  const resolved = new Map();
  body.traverse(node => {
    if (!wanted.has(node.name)) return;
    requireValue(!resolved.has(node.name), `duplicate scene node ${node.name}`);
    resolved.set(node.name, node);
  });
  for (const name of wanted) requireValue(resolved.has(name), `missing scene node ${name}`);

  // Resolve every mesh before cloning or assigning any scene field.
  const seenMeshes = new Set();
  const targets = contract.terminals.map(terminal => {
    const node = resolved.get(terminal.source_node_name);
    const meshes = [];
    node.traverse(mesh => {
      if (!mesh.isMesh) return;
      requireValue(!seenMeshes.has(mesh), `overlapping terminal mesh ${terminal.source_node_name}`);
      seenMeshes.add(mesh);
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      requireValue(materials.length > 0 && materials.every(m => m && typeof m.clone === 'function' && m.color),
        `terminal mesh has no cloneable color material: ${terminal.source_node_name}`);
      meshes.push(mesh);
    });
    requireValue(meshes.length > 0, `terminal has no mesh: ${terminal.source_node_name}`);
    return { terminal, node, meshes };
  });
  const staged = [];
  const clones = [];
  try {
    for (const { terminal, node, meshes } of targets) {
      const metadataFor = object => ({
        ...object.userData,
        label: terminal.display_label,
        displayLabel: terminal.display_label,
        batteryPolarity: {
          revision: REVISION,
          sourceNodeName: terminal.source_node_name,
          sourceAliases: [terminal.source_node_name],
          legacyNamePolarity: terminal.legacy_name_polarity,
          functionalName: terminal.functional_name,
          functionalPolarity: terminal.functional_polarity,
          symbol: terminal.symbol,
          sourceVerified: true,
          sourceDrawingSha256: SOURCE_SHA256,
          axisTopCmm: [...terminal.axis_top_C_mm],
          visualizationColor: terminal.color,
          terminalHardwareQualified: false,
          fullHarnessComplete: false
        }
      });
      const meshChanges = meshes.map(mesh => {
        const materialList = (Array.isArray(mesh.material) ? mesh.material : [mesh.material]).map(original => {
          const clone = original.clone();
          requireValue(clone !== original, 'material.clone returned the shared source material');
          clones.push(clone);
          requireValue(clone.color !== original.color && typeof clone.color?.set === 'function',
            'material.clone did not isolate its color');
          clone.color.set(terminal.color);
          return clone;
        });
        return {
          mesh,
          material: Array.isArray(mesh.material) ? materialList : materialList[0],
          userData: metadataFor(mesh)
        };
      });
      staged.push({ node, userData: metadataFor(node), meshChanges });
    }
  } catch (error) {
    for (const clone of clones) clone.dispose?.();
    throw error;
  }
  // Ordinary Object3D fields only. No name, geometry, parent or matrix writes.
  for (const { node, userData, meshChanges } of staged) {
    node.userData = userData;
    for (const change of meshChanges) {
      change.mesh.material = change.material;
      change.mesh.userData = change.userData;
    }
  }
  return {
    revision: REVISION,
    terminalsCorrected: staged.length,
    meshesCorrected: seenMeshes.size,
    sourceVerified: true,
    sourceDrawingSha256: SOURCE_SHA256,
    sourceNamesPreserved: true,
    geometryUnchanged: true,
    transformsUnchanged: true,
    terminalHardwareQualified: false,
    fullHarnessComplete: false,
    physicalElectricalContinuityVerified: false
  };
}
