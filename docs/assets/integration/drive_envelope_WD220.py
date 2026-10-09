"""WD220 hub-drive ENVELOPE solid that closes the upright -> wheel-adapter load path.

Original geometry from public interface dimensions only (no vendor CAD): stator flange seats on the upright outboard
face (Y=797 mm, 8x M10 pattern, Ø172 socket), can passes back to Y=606, rotor runs to the output face at Y=928
(Ø166 flange, Ø94 pilot, 5x M16x1.5 studs on PCD 140, phase 0). Kept inside drive-reservation.json bounds.
It is a clearance/load-path envelope: internal shape, mass and bearing ratings are unknown.

Frame: corner C, left station X=0 (mm), wheel axis +Y at Z=-250. Run: python drive_envelope_WD220.py
"""
import json, math, sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'mechanical'))
from generate_cad import glb  # metres/Z-up GLB writer used by the rest of the repo

AX_Z = -250.0
Y_REAR, Y_SEAT, Y_FLANGE, Y_OUT = 606.0, 797.0, 809.0, 928.0


def cyl(r, y0, y1, x=0.0, z=AX_Z):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def build():
    can = cyl(85.5, Y_REAR, Y_SEAT)  # passes the Ø172 upright socket with 0.5 mm radial clearance
    # Asymmetric stator flange: Ø248 disc cut to the hole-pattern band (holes z = -49..+91 about the axis, r 113).
    flange = cyl(124, Y_SEAT, Y_FLANGE).intersect(cq.Solid.makeBox(260, Y_FLANGE - Y_SEAT, 166, cq.Vector(-130, Y_SEAT, AX_Z - 62)))
    for x, zr in [(-113, 0), (113, 0), (-101.823376, -49), (101.823376, -49), (-101.823376, 49), (101.823376, 49),
                  (-66.992537, 91), (66.992537, 91)]:
        flange = flange.cut(cyl(5.25, Y_SEAT, Y_FLANGE, x, AX_Z + zr))  # M10 clearance
    rotor = cyl(100, Y_FLANGE + 2, Y_OUT - 15)  # 2 mm running gap to stator flange
    out_flange = cyl(83, Y_OUT - 15, Y_OUT)
    pilot = cyl(47, Y_OUT, Y_OUT + 10)  # Ø94 into the adapter pilot socket
    studs = [cyl(8, Y_OUT, Y_OUT + 30, 70 * math.cos(math.radians(a)), AX_Z + 70 * math.sin(math.radians(a))) for a in range(0, 360, 72)]
    conn = cq.Solid.makeBox(80, 110, 60, cq.Vector(-40, 650, AX_Z + 85.5))  # cable gland/connector block on top of can
    stator = can.fuse(flange).fuse(conn).clean()
    rotor = rotor.fuse(out_flange).fuse(pilot).clean()
    for s in studs:
        rotor = rotor.fuse(s)
    return {'stator': stator, 'rotor_with_studs': rotor.clean()}


if __name__ == '__main__':
    parts = build()
    res = json.loads((HERE.parent / 'corners/drive-reservation.json').read_text())['left_corner_C_bounds_m']
    allb = cq.Compound.makeCompound(list(parts.values())).BoundingBox()
    inside = all(a >= b * 1000 - 0.5 for a, b in zip((allb.xmin, allb.ymin, allb.zmin), res[0])) and \
        all(a <= b * 1000 + 0.5 for a, b in zip((allb.xmax, allb.ymax, allb.zmax), res[1]))
    ass = cq.Assembly(name='drive_envelope_WD220')
    for n, s in parts.items():
        ass.add(s, name=n)
    ass.export(str(HERE / 'drive_envelope_WD220.step'))
    glb(list(parts.items()), HERE / 'drive_envelope_WD220.glb')
    report = {'part': 'drive_envelope_WD220', 'classification': 'public-dimension envelope, not vendor CAD', 'frame': 'corner C, left station X=0, mm',
              'bounds_mm': [[allb.xmin, allb.ymin, allb.zmin], [allb.xmax, allb.ymax, allb.zmax]], 'inside_drive_reservation': inside,
              'mass_kg': None, 'mass_note': 'WD220 mass not published for this variant; do not use envelope volume',
              'valid': all(s.isValid() for s in parts.values())}
    (HERE / 'drive_envelope_WD220.json').write_text(json.dumps(report, indent=1))
    print(json.dumps(report))
