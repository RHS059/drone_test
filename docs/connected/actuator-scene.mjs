// Connected external interface models, never manufacturer-internal geometry.
export async function loadActuatorInterfaces(root,asset,contract,{retentionOwner='actuator'}={}){
 if(!['actuator','joints'].includes(retentionOwner))throw Error('Unknown actuator retention owner');
 const ends=new Map();
 for(const mount of contract.mounts){
  const fixed=await asset('./assets/actuators/actuator_fixed_interface.glb','Steering actuator: sourced mounting eyes, simplified maximum housing; load/duty unqualified');
  const moving=await asset('./assets/actuators/actuator_moving_interface.glb','Steering actuator rod and mounting eye: source dimensions with documented profile assumptions');
  fixed.name=mount.id+'_actuator_fixed_interface';moving.name=mount.id+'_actuator_moving_interface';
  fixed.position.set(...mount.fixed_pin_C_m);moving.position.set(...mount.moving_pin_neutral_C_m);
  if(contract.retention && retentionOwner==='actuator'){
   for(const [parent,file,label] of [[fixed,contract.retention.fixed_file,'fixed'],[moving,contract.retention.moving_file,'moving']]){
    const retained=await asset('./assets/actuators/'+file,'Actuator pin external take-up washer and split pin: original functional retention model, strength unqualified');
    retained.name=mount.id+'_actuator_'+label+'_retention';
    // Original rear-axle pin heads face the opposite X direction. This proper
    // rotation preserves the handed retention stack without reflecting geometry.
    if(mount.id==='rear')retained.rotation.z=Math.PI;
    parent.add(retained);
   }
  }
  root.add(fixed,moving);
  ends.set(mount.id,{fixed,moving,mount,rack:0});
 }
 function setRack(end,value){if(!ends.has(end)||!Number.isFinite(value)||Math.abs(value)>.075)throw Error('Actuator rack must remain within ±75 mm');const e=ends.get(end);e.rack=value;e.moving.position.y=e.mount.moving_pin_neutral_C_m[1]+value;}
 return{setRack,show(v){for(const e of ends.values()){e.fixed.visible=v;e.moving.visible=v;}},snapshot(){return{candidate:contract.candidate,retention_owner:retentionOwner,physical_operation_qualified:false,ends:[...ends.entries()].map(([id,e])=>({id,rack_m:e.rack,pin_span_m:e.moving.position.distanceTo(e.fixed.position),extension_m:e.moving.position.distanceTo(e.fixed.position)-.390}))}}};
}
