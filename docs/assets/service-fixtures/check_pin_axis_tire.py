"""Verify centerline obstruction of the prior fixture-only pin corridor.
Original tire model includes assumed hidden geometry; no physical tire claim.
"""
from pathlib import Path
import json,hashlib
import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_OUT
from OCP.gp import gp_Pnt
P=Path(__file__).resolve().parent
f=P.parent/'wheels/tire_C01.step'
s=cq.importers.importStep(str(f)).val();assert s.isValid()
c=BRepClass3d_SolidClassifier(s.wrapped)
c.Perform(gp_Pnt(350,-150,0),1e-5);assert c.State()==TopAbs_IN
c.Perform(gp_Pnt(0,0,0),1e-5);assert c.State()==TopAbs_OUT
rows=[]
for x in [-220,220]:
 for z in [-170,170]:
  c.Perform(gp_Pnt(x,-128,z),1e-5)
  rows.append({'tire_local_mm':[x,-128,z],'strictly_inside':c.State()==TopAbs_IN})
assert all(r['strictly_inside'] for r in rows)
result={'scope':'Original modeled tire only, hidden profile assumptions remain. A centerline point 220 mm in either X direction from either outer pin center lies within the declared ±260 mm straight extraction corridor. Positive containment rejects a straight full-length cylinder clearance claim through the installed modeled wheel, even with zero tool radius. Does not rule out shorter extraction, offset tooling or wheel-first service.','tire_step_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'points':rows}
expected=json.loads((P/'pin_axis_tire_obstruction.json').read_text())
assert result==expected
print('PASS: four strict tire-containment witnesses reproduce the installed-wheel corridor obstruction. No service path is approved.')
