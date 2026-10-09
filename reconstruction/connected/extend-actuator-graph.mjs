// Adds inspected external eye/pin interfaces. Commercial internal actuation is
// an explicit functional boundary, not an invented internal CAD connection.
export function extendActuatorGraph(base){
 const graph=structuredClone(base);
 for(const end of['front','rear']){
  const add=(module,node,instance=null)=>{const id=[module,...(instance?[instance]:[]),node].join('/');graph.nodes[id]={module,node,instance};return id;};
  const fixed=add('actuator','fixed',end),moving=add('actuator','moving',end);
  for(const [location,eye,parent]of[['rear',fixed,`${end}_rack_crossbeam_C03_R11`],['front',moving,`${end}_rack_carriage_C03_R11`]]){
   const pin=add('structure',`${end}_actuator_${location}_pin_C03_R11`),washer=add('joints',`${end}_actuator_${location}_external_washer`),cotter=add('joints',`${end}_actuator_${location}_cotter`),fork=add('structure',parent);
   graph.edges.push({id:`${end}_actuator_${location}_retained_eye`,kind:'source_dimensioned_eye_and_retained_crosspin',from_nodes:[eye],to_nodes:[fork],retaining_nodes:[pin,washer,cotter],evidence:['external: steering-actuator/nominal_integration_check.json','external: audit/actuator_brep_audit.json','joints/pin_retention_checks_C04_R01.json'],open_gates:['Configured actuator source profile, pin fits, retention strength and installed cotter bend','Actuator force/speed/duty and control safety qualification'],nominal_pin_diameter_mm:12,source_eye_bore_mm:12.2});
  }
  graph.edges.push({id:`${end}_commercial_actuator_internal_function`,kind:'purchased_telescoping_actuator_function',from_nodes:[fixed],to_nodes:[moving],retaining_nodes:[],evidence:['external: steering-actuator/actuator_interface_contract_R02.json'],open_gates:['HD48 B068200mm M/M remains development candidate','Internal motor/gearing/screw not modeled; purchased assembly function','Load, duty, failure response and controls not qualified']});
 }
 graph.scope+=' Actuator external eye retention and explicit purchased internal-function boundaries included.';
 return graph;
}
