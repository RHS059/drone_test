export function bindMainPairGraph(root,graph){
 const aliases={'Q0:P_OUT':'Q0_terminal_P_OUT_7SG8_lug','Q0:N_OUT':'Q0_terminal_N_OUT_7SG8_lug','LYNX:BAT+':'LYNX_BATpositive_Klauke7SG10_lug','LYNX:BAT-':'LYNX_BATnegative_Klauke7SG10_lug'};
 const refs=new Set(Object.keys(graph.nodes));for(const e of graph.edges)for(const field of['from_nodes','to_nodes','retaining_nodes'])for(const n of e[field]||[])refs.add(n);
 const nodes=new Map();for(const id of refs){const name=aliases[id]||id.replace(/^body\//,'');const found=[];root.traverse(n=>{if(n.name===name)found.push(n);});if(found.length!==1)throw Error('Missing or duplicate main cable interface: '+id);nodes.set(id,found[0]);}
 if(Object.keys(graph.nodes).length!==98||graph.edges.length!==22)throw Error('Unexpected main cable graph');
 return{nodes,edges:graph.edges,snapshot(){return{boundNodes:nodes.size,retainedOrFunctionalEdges:graph.edges.length,geometricJacketRoutes:2,physicalElectricalContinuityVerified:false,fullCircuitComplete:false};}};
}
