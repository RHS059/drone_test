# Six-wheel vehicle development model

This is a new source-backed reconstruction. The earlier missing local package and its historical audits have not been recovered.

## Current assembly

- Six original source-backed wheel models using published BFGoodrich KM3 MSPN 72204 and EVO Corse SE5240060141 dimensions. The file's C01 suffix is its component revision; it is not the earlier Warthog assembly configuration or its test evidence.
- Original faceted body, 175 CAD solids, eight removable service-cover groups, and separate battery/controller dimensional reservations.
- Original R07 lighter frame candidate, 386.953 kg at assumed steel density. Geometric validity, connected interfaces and machining-access checks do not establish structural strength.
- Original C03_R03 front/rear steering corners, physical guided racks, handed levers and tie rods, with two C02_R06 middle corners. The 76-node original steering assembly contains 202 valid B-rep solids. Rack sliders inspect linkage geometry. Optional unloaded motion study moves the four steering corners through ±12°; the middle pair stays fixed. The chassis is held 200 mm above its nominal display reference, with no lifting or ground-contact simulation. Actuator force/duty, purchased joints and actual driving remain unqualified. Selected motor solids are excluded because their redistribution is restricted; no substitute shape is claimed as authentic motor CAD.
- Licensed UR20 and Robotiq source meshes and joint graphs; two independently adjustable arms and mimic-driven grippers.
- Separate executable MuJoCo gripper experiment. Newly reconstructed nominal/heavy cases pass the strict 10 mm screen; low-friction fails. This does not qualify vehicle manipulation or reuse lost experiment results.

## Costs and workshop inspection

The main page includes dated native-currency public-price subsets, explicit missing quotes, a matched mass/BOM disclosure and editable operating-cost assumptions. Complete build cost, measured hourly cost and whole-vehicle runtime remain unknown. Prices are not supplier quotations or destination totals. Battery procurement requires serial-specific recall screening; coupling electrical routes and arm/controller bundle scope are kept separate.

An optional workshop study displays two original chassis trestles and a corner cradle at a static100mm-raised vehicle pose. The supports have no assigned load rating. No lifting animation, unsupported module removal, pin-release operation or autonomous repair is implied. Both wishbones, spring energy, module retention, floor reactions and lifting setup still need an engineered procedure. The service view's wireframe drive volumes are numerical space reservations, not motor CAD.

## Verification boundaries

Original wheel native and delivered geometry checks passed. Body solids, export roundtrip, service-node names and R07/body exact intersections passed. Final corner geometry and complete browser rendering are checked separately against the final release revision. The prior frame-and-arms page was rendered successfully in Colab at desktop and mobile sizes; that is not evidence for this expanded assembly.

Nominal unloaded tire geometry is tangent to the flat ground plane. Loaded tire radius, terrain response, suspension dynamics, steering actuation, braking, drive duty, battery integration, complete mass/CG and structural loads remain unresolved. Selected EVO rim net mass is 15.1 kg each from the exact-SKU manufacturer API; tire, nut and drive masses are unknown and are not silently treated as zero. Current documented corner hardware exceeds single-arm payload before the motor and wheel are added. Service-cover visualization is not executed repair; supported module removal requires rated external equipment and engineered lifting points.

## Corrected geometry and preserved failures

Earlier C03_R01 geometry passed its 12 neutral-suspension motor cases but failed 14 of 36 combined steering/travel cases. The original failure witnesses are preserved. Intermediate upper-arm candidates also failed tire or root-clamp checks and were not selected.

Selected C03_R03 uses upper R06 and lower R04. Its original-part checks cover 36 combined poses, 592 environment results, 60 root groups, 100 handed-clamp samples and 88 neutral workshop checks. Export binding independently verifies all 76 nodes and 202 solids. The scoped motor fit passes 36 sampled cases by composition with hash-bound revised-arm evidence. A separate nominal motor-to-original-rim/tire check passes, with rigid transform equivalence over those poses; native rotor phase, assumed wheel geometry, output clocking and physical fit limitations remain explicit. See [the complete numeric evidence and source package](assets/steering/index.html).

These passes do not establish continuous swept clearance. Local nominal margins are about 3 mm and remain unqualified for tolerances, welding distortion, mud, tire variation and elastic deflection. Purchased bearing/actuator/shock bodies, fastener stack and loads remain separate gates. The optional motion mode is a free-space kinematic inspection. It does not simulate wheel support, loaded tire radius, springs, terrain, vehicle movement or physical operation. Workshop mode forces neutral suspension and centered racks; Home exits the free-space study.

## Steering geometry checks

Independent source analysis checked 5,608 poses, including 36 boundary fixtures and 4,096 seeded random poses. Maximum steering disagreement was 6.72e-15 rad and tie closure residual 1.67e-15 m. All 76 baked nodes and 216 transformed exported-axis checks passed. Runtime tests separately compare the actual pivot-compensated wheel/tie matrices with those fixtures, check Home/rack state and reject invalid inputs. These are kinematic/export checks, not force, continuous collision or physical qualification.

The original public source archive is distributed as three independent ZIPs extracted into the same folder; its 215 files match the full archived package byte-for-byte. The runtime GLB is gzip-compressed without mesh simplification or quantization and expands to the exact original 42,252,148-byte geometry. See [steering source files](assets/steering/index.html).

## Reproduce bounded software checks

Run `node test-motion-study.mjs` for actual rover-mode and workshop/Home interlocks; `node test-steering.mjs` for exact geometry transport, closure fixtures and actual motion-binding checks; `node test-controls-ready.mjs` for loading/error/control interlocks; `node test-costs.mjs` for currency, unknown-value and scenario arithmetic; `node test-rover.mjs` for nominal scene/fixture interfaces; `node test-cad.mjs` for source FK, mimic joints, limits and robot source hashes. `node docs/contact/scripts/validate.mjs` reads saved contact results without rewriting them. Original CAD generators and source/dimensional assumptions accompany the assets. The historical `test-model.mjs` tests the legacy cost model only.

## Sources and permissions

UR graphical documentation retains its complete source terms and visible copyright notice. Robotiq, MuJoCo and Three.js retain their source-specific notices. Original body, frame, interface and source-backed wheel CAD are identified separately. Original tread and hidden rim/tire profiles are explicitly assumptions. The archived BSD Warthog assets are comparison references and are not loaded as the selected running gear. Restricted motor STEP/PDF, private review coupling STEP and user reference photographs are not distributed.

Buildability, autonomous peer assembly, self-repair and physical fabrication release remain open project goals.
