// Patches original, baked-coordinate CAD nodes by explicit name. Validation is
// completed before any scene mutation, so missing or duplicate parts fail closed.
export function applyNamedPartPatch(base, delta, changes) {
  if (!Array.isArray(changes) || !changes.length) throw Error('Empty CAD replacement schedule');
  const index = group => {
    const out=new Map();
    for(const node of group.children){
      if(!node.name || out.has(node.name))throw Error('Missing or duplicate CAD node name');
      out.set(node.name,node);
    }
    return out;
  };
  const old=index(base), fresh=index(delta), scheduled=new Set();
  for(const c of changes){
    if(!['replace','add','remove'].includes(c.action)||!c.name||scheduled.has(c.name))throw Error('Invalid or duplicate CAD change');
    scheduled.add(c.name);
    if(c.action==='add' && old.has(c.name))throw Error('CAD addition already exists: '+c.name);
    if(c.action!=='add' && !old.has(c.name))throw Error('Missing CAD replacement/removal target: '+c.name);
    if(c.action!=='remove' && !fresh.has(c.name))throw Error('Missing CAD delta node: '+c.name);
    if(c.action==='remove' && fresh.has(c.name))throw Error('Removed CAD part supplied in delta: '+c.name);
  }
  if([...fresh.keys()].some(n=>!scheduled.has(n)))throw Error('Unscheduled CAD delta node');
  // Both source roots must use the same local CAD frame. Nonidentity child
  // matrices are intentionally retained, not flattened or reset.
  for(const g of [base,delta]){
    if(g.matrixAutoUpdate)g.updateMatrix();
    if(g.matrix.elements.some((x,i)=>!Number.isFinite(x)||Math.abs(x-(i%5===0?1:0))>1e-12))throw Error('CAD patch roots use different coordinate frames');
  }
  for(const c of changes){
    if(c.action!=='add')base.remove(old.get(c.name));
    if(c.action!=='remove')base.add(fresh.get(c.name));
  }
  return {replaced:changes.filter(c=>c.action==='replace').length,added:changes.filter(c=>c.action==='add').length,removed:changes.filter(c=>c.action==='remove').length,nodes:base.children.length};
}

export function bindServiceVisibility(body, groups) {
  const nodes=new Map(body.children.map(n=>[n.name,n])), removable=new Set(),retained=new Set();
  for(const group of groups){
    for(const n of group.removable||[]){if(!nodes.has(n))throw Error('Missing removable service part: '+n);removable.add(n);}
    for(const n of group.retained_on_body||[]){if(!nodes.has(n))throw Error('Missing retained service part: '+n);retained.add(n);}
  }
  if([...retained].some(n=>removable.has(n)))throw Error('Part cannot be both removed and retained');
  return {setOpen(v){for(const n of removable)nodes.get(n).visible=!v;},snapshot(){return {removable:[...removable],retained:[...retained]};}};
}
