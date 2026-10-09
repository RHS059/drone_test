"""Buildability (DFM) screen for STEP weldments/parts. Units mm.
Run: python dfm_check.py part.step [more.step ...]  -> prints and writes <stem>_dfm.json
Checks geometry against standard stock and hole tables, and checks that every drilled
hole can actually be drilled/tapped/bolted (exit and approach not blocked by another part).
A clean screen is necessary for fabrication, not sufficient: no strength, tolerance or weld check.
"""
import sys, json, math
from pathlib import Path
import cadquery as cq
from OCP.BRepTools import BRepTools

# ISO 2306 tap drills (coarse), ISO 273 clearance fine/medium, DIN 974-1 counterbores for ISO 4762.
TAP = {2.5: 'M3', 3.3: 'M4', 4.2: 'M5', 5.0: 'M6', 6.8: 'M8', 8.5: 'M10', 10.2: 'M12', 14.0: 'M16', 17.5: 'M20'}
CLEAR = {'M3': (3.2, 3.6), 'M4': (4.3, 4.8), 'M5': (5.3, 5.8), 'M6': (6.4, 7.0), 'M8': (8.4, 10.0), 'M10': (10.5, 12.0),
         'M12': (13.0, 14.5), 'M16': (17.0, 18.5), 'M20': (21.0, 24.0)}  # ISO 273 fine..coarse
CBORE = {'M3': 6.5, 'M4': 8.0, 'M5': 10.0, 'M6': 11.0, 'M8': 15.0, 'M10': 18.0, 'M12': 20.0, 'M16': 26.0, 'M20': 33.0}
# EN 10029 hot-rolled plate thicknesses commonly stocked; EN 10219 RHS/SHS outer sections (h x b).
PLATE = [3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50]
RHS = {(40, 40), (50, 30), (50, 50), (60, 40), (60, 60), (70, 70), (80, 40), (80, 60), (80, 80), (90, 90), (100, 50),
       (100, 60), (100, 80), (100, 100), (120, 60), (120, 80), (120, 120), (140, 80), (140, 140), (150, 100), (150, 150),
       (160, 80), (160, 160), (180, 100), (180, 180), (200, 100), (200, 120), (200, 200), (250, 150), (250, 250), (300, 200)}
TOL = 0.05


def clearance_for(d):
    return next((m for m, (lo, hi) in CLEAR.items() if lo - TOL <= d <= hi + TOL), None)


def classify(d):
    for k, v in TAP.items():
        if abs(d - k) < TOL:
            return f'{v} tap drill'
    m = clearance_for(d)
    return f'{m} clearance' if m else None


def coaxial(a, b):
    off = (b['start'] - a['start'])
    return abs(abs(a['n'].dot(b['n'])) - 1) < 1e-6 and (off - a['n'] * off.dot(a['n'])).Length < 0.01


def holes(solid):
    """Full 360 degree internal cylinders, merged across OCC seam splits."""
    groups = {}
    for f in solid.Faces():
        if f.geomType() != 'CYLINDER':
            continue
        c = f._geomAdaptor().Cylinder()
        p, a = c.Location(), c.Axis().Direction()
        o, n = cq.Vector(p.X(), p.Y(), p.Z()), cq.Vector(a.X(), a.Y(), a.Z())
        ts = [(v.toTuple() and (cq.Vector(v.toTuple()) - o).dot(n)) for v in f.Vertices()]
        base = o + n * ((min(ts) + max(ts)) / 2)
        # Canonical key: axis point nearest origin, rounded.
        foot = base - n * base.dot(n)
        key = (round(c.Radius(), 3), *[round(abs(x), 2) for x in n.toTuple()], *[round(x, 1) for x in foot.toTuple()])
        u0, u1, _, _ = BRepTools.UVBounds_s(f.wrapped)
        g = groups.setdefault(key, {'r': c.Radius(), 'n': n, 'span': 0, 'pts': []})
        g['span'] += u1 - u0
        g['pts'] += [base + n * (t - (min(ts) + max(ts)) / 2) for t in ts]
    out = []
    for g in groups.values():
        if g['span'] < 2 * math.pi - 1e-6:
            continue  # fillet or partial arc, not a drilled hole
        ts = [p.dot(g['n']) for p in g['pts']]
        mid = g['pts'][0] + g['n'] * ((min(ts) + max(ts)) / 2 - ts[0])
        if solid.isInside(mid):
            continue  # boss or shaft, not a hole
        out.append({'d': 2 * g['r'], 'n': g['n'], 'start': g['pts'][0] + g['n'] * (min(ts) - ts[0]), 'len': max(ts) - min(ts)})
    return out


