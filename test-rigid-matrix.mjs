import assert from 'node:assert/strict';import * as T from './docs/vendor/three.core.js';import{assertRigidMatrix}from './docs/connected/rigid-matrix.mjs';
assertRigidMatrix(new T.Matrix4().makeTranslation(2,-1,.4).multiply(new T.Matrix4().makeRotationZ(.77)));
for(const m of[new T.Matrix4().makeScale(2,.5,1),new T.Matrix4().makeScale(-1,1,1),new T.Matrix4().makeShear(.2,0,0,0,0,0)])assert.throws(()=>assertRigidMatrix(m));
for(const at of[0,3,7,11,15]){const m=new T.Matrix4();m.elements[at]=NaN;assert.throws(()=>assertRigidMatrix(m));}
const m=new T.Matrix4();m.elements[3]=.1;assert.throws(()=>assertRigidMatrix(m));console.log('PASS rigid transform guards: proper translation/rotation accepted; scale, shear, reflection, NaN and nonaffine matrices rejected.');
