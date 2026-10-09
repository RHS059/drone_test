"""Nominal UR tool screw regression; no approval of thread engagement or fit."""
from pathlib import Path
import argparse, hashlib, json, math
import cadquery as cq


def evaluate(length, grip, maximum=7, proposed_minimum=4):
    if not all(math.isfinite(v) for v in (length, grip, maximum, proposed_minimum)):
        raise ValueError('Inputs must be finite')
    if length <= 0 or grip <= 0:
        raise ValueError('Positive screw length and grip required')
    protrusion = length-grip
    return {'nominal_protrusion_mm': protrusion,
            'manufacturer_maximum_screen_pass': protrusion <= maximum,
            'project_minimum_screen_pass': protrusion >= proposed_minimum,
            'nominal_screen_pass': proposed_minimum <= protrusion <= maximum}


def inspect(step, contract):
    shape=cq.importers.importStep(str(step)).val()
    assert shape.isValid() and len(shape.Solids()) == 1
    seats=[]; ur_faces=[]
    for f in shape.Faces():
        if f.geomType() != 'PLANE': continue
        n=f.normalAt(); c=f.Center()
        if abs(n.z) < .999999: continue
        if n.z < -.999999 and f.Area() > 1000 and abs(c.z-contract['ur_face_z_mm']) < 1e-7:
            ur_faces.append({'z_mm':c.z,'area_mm2':f.Area()})
        circles=[e.radius() for e in f.Edges() if e.geomType() == 'CIRCLE']
        if len(circles)==2 and sorted(round(r,5) for r in circles)==[4.25,7.5]:
            seats.append({'center_mm':[c.x,c.y,c.z], 'z_mm':c.z,
                          'inner_diameter_mm':8.5,'outer_diameter_mm':15})
    assert len(seats)==6, f'Expected six actual counterbore floor faces, found {len(seats)}'
    assert len(ur_faces)==1, 'Expected one broad actual UR-facing plane at the specified datum'
    grips=[s['z_mm']-ur_faces[0]['z_mm'] for s in seats]
    assert max(grips)-min(grips)<1e-6
    grip=sum(grips)/len(grips)
    result=evaluate(contract['candidate_underhead_length_mm'],grip,
                    contract['manufacturer_max_protrusion_mm'],contract['proposed_minimum_nominal_protrusion_mm'])
    return {'adapter_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),
            'actual_ur_face':ur_faces[0],'actual_counterbore_floors':seats,'actual_nominal_grip_mm':grip,
            'candidate_underhead_length_mm':contract['candidate_underhead_length_mm'],**result,
            'manufacturer_source':contract['source'],
            'proposed_minimum_is_manufacturer_requirement':False,
            'effective_thread_engagement_verified':False,'tolerance_stack_verified':False,
            'fabrication_approved':False,
            'limits':'This checks nominal protrusion only. Incomplete tip threads, chamfers, thread depth, exact fastener tolerance, adapter tolerance and effective engagement remain unresolved.'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('step',type=Path);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--contract',type=Path,default=Path(__file__).with_name('flange-fastener-contract.json'));a=ap.parse_args()
    r=inspect(a.step,json.loads(a.contract.read_text()));a.out.write_text(json.dumps(r,indent=2))
    print(json.dumps({k:r[k] for k in ['actual_nominal_grip_mm','nominal_protrusion_mm','nominal_screen_pass','fabrication_approved']}))
    raise SystemExit(0 if r['nominal_screen_pass'] else 1)
