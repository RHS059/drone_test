// Read-only tests of actual rendered transforms and declared connection completeness.
// Passing anchors cannot certify strength, fits, electrical protection or real hardware.
export function auditConnections(root, contract, THREE) {
  const failures=[], results=[];
  const fail=(id,reason)=>failures.push({id,reason});
  const required=contract.required_interfaces||[];
  if(!required.length)fail('contract','No required interface inventory');
  const interfaces=new Map();
  for(const j of contract.interfaces||[]){if(interfaces.has(j.id))fail(j.id,'Duplicate interface ID');interfaces.set(j.id,j);}
  root.updateMatrixWorld(true);
  const hasGeometry=node=>{let found=false;node.traverse(o=>{if(o.isMesh&&o.geometry?.attributes?.position?.count>0)found=true;});return found;};
  for(const id of required){
    const j=interfaces.get(id);if(!j){fail(id,'Required interface not described');continue;}
    const sides=[];
    for(const key of ['a','b']){
      const s=j[key],node=s&&root.getObjectByName(s.node);
      if(!node){fail(id,`Missing rendered ${key} component: ${s?.node}`);continue;}
      if(!hasGeometry(node)){fail(id,`Empty ${key} scene node has no physical mesh: ${s.node}`);continue;}
      if(!Array.isArray(s.point_m)||s.point_m.length!==3||!s.point_m.every(Number.isFinite)){fail(id,`Invalid ${key} anchor`);continue;}
      const point=new THREE.Vector3(...s.point_m).applyMatrix4(node.matrixWorld);
      let axis=null;
      if(s.axis){if(s.axis.length!==3||!s.axis.every(Number.isFinite)||Math.hypot(...s.axis)<1e-12){fail(id,`Invalid ${key} axis`);continue;}axis=new THREE.Vector3(...s.axis).transformDirection(node.matrixWorld);}
      sides.push({point,axis});
    }
    for(const name of j.retaining_nodes||[]){const n=root.getObjectByName(name);if(!n||!hasGeometry(n))fail(id,`Missing retaining component geometry: ${name}`);}
    if(!j.retaining_nodes?.length&&!j.retention_integral)fail(id,'No modeled retention identified');
    if(!j.source_reference)fail(id,'Missing source/drawing reference');
    if(j.status!=='modeled_connection')fail(id,'Connection unresolved or merely reserved');
    if(sides.length!==2)continue;
    const gap=sides[0].point.distanceTo(sides[1].point),tol=j.position_tolerance_m;
    if(!Number.isFinite(tol)||tol<0)fail(id,'Missing finite positional acceptance bound');
    else if(gap>tol)fail(id,`Anchor gap ${gap} m exceeds ${tol} m`);
    let angle=null;
    if(sides.every(s=>s.axis)){
      // Axes are unoriented unless the joint explicitly demands same-direction vectors.
      const dot=sides[0].axis.dot(sides[1].axis);angle=Math.acos(Math.min(1,Math.max(-1,j.axis_directed?dot:Math.abs(dot))));
      if(!Number.isFinite(j.axis_tolerance_rad)||j.axis_tolerance_rad<0)fail(id,'Missing finite axis acceptance bound');
      else if(angle>j.axis_tolerance_rad)fail(id,`Axis mismatch ${angle} rad`);
    }
    results.push({id,gap_m:gap,axis_angle_rad:angle});
  }
  return {pass:failures.length===0,checked:results.length,required:required.length,results,failures,scope:'Declared retained interfaces and actual scene transforms only; no hardware/load/electrical safety qualification'};
}

export function auditPowerPaths(contract){
 const failures=[],edges=contract.connections||[],nodes=new Map((contract.components||[]).map(x=>[x.id,x]));
 const fail=(id,reason)=>failures.push({id,reason});
 const adjacency=new Map();
 for(const e of edges){
  if(!nodes.has(e.from)||!nodes.has(e.to))fail(e.id,'Connection endpoint component missing');
  if(!e.from_terminal||!e.to_terminal)fail(e.id,'Named physical terminal missing');
  if(e.status!=='selected_interface')fail(e.id,'Electrical interface unresolved');
  if(!e.source_reference)fail(e.id,'No compatibility/source evidence');
  if(!adjacency.has(e.from))adjacency.set(e.from,[]);adjacency.get(e.from).push(e.to);
 }
 function reaches(a,b){const todo=[a],seen=new Set();while(todo.length){const n=todo.pop();if(n===b)return true;if(seen.has(n))continue;seen.add(n);todo.push(...(adjacency.get(n)||[]));}return false;}
 const loads=contract.required_loads||[];if(!loads.length)fail('contract','No required powered-load inventory');
 for(const id of loads){if(!nodes.has(id)){fail(id,'Powered component missing');continue;}if(!reaches(contract.source_positive,id))fail(id,'No positive power path');if(!reaches(id,contract.source_return))fail(id,'No return path');}
 return {pass:!failures.length,required_loads:loads.length,failures,scope:'Declared terminal graph continuity only; no current, fault, thermal, EMC or functional-safety qualification'};
}
