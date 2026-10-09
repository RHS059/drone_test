import fs from 'node:fs';import assert from 'node:assert/strict';
import * as T from '../app/docs/vendor/three.core.js';
import {readCad} from './read-original-glb.mjs';
import {applyNamedPartPatch,bindServiceVisibility} from './named-part-patch.mjs';
const p=new URL('../body-power/panel-retention/',import.meta.url);
const manifest=JSON.parse(fs.readFileSync(new URL('replacement_addition_manifest.json',p)));
const exclusions=new Set(manifest.unfrozen_rear_service_enclosure_group.delta_changes_to_exclude);
const changes=manifest.changes.filter(c=>!exclusions.has(c.name));
const base=readCad(new URL('../body-power/R02/body_power_R02.glb',import.meta.url));
const delta=readCad(new URL('body_retention_delta_nonrear_PR01.glb',p));
const prior=new Map(base.children.map(n=>[n.name,n]));
const next=new Map(delta.children.map(n=>[n.name,n]));
const receipt=applyNamedPartPatch(base,delta,changes);
assert.equal(receipt.replaced+receipt.added,157);assert.equal(delta.children.length,0);
for(const c of changes){assert.equal(base.getObjectByName(c.name),next.get(c.name));if(c.action==='replace')assert.equal(prior.get(c.name).parent,null);}
for(const [name,node]of prior)if(!changes.some(c=>c.name===name))assert.equal(base.getObjectByName(name),node);
const service=bindServiceVisibility(base,manifest.retained_service_groups.filter(g=>g.name!=='rear_controller_hatch'));
service.setOpen(true);for(const n of service.snapshot().removable)assert.equal(base.getObjectByName(n).visible,false);
for(const n of service.snapshot().retained)assert.equal(base.getObjectByName(n).visible,true);
service.setOpen(false);for(const n of service.snapshot().removable)assert.equal(base.getObjectByName(n).visible,true);
for(const bad of [[{action:'replace',name:'missing'}],[{action:'add',name:base.children[0].name}]]){const n=base.children.length;assert.throws(()=>applyNamedPartPatch(base,new T.Group(),bad));assert.equal(base.children.length,n);}
const a=new T.Group(),b=new T.Group();for(const g of[a,b]){let n=new T.Group();n.name='x';g.add(n);}b.position.x=1;
assert.throws(()=>applyNamedPartPatch(a,b,[{action:'replace',name:'x'}]),/coordinate frames/);assert.equal(a.children.length,1);assert.equal(b.children.length,1);
for(const manual of [true,false]){const a=new T.Group(),b=new T.Group();for(const g of[a,b]){const n=new T.Group();n.name='x';g.add(n);}b.matrixAutoUpdate=!manual;if(manual)b.matrix.makeTranslation(1,0,0);else b.position.x=NaN;const original=b.matrix.toArray();assert.throws(()=>applyNamedPartPatch(a,b,[{action:'replace',name:'x'}]),/coordinate frames/);assert.equal(a.children.length,1);assert.equal(b.children.length,1);if(manual)assert.deepEqual(b.matrix.toArray(),original);}
console.log(JSON.stringify({pass:true,...receipt,service_groups:7,atomic_failure_cases:5}));
