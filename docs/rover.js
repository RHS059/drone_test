import * as T from 'three/webgpu';

// All imported geometry is metres, Z-up. Right corners use a proper rotation,
// never a reflected or resized copy. This release keeps suspension travel locked.
export async function loadRover(root, asset) {
  const get = async p => { const r = await fetch(p); if (!r.ok) throw Error(`Missing assembly contract: ${p}`); return r.json(); };
  const [corner, bodyContract] = await Promise.all([
    get('./assets/corners/interface_contract_C02_R05.json'),
    get('./assets/body-power/interface_contract.json')
  ]);
  const body = await asset('./assets/body-power/body_power_R01.glb', 'Original faceted body and service hardware · source-backed design');
  root.add(body);
  const reservations = await asset('./assets/body-power/cots_reservations_R01.glb', 'Battery/controller dimensional reservation · manufacturer shape and wiring not modeled');
  reservations.visible = false; root.add(reservations);
  const corners = [], wheelSpinners = [];
  for (const station of corner.wheel_stations_m) {
    const group = new T.Group(); group.name = station.id;
    group.position.x = station.x; group.rotation.z = station.side < 0 ? Math.PI : 0;
    root.add(group); corners.push(group);
    for (const spec of corner.meshes) {
      // Bearing fit shells are evidence envelopes, not authentic bearing internals.
      if (spec.file.includes('bearing_envelopes')) continue;
      const part = await asset('./assets/corners/' + spec.file, 'Original ' + spec.file.replace(/_C02_.*$/, '').replaceAll('_', ' ') + ' · strength and joints unqualified');
      if (spec.initial_rotation_x_rad) part.rotation.x = spec.initial_rotation_x_rad;
      if (spec.initial_translation_m) part.position.set(...spec.initial_translation_m);
      group.add(part);
    }
    const spin = new T.Group(); spin.position.set(...corner.left_at_station_zero.wheel_center); group.add(spin);
    spin.add(await asset('./assets/wheels/wheel_C01.glb', 'BFGoodrich KM3 / EVO Corse dimensional model · original tire profile, tread and rim details; see source assumptions'));
    wheelSpinners.push(spin);
  }
  const removableNames = new Set(bodyContract.service_access.flatMap(s => [...s.cover_nodes, ...(s.associated_gasket_nodes || []), ...(s.associated_removable_fastener_nodes || [])]));
  const removable = []; body.traverse(o => { if (removableNames.has(o.name)) removable.push(o); });
  if (removable.length < 8) throw Error('Service cover names do not match delivered CAD');
  let serviceOpen = false;
  return {
    corner, bodyContract, corners,
    showBody(v) { body.visible = v; },
    showCorners(v) { corners.forEach(c => c.visible = v); },
    openService(v) { serviceOpen = v; removable.forEach(o => o.visible = !v); reservations.visible = v; },
    snapshot() { return { assemblyRevision: corner.configuration, wheelCentersC: corner.wheel_stations_m.map(s => s.wheel_center), wheelDiameter: corner.wheel_interface.diameter_source_m, groundLift: root.position.z, cornerCount: corners.length, serviceOpen, removableNodes: removable.length, steering: 'locked', suspensionTravel: 'locked pending clearance' }; }
  };
}
