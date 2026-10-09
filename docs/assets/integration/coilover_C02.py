"""Coilover envelope + spring sizing for corner C02 (left, station X=0), from interface_contract_C02_R06 eye points.

Envelope only (no OEM shock CAD): Ø40x30 eye bushings, Ø20 shaft, Ø57 body (2.0-in class), Ø90/Ø70 spring envelope.
Sweeps the parallel-link suspension over the contract's planned +-12 deg, moving arms, upright, drive, adapter, wheel
and the lower eye exactly as the contract's motion rule says, and checks the coilover for clashes at each step.
Spring rate is sized for a target ride frequency, for several vehicle-mass scenarios (whole-vehicle mass is not yet known).

Run: python coilover_C02.py  -> coilover_C02.step/.glb (neutral pose) + coilover_C02.json
"""
import json, math, sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'mechanical'))
from generate_cad import glb
import assembly_check as ac

C = json.loads((HERE.parent / 'corners/interface_contract_C02_R06.json').read_text())['left_at_station_zero']
mm = lambda v: cq.Vector(*[x * 1000 for x in v])
FIXED = mm(C['coilover_fixed_eye'])
LP = mm(C['lower_pivot']); UP = mm(C['upper_pivot'])
LOWER_VEC = mm(C['coilover_lower_attachment_vector_from_lower_pivot'])
ARM = mm(C['outer_lower']) - LP  # lower pivot -> outer lower joint


def rot_x(v, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return cq.Vector(v.x, v.y * c - v.z * s, v.y * s + v.z * c)


def coilover(a, b):
    """Eye-to-eye envelope from a (fixed, top) to b (lower arm)."""
    d = (b - a); L = d.Length; u = d.normalized()
    eye = lambda p: cq.Solid.makeCylinder(20, 30, p - cq.Vector(15, 0, 0), cq.Vector(1, 0, 0))
    seg = lambda r, t0, t1: cq.Solid.makeCylinder(r, (t1 - t0) * L, a + u * (t0 * L), u)
    body = seg(28.5, 0.06, 0.62)            # damper body from top
    shaft = seg(10, 0.62, 0.94)
    spring = seg(45, 0.10, 0.88).cut(seg(35, 0.10, 0.88))  # spring envelope between perches
    perches = seg(45, 0.08, 0.10).fuse(seg(45, 0.88, 0.90))
    return eye(a).fuse(eye(b)).fuse(body).fuse(shaft).fuse(spring).fuse(perches).clean()


def pose(deg):
    """Corner parts at arm angle `deg` per the contract motion rule (left corner)."""
    P = ac.corner_left_middle()
    shift = rot_x(ARM, deg) - ARM
    out = {}
    for n, s in P.items():
        if n.startswith(('upper_wishbone', 'upper_bearing')):
            s = s.rotate(UP, UP + cq.Vector(1, 0, 0), deg)
        elif n.startswith(('lower_wishbone', 'lower_bearing')):
            s = s.rotate(LP, LP + cq.Vector(1, 0, 0), deg)
        elif not n.startswith(('stationary', 'inner_backing')):
            s = s.translate(shift)  # upright, pins, drive, adapter, wheel translate (parallel links)
        out[n] = s
    return out, LP + rot_x(LOWER_VEC, deg), shift.z


def main():
    sweep = []
    for deg in (-12, -6, 0, 6, 12):
        parts, lower_eye, wheel_dz = pose(deg)
        co = coilover(FIXED, lower_eye)
        clashes = []
        for n, s in parts.items():
            if co.distance(s) < 1e-6:
                v = co.intersect(s).Volume()
                if v > 1:
                    clashes.append([n, round(v, 1)])
        sweep.append({'arm_deg': deg, 'wheel_dz_mm': round(wheel_dz, 1), 'eye_to_eye_mm': round((lower_eye - FIXED).Length, 1),
                      'clashes_mm3': clashes})
        print(sweep[-1], flush=True)
    # Motion ratio = d(spring length)/d(wheel travel), central difference about neutral.
    L = {s['arm_deg']: s['eye_to_eye_mm'] for s in sweep}; Z = {s['arm_deg']: s['wheel_dz_mm'] for s in sweep}
    mr = abs((L[6] - L[-6]) / (Z[6] - Z[-6]))
    unsprung = 90.0  # kg per corner, typical: wheel/tyre ~42, drive ~30 (unknown), adapter/upright/half arms ~18
    f = 1.4          # Hz target ride frequency, typical heavy off-road
    rates = []
    for M in (1300, 1600, 2000):
        m = (M - 6 * unsprung) / 6
        kw = (2 * math.pi * f) ** 2 * m       # N/m at wheel
        ks = kw / mr ** 2                      # N/m at spring
        static = m * 9.81 / mr                 # N in spring at ride
        rates.append({'vehicle_kg': M, 'sprung_per_corner_kg': round(m, 1), 'wheel_rate_N_mm': round(kw / 1000, 1),
                      'spring_rate_N_mm': round(ks / 1000, 1), 'spring_rate_lb_in': round(ks / 175.127, 0),
                      'static_spring_force_kN': round(static / 1000, 2), 'static_sag_spring_mm': round(static / ks * 1000, 1)})
    co = coilover(FIXED, LP + LOWER_VEC)
    ass = cq.Assembly(name='coilover_C02'); ass.add(co, name='coilover_envelope'); ass.export(str(HERE / 'coilover_C02.step'))
    glb([('coilover_envelope', co)], HERE / 'coilover_C02.glb')
    stroke = max(L.values()) - min(L.values())
    report = {'classification': 'envelope + sizing, not OEM shock CAD or qualified spring', 'frame': 'corner C, left station X=0, mm',
              'eyes_mm': {'fixed': list(FIXED.toTuple()), 'lower_at_neutral': list((LP + LOWER_VEC).toTuple())},
              'sweep': sweep, 'motion_ratio_spring_per_wheel': round(mr, 3), 'shock_stroke_needed_mm_for_pm12deg': round(stroke, 1),
              'wheel_travel_mm_for_pm12deg': round(Z[12] - Z[-12], 1), 'ride_frequency_Hz': f, 'unsprung_per_corner_kg_assumed': unsprung,
              'spring_sizing': rates,
              'selection_rule': 'pick a 2.0-2.5 in coilover with eye-to-eye at ride = neutral eye_to_eye and stroke >= shock_stroke_needed + 10 mm bump margin; spring rate from row matching the measured vehicle mass'}
    (HERE / 'coilover_C02.json').write_text(json.dumps(report, indent=1))
    print(json.dumps({k: report[k] for k in ('motion_ratio_spring_per_wheel', 'shock_stroke_needed_mm_for_pm12deg', 'wheel_travel_mm_for_pm12deg', 'spring_sizing')}, indent=1))


if __name__ == '__main__':
    main()
