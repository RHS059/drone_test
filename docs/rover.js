import * as T from 'three/webgpu';
import {loadSteering} from './steering.js?v=steering-01';

// All imported geometry is metres, Z-up. Right corners use a proper rotation,
// never a reflected or resized copy. This release keeps suspension travel locked.
export async function loadRover(root, asset) {
  const get = async p => { const r = await fetch(p); if (!r.ok) throw Error(`Missing assembly contract: ${p}`); return r.json(); };
  const [corner, bodyContract, fixtureContract, driveReservation] = await Promise.all([
    get('./assets/corners/interface_contract_C02_R06.json'),
    get('./assets/body-power/interface_contract.json'),
    get('./assets/service-fixtures/service_interface_contract_S01.json'),
    get('./assets/corners/drive-reservation.json')
  ]);
  const body = await asset('./assets/body-power/body_power_R01.glb', 'Original faceted body and service hardware · source-backed design');
  root.add(body);
  const reservations = await asset('./assets/body-power/cots_reservations_R01.glb', 'Battery/controller dimensional reservation · manufacturer shape and wiring not modeled');
  reservations.visible = false; root.add(reservations);
  const fixtures = new T.Group(); fixtures.visible = false; root.add(fixtures);
  fixtures.add(await asset('./assets/service-fixtures/chassis_trestles_S01.glb', 'Original chassis support trestles · static fit study, no load rating'));
  const cradle = new T.Group(); fixtures.add(cradle);
  cradle.add(await asset('./assets/service-fixtures/corner_cradle_S01.glb', 'Original wheel-module cradle · support and restraint unqualified'));
  let workshop = false, cradleStation = 'left_1';
  const motorReservations = new T.Group(); motorReservations.visible = false; root.add(motorReservations);
  const corners = [], wheelSpinners = [];
  const steering = await loadSteering(root,asset,get);
  for (const station of corner.wheel_stations_m) {
    const group = new T.Group(); group.name = station.id;
    group.position.x = station.x; group.rotation.z = station.side < 0 ? Math.PI : 0;
    root.add(group); corners.push(group);
    const reserved = new T.Group(); reserved.position.x=station.x; reserved.rotation.z=station.side<0?Math.PI:0;
    const box = new T.Mesh(new T.BoxGeometry(...driveReservation.size_m),new T.MeshBasicMaterial({color:0x83c6d0,wireframe:true,transparent:true,opacity:.35}));
    box.position.set(...driveReservation.center_m);box.userData.label='Wheel-drive reserved space · bounding box only, not motor CAD';reserved.add(box);motorReservations.add(reserved);
    for (const spec of (station.x === 0 ? corner.meshes : [])) {
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
    if(station.x!==0){const id=(station.x>0?'front':'rear')+'_'+(station.side>0?'left':'right');root.attach(spin);steering.bindWheel(id,spin);reserved.updateMatrix();steering.bindReservation(id,reserved,reserved.matrix.clone());}
  }
  const removableNames = new Set(bodyContract.service_access.flatMap(s => [...s.cover_nodes, ...(s.associated_gasket_nodes || []), ...(s.associated_removable_fastener_nodes || [])]));
  const removable = []; body.traverse(o => { if (removableNames.has(o.name)) removable.push(o); });
  if (removable.length < 8) throw Error('Service cover names do not match delivered CAD');
  let serviceOpen = false;
  return {
    corner, bodyContract, corners, steering,
    setRack(end,value){if(workshop && value!==0)throw Error('Workshop placement is checked only with centered steering');steering.setRack(end,value);},
    homeSteering(){steering.home();},
    setWorkshop(v) { workshop=v; if(v)steering.home(); fixtures.visible=v; root.position.z=v?-fixtureContract.illustrative_floor_Z_C_m:.68815; },
    setCradle(id) { const station=corner.wheel_stations_m.find(s=>s.id===id);if(!station)throw Error('Unknown cradle station');cradleStation=id;cradle.position.x=station.x;cradle.rotation.z=station.side<0?Math.PI:0; },
    showBody(v) { body.visible = v; },
    showCorners(v) { corners.forEach(c => c.visible = v);wheelSpinners.forEach(w=>w.visible=v);steering.assembly.visible=v; },
    openService(v) { serviceOpen = v; removable.forEach(o => o.visible = !v); reservations.visible = v; motorReservations.visible=v; },
    snapshot() { return { assemblyRevision: steering.contract.configuration, workshop, cradleStation, fixtureLoadRating:null, wheelCentersC: corner.wheel_stations_m.map(s => s.wheel_center), wheelDiameter: corner.wheel_interface.diameter_source_m, groundLift: root.position.z, cornerCount: corners.length, serviceOpen, removableNodes: removable.length, steering: steering.snapshot(), suspensionTravel: 'held at neutral; load and ground-contact response unqualified' }; }
  };
}
