"""Known-answer test for dfm_check.py: one clean part, one with each defect class. Run: python test_dfm.py"""
import tempfile
from pathlib import Path
import cadquery as cq
from dfm_check import check


def step(parts, path):
    a = cq.Assembly()
    for i, p in enumerate(parts):
        a.add(p, name=f'p{i}')
    a.export(str(path))
    return check(path)


d = Path(tempfile.mkdtemp())
plate = lambda t: cq.Workplane('XY').box(100, 100, t)
good = plate(10).faces('>Z').workplane().pushPoints([(-25, 0)]).cboreHole(9.0, 15.0, 9).faces('>Z').workplane().pushPoints([(25, 0)]).hole(6.8)
r = step([good], d / 'good.step')
assert r['pass'], r['issues']
holes = {h['class'] for h in r['parts'][0]['holes']}
assert holes == {'M8 clearance', 'M8 counterbore', 'M8 tap drill'}, holes

bad = plate(7).faces('>Z').workplane().pushPoints([(-25, 0)]).cboreHole(9.0, 14.0, 4).faces('>Z').workplane().pushPoints([(25, 0)]).hole(7.3)
blocker = cq.Workplane('XY').box(30, 30, 10).translate((25, 0, -10))  # under the Ø7.3 hole exit
r = step([bad, blocker], d / 'bad.step')
text = '\n'.join(r['issues'])
for expect in ['non-standard stock (plate t=7.0)', 'Ø7.30', 'not a standard', 'counterbore Ø14.0 != DIN 974-1 Ø15.0', 'blocked by solid_01']:
    assert expect in text, (expect, text)
print('PASS: dfm_check known-answer tests (stock, hole size, counterbore, blocked drill exit)')
