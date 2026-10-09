# Independent C03 geometry / forward-kinematics audit

Result: PASS for the frozen original source and the specified pivot-compensated transform scheme. No source FK or proposed transform defect found. This does not verify that a particular viewer implementation actually applies those transforms.

## Evidence

- 5,608 poses: 36 boundary-grid cases (all four corners, q = −12/0/+12 degrees, rack = −75/0/+75 mm); 4,096 seeded bounded random poses; 964 zero-rack suspension cases; 512 mirror cases.
- Steering checked by independent contract-coordinate reconstruction and bracketed Brent root-finding of the Euclidean tie-length residual across a complete turn. The source analytic formula is not reproduced. Select the closure branch nearest neutral.
- Maximum source/reference steering disagreement: 6.72e−15 rad. Maximum tie closure error: 1.67e−15 m. Zero-rack bump steer: at most 8.89e−16 rad.
- Fore/aft coordinates reflect in X with opposite steering. Left/right coordinates reflect in Y when rack translation also reverses. Exact agreement in checked reflection cases. Actuator Y layout is intentionally asymmetric and shared by both corners, so it is excluded from the L/R position-reflection assertion.
- Wheel center = kingpin + 0.128 m × wheel axis, with maximum 1.25e−16 m error. Upper/lower arm-joint spacing remains vertical within 1.25e−16 m. Wheel and tie-pin axes remain unit length.
- Maximum sampled steering magnitude: 21.4670183183 degrees at q = −12 degrees and rack = −75 mm for front-left (mirrored equivalents also exist). Nearest competing root has an absolute-angle-selection margin of at least 0.29507 rad in checked samples.
- All 45 source guard checks pass: finite numeric inputs, nonnumeric rejection, exact limits, out-of-domain rejection, documented 1e−10 numerical boundary allowance, valid side/fore signs, and defaults.
- GLB: 76 unique named root nodes; exact 1:1 manifest mapping; no node transforms; metres, Vehicle C Z-up; vertices already baked in world coordinates.
- GLB integrated-triangle volume properties agree with CAD manifest centroids to 4.70e−6 m and volumes to 0.04475%. These are tessellation comparisons, not mechanical tolerances.
- 216 transformed GLB wheel-adapter, tie-pin and tie-tube/insert axis checks pass. Maximum geometric-axis error is 4.37e−5 degrees; centroid-to-expected-axis distance is at most 7.51e−8 m. Axis extraction uses integrated tetrahedral volume covariance to avoid bias from uneven vertex sampling.

## Required integration transforms

For a baked world-coordinate vertex x, do not add native station/side transforms again.

- Upper/lower arm: P + Rx(side × q) × (x − P), using its own fixed pivot P.
- Upright/outer pins/wheel adapter: suspensionDelta + K0 + Rz(steerRad) × (x − K0).
- Tie tube/inserts: currentInner + Ralign(nominalOuter − nominalInner, currentOuter − currentInner) × (x − nominalInner).
- Rack and inner tie pins: x + [0, rack, 0]. Fixed rack groups do not move.
- Upper/lower retainers follow their arms, not steering yaw.
- Wheel spin is applied about the resulting current wheel axle after steering/suspension. The adapter/wheel is not scaled.
- Front/rear receive the same signed global-Y rack input to obtain opposite rear steering. Do not negate the rear rack a second time.
- Side already appears in armWorldRx and in returned world axes. Do not multiply returned steerRad or axes by side/fore again.
- Middle C02 corners remain fixed-steer; they are absent from the C03 GLB.

## Files and reproduction

- boundary_fixtures_C03_R01.json: 36 independent boundary poses with all expected FK fields and closure diagnostics.
- random_fixtures_C03_R01.json: 4,096 independent seeded bounded poses.
- independent_fixtures_C03_R01.json: combined 4,132-fixture set.
- audit_summary.json: numeric comparisons, source SHA-256 fingerprints and 45 guard results.
- glb_alignment_audit.json: all 76 node/bounds/mass comparisons and 216 transformed axis checks.
- audit_c03.py and run_source.mjs: reproducible independent FK and source-runtime comparison.
- audit_glb.py: reproducible direct GLB geometry and transform comparison.

Run python audit_c03.py, then python audit_glb.py. Both are read-only against the frozen C03 source and write only in this audit directory. Python dependencies: NumPy and SciPy. The source solver is executed by Node.js without editing or copying its formula.

## Scope limits

This is geometric/FK verification only. It is not continuous collision clearance, physical qualification, motor/load/actuator sizing, dynamics, strength, fatigue, fabrication, or service approval. Private OEM source is excluded. It does not replace application-level runtime tests, tests of wheel-spin behavior, or checks of separately loaded wheel/C02/frame/body models.
