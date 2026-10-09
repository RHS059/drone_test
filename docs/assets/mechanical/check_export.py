"""Independent STEP roundtrip and GLB-envelope validation. Run after generate_cad.py."""
from pathlib import Path
import json,struct
import numpy as np
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).resolve().parent
r={}
for stem,n in [('frame_R06',18),('adapter_R03',1)]:
    s=cq.importers.importStep(str(P/(stem+'.step'))).val()
    assert s.isValid() and len(s.Solids())==n
    b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);bounds=b.Get()
    raw=(P/(stem+'.glb')).read_bytes();magic,version,size=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and size==len(raw)
    jslen,jstype=struct.unpack_from('<II',raw,12);j=json.loads(raw[20:20+jslen]);assert len(j['nodes'])==n
    mins=[];maxs=[]
    for m in j['meshes']:
        a=j['accessors'][m['primitives'][0]['attributes']['POSITION']];mins.append(a['min']);maxs.append(a['max'])
    lo=np.min(mins,axis=0);hi=np.max(maxs,axis=0)
    assert np.allclose(lo,np.array(bounds[:3])/1000,atol=.00021) and np.allclose(hi,np.array(bounds[3:])/1000,atol=.00021)
    r[stem]={'STEP_roundtrip_valid':True,'STEP_solid_count':n,'STEP_volume_m3':s.Volume()*1e-9,'mass_kg_at_7850':s.Volume()*1e-9*7850,'exact_STEP_bounds_mm':bounds,'GLB_valid_container':True,'GLB_node_count':len(j['nodes']),'GLB_bounds_m':[lo.tolist(),hi.tolist()],'GLB_STEP_bounds_agree_tolerance_m':.00021}
(P/'export_roundtrip_tests.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
