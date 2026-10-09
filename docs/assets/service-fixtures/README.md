# S01 original static workshop fixtures

Engineering-development CAD, not fabrication released or safe to use. These original fixtures have no safe working load, proof test, material-grade approval, weld design or stability approval. They are not lifting equipment, commercially rated stands, an autonomous mechanism or manufacturer-approved accessories.

Current corner contract: C02_R05, retaining upright R04 and wheel adapter R02. Adapter R02 changes only pilot-hole size, so fixture placement is unchanged.

## What is actually modeled

- Two independent original transverse chassis trestles at X = −1775 and +1775 mm. Each has a plate-built hollow crossbeam, two vertical hollow posts, two floor plates and two rail-bearing saddles. The frame is not drilled, cut or welded.
- Four 160 × 220 × 16 mm saddle plates bear directly under the R07 200 × 100 × 6 main rails at Y = ±460, Z = −100 mm. Each spans the complete rail width. Actual contact is the rounded rail's 76 mm-wide bottom flat; local web/bottom-wall load transfer remains unqualified.
- Four screw-adjusted side locators per saddle provide an actual mount/registration mechanism. Gravity flows through the saddle into the trestle, not through locator friction. Locator screws must never be called lifting points or relied on to prevent uplift. The side bosses have smooth bores representing unresolved threaded manufacture; threads, screw locking, tip attachment, preload and rail wall crushing need design review.
- A separate floor-supported wheel-corner cradle uses two hollow contour-shoe weldments, replaceable nominal 6 mm elastomer liners, two longitudinal rails, two transverse rails and four feet. The shoes follow the selected tire's stated 438.15 mm unloaded radius. The tire model is original C01 reference geometry; fitted width, actual tread contact and compression are unknown.
- Four removable bolted capture-post weldments and two removable bolted crossbars form an enclosing cage around the tire. The posts must be removed during cradle insertion. The cage is not a rated restraint, lifting bail, tie-down or personnel guard. No hoist hooks, drive-housing contact geometry, wheels, casters or autonomous motion are invented.

STEP is millimetres. GLB is metres, Z-up, in rover C coordinates (X forward, Y left). The cradle is at the middle left wheel; apply a proper Rz(180°) rotation for the right side, then translate X to the desired station. Do not use negative scaling. Four-point chassis saddle centers form a 3550 × 920 mm rectangle. This does not demonstrate a stable vehicle in any arm pose.

## Deliberate service scene and height

The nominal C01 tire floor is Z = −688.15 mm. S01's illustrative floor is Z = −788.15 mm, representing a 100 mm raised chassis while the C02 links remain at q = 0. The chassis saddle underside is Z = −116 mm, therefore 672.15 mm above this floor. The trestles are purpose-dimensioned original CAD for that one pose; they do not telescope or lift. Each fixture must be positioned before receiving load. Other heights require engineering a different fixture; do not add loose packing.

ESCO 10498 is not assigned to this model. Its maximum 546 mm saddle height is below even the unraised saddle underside (572.15 mm), and its manual limits accessories/adapters to manufacturer-supplied ones and prohibits adding material for height. US Jack taller candidates do not automatically solve the configuration: their one-end matched-pair usage restriction must not be reinterpreted as approval for four stands under the full vehicle. No commercial load rating transfers to S01. At either end wheel station, the nearest cradle and trestle foot edges have only 5 mm nominal lateral separation. Placement tolerance, floor unevenness and loaded deflection must be checked; this is not a released workshop aisle or installation clearance.

The CAD-only assumed mass is about 97 kg per trestle and about 90 kg for the cradle (see the latest verification JSON for exact values). They are not hand-lift or UR20 payloads. A separate reviewed handling/positioning method is required before these fixtures can be deployed; none is claimed by this geometry.

## Load paths and remaining interfaces

Chassis: main rail bottom flat → saddle plate → transverse box → two vertical boxes → floor plates → qualified floor. Locator screw loads, local rail bending/crushing, column buckling, box torsion, eccentric loading, welds, base plate bending, foot contact, anchorage and overturning are unresolved.

Corner: tire tread → liner → curved shoe top/walls/base → transverse members → longitudinal members → floor plates → floor. The drive/upright hangs inboard from the wheel through existing joints, so the full module mass and CG must be measured and a tip/stability calculation performed. The original upright is deliberately not supported on guessed OEM drive housing surfaces. A future direct upright support should contact checked original non-bearing lands; S01 does not add one.

