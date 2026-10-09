// GLTFLoader sanitizes names for animation bindings. CAD contracts address the
// exact exported node names, recovered by source index rather than text guesses.
export function restoreCadNodeNames(gltf){
 const assignments=[];
 gltf.scene.traverse(node=>{const index=gltf.parser.associations.get(node)?.nodes;
  if(index===undefined)return;
  const name=gltf.parser.json.nodes[index]?.name;
  if(typeof name==='string'&&name.length)assignments.push([node,name]);
 });
 for(const [node,name]of assignments)node.name=name;
 return gltf;
}
