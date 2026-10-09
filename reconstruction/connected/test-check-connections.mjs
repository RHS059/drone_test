import assert from 'node:assert/strict';
import * as T from '../app/docs/vendor/three.core.js';
import {auditConnections,auditPowerPaths}from'./check-connections.mjs';
const root=new T.Group();for(const name of['housing','ball','pin']){const n=new T.Mesh(new T.BoxGeometry(.01,.01,.01),new T.MeshBasicMaterial());n.name=name;root.add(n)}
const c={required_interfaces:['pivot'],interfaces:[{id:'pivot',a:{node:'housing',point_m:[0,0,0],axis:[0,1,0]},b:{node:'ball',point_m:[0,0,0],axis:[0,-1,0]},retaining_nodes:['pin'],status:'modeled_connection',source_reference:'known-answer fixture',position_tolerance_m:1e-6,axis_tolerance_rad:1e-6}]};
assert(auditConnections(root,c,T).pass);root.getObjectByName('ball').position.x=.001;assert(!auditConnections(root,c,T).pass);root.getObjectByName('ball').position.x=0;root.remove(root.getObjectByName('pin'));assert(!auditConnections(root,c,T).pass);
const p={components:[{id:'positive'},{id:'controller'},{id:'motor'},{id:'return'}],source_positive:'positive',source_return:'return',required_loads:['motor'],connections:[['positive','controller'],['controller','motor'],['motor','return']].map(([from,to],i)=>({id:String(i),from,to,from_terminal:'declared-out',to_terminal:'declared-in',status:'selected_interface',source_reference:'known-answer fixture'}))};
assert(auditPowerPaths(p).pass);p.connections.pop();assert(!auditPowerPaths(p).pass);p.connections[1].status='unknown';assert(auditPowerPaths(p).failures.some(x=>x.reason.includes('unresolved')));
console.log('PASS synthetic controls: anchor separation, missing retention, incomplete return and unresolved interface all fail closed. No rover claim until a real contract is bound.');
