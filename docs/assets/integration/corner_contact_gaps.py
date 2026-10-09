"""Measures surface-to-surface gaps (1.5 mm sampling) between each declared joint in the front-left corner chain.
Usage: python docs/assets/integration/corner_contact_gaps.py out.json   (from corner_contact_dump.js)"""
import json, sys
import numpy as np
from scipy.spatial import cKDTree

d = {k: np.array(v) for k, v in json.load(open(sys.argv[1])).items()}
G = lambda *p: (np.vstack([d[k] for k in d if all(s in k for s in p)]) if any(all(s in k for s in p) for k in d) else None)
fl = 'front_left'
CHAIN = [
    ('tyre -> rim', (fl, 'wheel|tire'), (fl, 'wheel|rim')), ('rim -> hub motor output flange', (fl, 'wheel|rim'), (fl, 'drive_output_hub')),
    ('wheel nuts -> rim', (fl, 'direct_wheel_nut'), (fl, 'wheel|rim')), ('wheel nuts -> studs', (fl, 'direct_wheel_nut'), (fl, 'drive_input_stud')),
    ('studs -> output flange', (fl, 'drive_input_stud'), (fl, 'drive_output_hub')), ('output flange -> motor body', (fl, 'drive_output_hub'), (fl, 'drive_stator')),
    ('motor body -> knuckle', (fl, 'drive_stator'), (fl + '_upright|',)), ('M10 screws -> knuckle', (fl, 'drive_mount_M10'), (fl + '_upright|',)),
    ('knuckle -> upper ball joint', (fl + '_upright|',), (fl, 'upper_outer')), ('knuckle -> lower ball joint', (fl + '_upright|',), (fl, 'lower_outer')),
    ('upper ball joint -> upper arm', (fl, 'upper_outer'), (fl + '_upper|',)), ('lower ball joint -> lower arm', (fl, 'lower_outer'), (fl + '_lower|',)),
    ('upper pivot bearings -> upper arm', (fl, 'upper_root'), (fl + '_upper|',)), ('lower pivot bearings -> lower arm', (fl, 'lower_root'), (fl + '_lower|',)),
    ('pivot bearings -> clamp', (fl, '_root'), (fl + '_clamp|',)), ('clamp -> frame rail', (fl + '_clamp|',), ('main_rail_left',)),
    ('outer tie pin -> knuckle', (fl, 'outer_tie_pin'), (fl + '_upright|',)), ('outer rod-end ball -> tie pin', (fl, 'outer_ball'), (fl, 'outer_tie_pin')),
    ('inner rod-end ball -> tie pin', (fl, 'inner_ball'), (fl, 'inner_tie_pin')), ('inner tie pin -> rack carriage', (fl, 'inner_tie_pin'), ('front_rack_carriage',)),
    ('rack carriage -> guide', ('front_rack_carriage',), ('front_rack_guide',)), ('guide -> crossbeam', ('front_rack_guide',), ('front_rack_crossbeam',)),
    ('crossbeam -> clamp', ('front_rack_crossbeam',), (fl + '_clamp|',)), ('actuator pin -> rack carriage', ('front_actuator_front_pin',), ('front_rack_carriage',)),
    ('upper shock pin -> shock eye', (fl, 'upper_shared_pin'), (fl, 'shock_upper_eye')), ('upper shock pin -> clamp', (fl, 'upper_shared_pin'), (fl + '_clamp|',)),
    ('lower shock pin -> shock eye', (fl, 'lower_shared_pin'), (fl, 'shock_lower_eye')), ('lower shock pin -> lower arm', (fl, 'lower_shared_pin'), (fl + '_lower|',)),
]
bad = 0
for label, a, b in CHAIN:
    A, B = G(*a), G(*b)
    if A is None or B is None:
        print(f'{label:40s} MISSING'); bad += 1; continue
    m = cKDTree(B).query(A, k=1)[0].min() * 1000
    ok = m < 2.5; bad += not ok
    print(f"{label:40s} {m:6.1f} mm  {'touching' if ok else 'GAP'}")
sys.exit(1 if bad else 0)
