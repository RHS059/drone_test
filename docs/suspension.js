// Original parallel-wishbone geometry. No force, traction or load qualification.
export function rotateX([x,y,z],q){const c=Math.cos(q),s=Math.sin(q);return[x,c*y-s*z,s*y+c*z];}
export const add=(a,b)=>a.map((v,i)=>v+b[i]);
export const subtract=(a,b)=>a.map((v,i)=>v-b[i]);
export const length=a=>Math.hypot(...a);
export function suspensionPose(corner,q){
 if(!Number.isFinite(q))throw Error('Suspension angle must be finite');
 if(q<corner.limits[0]-1e-10||q>corner.limits[1]+1e-10)throw Error('Suspension travel limit exceeded');
 const signed=q*(corner.side_sign??1),outer=rotateX(corner.outer_vector,signed);
 const upper=add(corner.upper_pivot,outer),lower=add(corner.lower_pivot,outer);
 const translation=subtract(lower,add(corner.lower_pivot,corner.outer_vector));
 const wheel=add(corner.wheel_center,translation);
 const shockLower=add(corner.lower_pivot,rotateX(subtract(corner.shock_lower,corner.lower_pivot),signed));
 const shockUpper=[...corner.shock_upper],shockLength=length(subtract(shockUpper,shockLower));
 return{angle:signed,upper,lower,wheel,translation,shock:{upper:shockUpper,lower:shockLower,length:shockLength}};
}