The CAD's two contact shoes and enclosing cage do not establish adequate module retention. Liner bonding/mechanical retention, tire condition/inflation, compressibility, proof loading, blocked-movement behavior, lateral capacity and floor anchorage remain gates. Ground contact is not automatically anchorage: foot holes are original unqualified patterns and no anchors are selected.

## Bounded C02 removal and inspection sequence

This is a proposed design sequence for review, not an executable approved workshop procedure. Do not proceed past a missing precondition.

1. Establish an approved vehicle isolation/lockout plan; isolate traction and arms, control brake release, chock the still-grounded wheels and identify stored energy. C02 connectors and the coilover are not selected, so those manufacturer procedures remain open.
2. Measure the entire vehicle and removable-module masses/CGs; calculate worst-case support reactions and all intermediate stability cases. Select and qualify actual lifting points, jack/hoist, sling/fixture, headroom and lift height. S01 supplies no lifting attachment; the current frame has no qualified lifting lugs. Initial raising is blocked until this is resolved.
3. With qualified equipment carrying the load under human supervision, position the two engineered trestles and the unloaded cradle at the selected corner. Remove the cradle's four capture-post weldments and two crossbars for insertion, leaving its floor frame/shoes assembled. The 100 mm raised q = 0 pose is illustrative; actual suspension droop and insertion clearance need checking. Seat all four chassis saddles and the corner support through a reviewed load-transfer process with load measurement. Do not assume equal stand reactions or four-way load sharing.
4. Install and inspect the cradle's four post weldments (eight base fasteners) and two crossbars (four upper fasteners). Establish independently qualified anti-tip/anti-rotation restraint for the actual corner, and check full module load/CG. Do not release a corner held solely by robot arms.
5. Positively support both wishbones in their retained chassis position and control all coilover/spring energy by the selected manufacturer's procedure. Those support devices are not in S01, and the planned C02 coilover is unselected: pin release remains blocked. The chassis rail clamps and their through-tie hardware remain installed.
6. After the preceding checks are released, isolate/disconnect the exact drive/brake/sensor connectors and remove the retention devices for the two outer X-axis upright pins. Final pin retention is not designed in C02. An original Ø28 mm extraction corridor from X −260 to +260 mm is screened against S01, but an actual puller/hand/tool approach is not selected. Withdraw the two outer pins only while the external workholding carries the corner and both links remain positively supported. Do not remove inner pivot or rail-clamp bolts.
7. The C02 service boundary is wheel + adapter + drive + upright. Wishbones, stationary rail clamps and planned coilover remain on the chassis. Keep the detached module supported in the stationary cradle for inspection. Moving it away, lifting it or rolling it requires a separately engineered transport/lifting attachment and sequence; S01 deliberately does not animate or assert that operation.
8. Reassembly requires qualified pin/bearing retention, hardware grade/engagement/torque, connector/brake checks, witness inspection and controlled transfer back onto tires. No numeric tightening torque is invented.

This sequence is C02-specific. A future steering tie rod/actuator adds another connection and cannot inherit this removal boundary without revision. Current fixed UR20 bases cannot reach the rear wheel station (2.25 m longitudinal separation exceeds 1.75 m nominal reach); rear service is human-assisted. Reachability and payload/moment limits still need verification for every proposed arm operation at other stations. Tools, coupling, gripper and workpiece all count. Two robot payload ratings cannot simply be added.

## Files and reproduction

- `chassis_trestles_S01.step/.glb`: the two original chassis fixtures
- `corner_cradle_S01.step/.glb`: one original cradle, left-middle C02 pose
- `service_fixtures_S01.glb`: both groups together; reference vehicle not bundled
- `build_fixtures.py`, `parameters.json`: editable source and explicit parameters
- `verify_interfaces.py`, `interface_verification_S01.json`: file-level nominal geometry screens against R07 frame, original R01 body, original C01 wheels and original C02 interfaces
- Per-group verification JSON and `parts_S01.csv`: solid counts, assumed CAD-only masses, contacts and interference reports
- `service_interface_contract_S01.json`: placement, grouping and blocked operations
- `SOURCES.json`: official equipment source references, no downloaded private source files

Run `python build_fixtures.py` with CadQuery 2.7 and numpy, then `python verify_interfaces.py` alongside the declared original reference packages. The generator imports no private motor CAD. Public outputs contain only these original fixture solids, source code, numerical checks and documentation. Geometric testing must not be reported as load qualification.
