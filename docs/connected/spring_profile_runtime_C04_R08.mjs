/* Original visualization only. Eibach1800.300.0200S nominal ID/free/block are sourced.
   Wire10 mm, 12 helical turns and end profiles are explicit approximations.
   No supplier geometry, spring stress/rate or dynamic-force calculation is encoded.
   Mesh local origin is the upper spring-bearing plane; local +Z points to lower seat.
   Scene units metres. Place at upperEye + bodyAxisZ*0.170.
   Use indexed arrays with BufferGeometry; do not axially scale the entire GLB spring. */
export const springEvidence = Object.freeze({
  part: 'Eibach1800.300.0200S',
  source: 'https://eibach.com/product/1800.300.0200S',
  nominalIDM: .0762, nominalFreeLengthM: .4572, catalogBlockHeightM: .161036,
  catalogRateLbPerIn: 200, rateQualified: false, wireAndCoilProfileSourceExact: false,
  assumedWireDiameterM: .010, assumedOutsideDiameterM: .0962,
  reservedOutsideEnvelopeM: .110, positiveStabilityAndGuidanceQualified: false, mechanicalAlignmentGuideModeled: true
});
export function makeSpringProfile() {
  const positions=[], normals=[], coefficients=[], offsets=[], normalSeed=[], indices=[];
  const wire=.005, radius=.0431, m=20;
  function tube(n, turns, kind) {
    const base=positions.length/3;
    for(let i=0;i<=n;i++) {
      const t=i/n, th=t*2*Math.PI*turns, co=Math.cos(th), si=Math.sin(th);
      for(let j=0;j<m;j++) {
        const ph=j*2*Math.PI/m, cp=Math.cos(ph), sp=Math.sin(ph);
        positions.push((radius+wire*cp)*co,(radius+wire*cp)*si,0);
        coefficients.push(kind==='helix'?t:kind==='upper'?0:1);
        offsets.push((kind==='helix'?.004-.008*t:kind==='upper'?.004:-.004)+wire*sp);
        normalSeed.push(cp*co,cp*si,sp); normals.push(0,0,0);
      }
    }
    for(let i=0;i<n;i++) for(let j=0;j<m;j++) {
      const a=base+i*m+j,b=base+i*m+(j+1)%m,c=b+m,d=a+m;
      indices.push(a,b,c,a,c,d);
    }
  }
  tube(12*96,12,'helix');tube(96,1,'upper');tube(96,1,'lower');
  const pos=new Float32Array(positions),nor=new Float32Array(normals),idx=new Uint32Array(indices);
  function setSeatLengthM(H) {
    if(!Number.isFinite(H)||H<.300-1e-8||H>.370+1e-8) throw new RangeError('Outside prototype screened seat-length domain');
    for(let k=0;k<coefficients.length;k++) {
      const z=coefficients[k]*H+offsets[k];pos[k*3+2]=Math.max(0,Math.min(H,z));
      if(z<=0){nor[k*3]=0;nor[k*3+1]=0;nor[k*3+2]=-1;}
      else if(z>=H){nor[k*3]=0;nor[k*3+1]=0;nor[k*3+2]=1;}
      else{nor[k*3]=normalSeed[k*3];nor[k*3+1]=normalSeed[k*3+1];nor[k*3+2]=normalSeed[k*3+2];}
    }
    return {positions:pos,normals:nor,indices:idx};
  }
  return {positions:pos,normals:nor,indices:idx,setSeatLengthM};
}
export function springSeatLengthFromEyeLengthM(eyeLengthM) { return eyeLengthM-.225; }
