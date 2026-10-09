import fs from 'node:fs/promises';
import {createEngine,summarize} from '../simulation.mjs';
const root=new URL('../',import.meta.url);
const engine=await createEngine(async p=>new Uint8Array(await fs.readFile(new URL(p,root))));
const runs=[];
for(const name of ['nominal','low-friction','heavy']){
 const sim=engine.createCase(name),samples=[];
 for(let i=0;i<5500;i++){sim.step();if((i+1)%10===0)samples.push(sim.sample());}
 const metrics=summarize(samples);runs.push({case:name,samples,metrics});console.log(name,metrics);sim.dispose();
}
await fs.writeFile(new URL('results/wasm.json',root),JSON.stringify({engine:engine.mj.mj_versionString(),runs}));
