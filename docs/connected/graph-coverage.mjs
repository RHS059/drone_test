export function modeledMechanicalAddresses(rig,frame){
 const ids=[];for(const b of rig.structure.bindings)ids.push('structure/'+b.node.name);
 for(const b of rig.joints.bindings)ids.push('joints/'+b.node.name);
 for(const i of rig.drive.instances)for(const {local}of Object.values(i.groups))for(const node of local.children)ids.push('drive/'+i.id+'/'+node.name.slice(i.id.length+1));
 for(const i of rig.wheels.instances)for(const node of i.local.children)ids.push('wheel/'+i.id+'/'+node.name);
 for(const i of rig.shocks.instances){for(const g of Object.values(i.groups))for(const n of g.children)ids.push('shock/'+i.id+'/'+n.name.slice(i.id.length+1));ids.push('shock/'+i.id+'/catalog_spring_profile');}
 for(const end of['front','rear'])for(const part of['fixed','moving'])ids.push('actuator/'+end+'/'+part);
 for(const node of frame.children)ids.push('frame/'+node.name);
 if(new Set(ids).size!==ids.length)throw Error('Duplicate active component address');return ids;
}
export function connectionCoverage(addresses,graph){
 const active=new Set(addresses),declared=new Set(Object.keys(graph.nodes)),used=new Set(graph.edges.flatMap(e=>[...(e.from_nodes||[]),...(e.to_nodes||[]),...(e.retaining_nodes||[])]));
 const missingNodes=addresses.filter(a=>!declared.has(a)),missingEdges=addresses.filter(a=>declared.has(a)&&!used.has(a)),inactiveDeclarations=[...declared].filter(a=>!active.has(a));
 return{activeCount:active.size,declaredCount:declared.size,missingNodes,missingEdges,inactiveDeclarations,complete:!missingNodes.length&&!missingEdges.length&&!inactiveDeclarations.length};
}
export function extendFrameContacts(base,report){
 const graph=structuredClone(base);
 for(const p of report.parts){const node=p.name;graph.nodes['frame/'+node]={module:'frame',instance:null,node};}
 report.zero_gap_contacts.forEach(([a,b,d],i)=>graph.edges.push({id:'R07_nominal_weld_contact_'+i,kind:'original_frame_nominal_weld_fit',from_nodes:['frame/'+a],to_nodes:['frame/'+b],retaining_nodes:[],evidence:['external: mechanical/frame_R07_verification.json'],open_gates:['Proposed welded construction; weld size, preparation, procedure, strength, fatigue and inspection remain unqualified'],nominal_gap_mm:d,contact_is_not_weld_qualification:true}));
 return graph;
}
export function rootedConnectionCoverage(graph,rootModule='frame'){
 const adjacent=new Map(Object.keys(graph.nodes).map(n=>[n,new Set()]));
 for(const e of graph.edges){const nodes=[...new Set([...(e.from_nodes||[]),...(e.to_nodes||[]),...(e.retaining_nodes||[])])];for(const n of nodes)if(!adjacent.has(n))throw Error('Undeclared graph endpoint');for(let i=1;i<nodes.length;i++){adjacent.get(nodes[0]).add(nodes[i]);adjacent.get(nodes[i]).add(nodes[0]);}}
 const roots=Object.entries(graph.nodes).filter(([,n])=>n.module===rootModule).map(([n])=>n);if(!roots.length)throw Error('No structural root');
 const reached=new Set([roots[0]]),queue=[roots[0]];while(queue.length){const n=queue.shift();for(const next of adjacent.get(n))if(!reached.has(next)){reached.add(next);queue.push(next);}}
 const unreachable=[...adjacent.keys()].filter(n=>!reached.has(n));
 return{root:roots[0],rootModule,rootedCount:reached.size,unreachable,topologicallyConnected:unreachable.length===0,qualification:'Graph connectivity preserves edge kinds and open gates; it is not proof of physical strength, fit or safety.'};
}
