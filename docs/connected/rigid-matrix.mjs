// Validate a proper affine rigid transform, rejecting scale/shear even when det=1.
export function assertRigidMatrix(matrix,tolerance=1e-9){
 const e=matrix.elements;
 if(e.length!==16||!e.every(Number.isFinite)||[e[3],e[7],e[11],e[15]-1].some(v=>Math.abs(v)>tolerance))throw Error('Invalid rigid affine matrix');
 for(let i=0;i<3;i++)for(let j=0;j<3;j++){
  let dot=0;for(let k=0;k<3;k++)dot+=e[4*i+k]*e[4*j+k];
  if(Math.abs(dot-(i===j?1:0))>tolerance)throw Error('Scale or shear in rigid transform');
 }
 if(Math.abs(matrix.determinant()-1)>tolerance)throw Error('Reflection in rigid transform');
 return matrix;
}