def blocked(h, others, depth):
    """Parts intersecting a drill/fastener corridor of hole diameter extending `depth` beyond each hole end."""
    hits = []
    for sign, origin in ((-1, h['start']), (1, h['start'] + h['n'] * h['len'])):
        d = h['n'] * sign
        probe = cq.Solid.makeCylinder(h['d'] / 2, depth, origin + d * 0.01, d)
        for name, s in others:
            if s.intersect(probe).Volume() > 1e-3:
                hits.append(name)
    return sorted(set(hits))


def stock(solid):
    bb = solid.BoundingBox()
    dims = sorted([bb.xlen, bb.ylen, bb.zlen])
    if abs(dims[1] - dims[2]) < TOL and any(f.geomType() == 'CYLINDER' and abs(2 * f._geomAdaptor().Cylinder().Radius() - dims[2]) < TOL
                                           for f in solid.Faces()):
        return f'turned from round bar >= Ø{dims[2]:.0f}+stock allowance, L={dims[0]:.1f}', True
    if dims[0] <= 50 and solid.Volume() > 0.4 * dims[0] * dims[1] * dims[2]:
        t = dims[0]
        ok = any(abs(t - p) < TOL for p in PLATE)
        return f'plate t={t:.1f}', ok
    sec = (round(dims[1]), round(dims[0]))
    if solid.Volume() < 0.5 * dims[0] * dims[1] * dims[2]:
        return f'hollow section {sec[0]}x{sec[1]} L={dims[2]:.0f}', sec in RHS
    return f'unclassified envelope {dims[0]:.0f}x{dims[1]:.0f}x{dims[2]:.0f}', None


def check(path):
    shape = cq.importers.importStep(str(path)).val()
    parts = [(f'solid_{i:02d}', s) for i, s in enumerate(shape.Solids())]
    report = {'file': Path(path).name, 'solids': len(parts), 'issues': [], 'parts': []}
    for name, s in parts:
        kind, ok = stock(s)
        row = {'part': name, 'stock': kind, 'stock_standard': ok, 'holes': []}
        if ok is False:
            report['issues'].append(f'{name}: non-standard stock ({kind})')
        others = [(n, o) for n, o in parts if n != name]
        hs = holes(s)
        for h in hs:
            c = h['start'] + h['n'] * (h['len'] / 2)
            inner = [o for o in hs if o['d'] < h['d'] and coaxial(h, o)]
            under_cbore = any(o['d'] > h['d'] and coaxial(h, o) for o in hs)
            m = clearance_for(h['d'])
            cls = f'{m} clearance' if under_cbore and m else classify(h['d'])
            if inner:  # larger coaxial bore over a clearance hole is a counterbore for that screw
                m = clearance_for(max(o['d'] for o in inner))
                cls = f'{m} counterbore' if m and abs(h['d'] - CBORE[m]) < TOL else None
                if m and cls is None:
                    cls = f'{m} counterbore Ø{h["d"]:.1f} != DIN 974-1 Ø{CBORE[m]}'
                    report['issues'].append(f'{name} Ø{h["d"]:.2f} at ({c.x:.1f},{c.y:.1f},{c.z:.1f}): {cls}; ISO 4762 head may bind')
            hit = blocked(h, others, depth=max(3 * h['d'], 25)) if h['d'] <= 22 else []
            row['holes'].append({'d_mm': round(h['d'], 3), 'center_mm': [round(x, 1) for x in c.toTuple()], 'class': cls, 'blocked_by': hit})
            where = f'{name} Ø{h["d"]:.2f} at ({c.x:.1f},{c.y:.1f},{c.z:.1f})'
            if h['d'] <= 22 and cls is None:
                report['issues'].append(f'{where}: not a standard tap-drill/clearance/counterbore size')
            if hit:
                report['issues'].append(f'{where}: drill exit/fastener access blocked by {", ".join(hit)}')
        report['parts'].append(row)
    report['pass'] = not report['issues']
    return report


if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = check(p)
        Path(p).with_name(Path(p).stem + '_dfm.json').write_text(json.dumps(r, indent=2))
        print(f"{r['file']}: {r['solids']} solids, {'PASS' if r['pass'] else 'FAIL'}")
        for i in r['issues']:
            print('  -', i)
