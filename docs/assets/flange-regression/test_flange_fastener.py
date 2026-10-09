from check_flange_fastener import evaluate
assert evaluate(16,11.5)['nominal_protrusion_mm']==4.5
assert evaluate(18,11.5)['nominal_screen_pass']
assert evaluate(18.5,11.5)['manufacturer_maximum_screen_pass']
assert not evaluate(19,11.5)['manufacturer_maximum_screen_pass']
assert not evaluate(20,11.5)['nominal_screen_pass']
assert not evaluate(14,11.5)['project_minimum_screen_pass']
# Example adverse tolerances can invalidate the otherwise passing18mm candidate.
assert not evaluate(18+.5,11.5-.2)['manufacturer_maximum_screen_pass']
for v in [float('nan'),float('inf'),-1,0]:
    try: evaluate(v,11.5)
    except ValueError: pass
    else: raise AssertionError(v)
print('PASS: nominal screw-length and adverse-tolerance regression; minimum engagement remains unverified.')
