// Samples world-space surface points of the front-left corner chain from the live viewer scene.
// Usage: (cd docs && python3 -m http.server 8770) &  node docs/assets/integration/corner_contact_dump.js out.json [url]
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const e=[];p.on('pageerror',x=>e.push(String(x)));
await p.goto(process.argv[3]||'http://localhost:8770/?webgl');await p.waitForFunction(()=>window.__CAD_DEBUG__&&window.__CAD_DEBUG__.rover,null,{timeout:120000});await p.waitForTimeout(3000);
const out=await p.evaluate(()=>{const api=window.__CAD_DEBUG__;let root=api.rover.rig.assembly;while(root.parent)root=root.parent;root.updateMatrixWorld(true);
 const want=/front_left|main_rail_left|front_rack|actuator/i;const res={};const v=new (api.rover.rig.assembly.position.constructor)();
 root.traverse(o=>{if(!o.isMesh)return;let n=o.name,q=o;while(q&&!want.test(n)){q=q.parent;n=q?q.name:''}if(!q)return;
  const key=(q.name||o.name)+'|'+o.name;const pos=o.geometry.attributes.position, idx=o.geometry.index;const arr=[];
  const P=i=>new (api.rover.rig.assembly.position.constructor)().fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld);
  const nT=idx?idx.count/3:pos.count/3;const tris=[];let area=0;
  for(let t=0;t<nT;t++){const a=P(idx?idx.getX(3*t):3*t),b=P(idx?idx.getX(3*t+1):3*t+1),c=P(idx?idx.getX(3*t+2):3*t+2);
   const ar=b.clone().sub(a).cross(c.clone().sub(a)).length()/2;tris.push([a,b,c,ar]);area+=ar;}
  const spacing=0.0015, budget=40000; let dens=Math.min(1/(spacing*spacing), budget/Math.max(area,1e-9));
  for(const [a,b,c,ar] of tris){let n=ar*dens;let k=Math.floor(n)+(Math.random()<n%1?1:0);k=Math.max(k,1);
   for(let j=0;j<k;j++){let r1=Math.random(),r2=Math.random();if(r1+r2>1){r1=1-r1;r2=1-r2;}
    arr.push([+(a.x+r1*(b.x-a.x)+r2*(c.x-a.x)).toFixed(5),+(a.y+r1*(b.y-a.y)+r2*(c.y-a.y)).toFixed(5),+(a.z+r1*(b.z-a.z)+r2*(c.z-a.z)).toFixed(5)]);}}
  res[key]=(res[key]||[]).concat(arr);});
 return res;});
require('fs').writeFileSync(process.argv[2],JSON.stringify(out));console.log(Object.keys(out).length,'meshes; errors',JSON.stringify(e).slice(0,300));await b.close();})();
