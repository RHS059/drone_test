export function bindConnectionGraph(graph,rig,frame){
 const resolve=s=>{
  if(s.module==='actuator')return rig.assembly.getObjectByName(s.instance+'_actuator_'+s.node+'_interface');
  if(s.module==='structure')return rig.structure.assembly.getObjectByName(s.node);
  if(s.module==='joints')return rig.joints.assembly.getObjectByName(s.node);
  if(s.module==='frame')return frame.getObjectByName(s.node);
  if(s.module==='drive')return rig.drive.assembly.getObjectByName(s.instance+'_'+s.node);
  if(s.module==='wheel')return rig.wheels.instances.find(i=>i.id===s.instance)?.local.getObjectByName(s.node);
  if(s.module==='shock')return s.node==='catalog_spring_profile'?rig.shocks.instances.find(i=>i.id===s.instance)?.spring:rig.shocks.assembly.getObjectByName(s.instance+'_'+s.node);
  throw Error('Unknown connection graph module: '+s.module);
 };
 const nodes=new Map();
 for(const[address,spec]of Object.entries(graph.nodes)){const node=resolve(spec);if(!node)throw Error('Connection graph missing actual CAD node: '+address);nodes.set(address,node);}
 const edgeIds=new Set();for(const e of graph.edges){if(!e.id||edgeIds.has(e.id))throw Error('Duplicate connection edge');edgeIds.add(e.id);for(const n of[...(e.from_nodes||[]),...(e.to_nodes||[]),...(e.retaining_nodes||[])])if(!nodes.has(n))throw Error('Unbound connection edge node: '+n);if(!e.kind||!Array.isArray(e.evidence)||!Array.isArray(e.open_gates))throw Error('Incomplete connection evidence');}
 // Metadata is attached only after the entire graph is resolved. These edges
 // are inspectable engineering claims, not proof that open supplier gates pass.
 for(const[address,node]of nodes){node.userData.connectionAddresses=[...(node.userData.connectionAddresses||[]),address];}
 return{nodes,edges:graph.edges,unresolvedEdges:graph.edges.filter(e=>e.open_gates.length>0),fabricationReleased:false};
}
