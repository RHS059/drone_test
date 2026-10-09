"""Assembly connectivity screen: is every part physically held by something?

Loads STEP solids with their assembly transforms (as rover.js places them), builds a touch graph
(gap <= TOUCH mm), and walks it from the frame. Reports:
  - parts not connected to the frame at all (floating),
  - positive-volume interferences,
  - the gap between each floating group and its nearest connected part.
Touching is necessary, not sufficient: it does not prove a fastener, weld, bearing or load rating.

Run from repo root: python docs/assets/mechanical/assembly_check.py [--corner]  -> assembly_check[_corner].json
Bearing fit envelopes are included as the stand-in for the wishbone bearings.
"""
import json, math
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2] / 'assets'
TOUCH = 0.5  # mm
OUT = Path(__file__).with_name('assembly_check.json')
# Declared joints whose load-carrying element is internal to a purchased part (not modelled as a solid).
JOINTS = [('drive_stator', 'drive_rotor', 'WD220 internal output bearing (vendor; rating unknown)')]


def load(rel, rot_x_deg=0, move=(0, 0, 0)):
    s = cq.importers.importStep(str(ROOT / rel)).val()
    if rot_x_deg:
        s = s.rotate((0, 0, 0), (1, 0, 0), rot_x_deg)
    return s.translate(cq.Vector(*move))


def corner_left_middle():
    """Middle-left corner (station X=0) exactly as rover.js + interface_contract_C02_R06 place it, in frame C (mm)."""
    c = json.loads((ROOT / 'corners/interface_contract_C02_R06.json').read_text())
    parts = {}
    for spec in c['meshes']:
        rel = 'corners/' + spec['file'].replace('.glb', '.step')
        rot = math.degrees(spec.get('initial_rotation_x_rad', 0))
        move = [v * 1000 for v in spec.get('initial_translation_m', [0, 0, 0])]
        shape = load(rel, rot, move)
        for i, solid in enumerate(shape.Solids()):
            parts[f"{spec['file'].split('_C02')[0]}#{i}" if len(shape.Solids()) > 1 else spec['file'].split('_C02')[0]] = solid
    import sys
    sys.path.insert(0, str(ROOT / 'integration'))
    from drive_envelope_WD220 import build as drive
    d = drive()
    parts['drive_stator'], parts['drive_rotor'] = d['stator'], d['rotor_with_studs']
    wc = [v * 1000 for v in c['left_at_station_zero']['wheel_center']]
    for i, solid in enumerate(load('wheels/wheel_C01.step', 0, wc).Solids()):
        parts[f'wheel_C01#{i}'] = solid
    return parts


def build(corner_only=False):
    parts = {f'frame_R07#{i}': s for i, s in enumerate(load('mechanical/frame_R07.step').Solids())}
    if corner_only:
        parts.update(corner_left_middle())
        return parts
    body = load('body-power/body_power_R01.step').Solids()
    parts.update({f'body#{i}': s for i, s in enumerate(body)})
    res = load('body-power/cots_reservations_R01.step').Solids()
    parts.update({f'reservation#{i}': s for i, s in enumerate(res)})
    parts.update(corner_left_middle())
    return parts


def check(parts):
    names = list(parts)
    boxes = {n: parts[n].BoundingBox() for n in names}
    edges, clashes = [], []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = boxes[a], boxes[b]
            if (A.xmin > B.xmax + TOUCH or B.xmin > A.xmax + TOUCH or A.ymin > B.ymax + TOUCH or B.ymin > A.ymax + TOUCH
                    or A.zmin > B.zmax + TOUCH or B.zmin > A.zmax + TOUCH):
                continue
            d = parts[a].distance(parts[b])
            if d <= TOUCH:
                edges.append((a, b))
                if d < 1e-6:
                    v = parts[a].intersect(parts[b]).Volume()
                    if v > 1:
                        clashes.append([a, b, round(v, 1)])
    for a, b, _ in JOINTS:
        if a in parts and b in parts:
            edges.append((a, b))
    grounded = {n for n in names if n.startswith('frame_R07')}
    while True:
        nxt = grounded | {b for a, b in edges if a in grounded} | {a for a, b in edges if b in grounded}
        if nxt == grounded:
            break
        grounded = nxt
    floating = [n for n in names if n not in grounded]
    gaps = []
    for n in floating:
        near = min(((parts[n].distance(parts[g]), g) for g in grounded
                    if parts[n].BoundingBox().center.sub(parts[g].BoundingBox().center).Length < 1500), default=(None, None))
        gaps.append({'part': n, 'nearest_connected': near[1], 'gap_mm': None if near[0] is None else round(near[0], 1)})
    return {'touch_tolerance_mm': TOUCH, 'declared_joints': [j for j in JOINTS if j[0] in parts and j[1] in parts], 'parts': len(names), 'connected_to_frame': len(grounded), 'floating': gaps,
            'interferences_mm3': clashes, 'touch_pairs': len(edges)}


if __name__ == '__main__':
    import sys
    fast = '--corner' in sys.argv
    r = check(build(corner_only=fast))
    if fast:
        OUT = OUT.with_name('assembly_check_corner.json')
    OUT.write_text(json.dumps(r, indent=1))
    print(f"{r['parts']} parts, {r['connected_to_frame']} connected to frame, {len(r['floating'])} floating, {len(r['interferences_mm3'])} interferences")
    for g in r['floating']:
        print('  FLOATING', g)
    for c in r['interferences_mm3']:
        print('  CLASH', c)
