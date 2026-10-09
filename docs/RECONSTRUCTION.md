# Six-wheel vehicle development model

This is a new source-backed reconstruction. The earlier missing local package and its historical audits have not been recovered.

## Current assembly

- Six original source-backed wheel models using published BFGoodrich KM3 MSPN 72204 and EVO Corse SE5240060141 dimensions. The file's C01 suffix is its component revision; it is not the earlier Warthog assembly configuration or its test evidence.
- Original faceted body, 175 CAD solids, eight removable service-cover groups, and separate battery/controller dimensional reservations.
- Original R07 lighter frame candidate, 386.953 kg at assumed steel density. Geometric validity, connected interfaces and machining-access checks do not establish structural strength.
- Original independent corner interfaces. Steering and suspension travel remain locked while geometry/hardware checks continue. Selected motor solids are excluded because their redistribution is restricted; no substitute shape is claimed as authentic motor CAD.
- Licensed UR20 and Robotiq source meshes and joint graphs; two independently adjustable arms and mimic-driven grippers.
- Separate executable MuJoCo gripper experiment. Newly reconstructed nominal/heavy cases pass the strict 10 mm screen; low-friction fails. This does not qualify vehicle manipulation or reuse lost experiment results.

## Verification boundaries

Original wheel native and delivered geometry checks passed. Body solids, export roundtrip, service-node names and R07/body exact intersections passed. Final corner geometry and complete browser rendering are checked separately against the final release revision. The prior frame-and-arms page was rendered successfully in Colab at desktop and mobile sizes; that is not evidence for this expanded assembly.

Nominal unloaded tire geometry is tangent to the flat ground plane. Loaded tire radius, terrain response, suspension dynamics, steering, braking, drive duty, battery integration, complete mass/CG and structural loads remain unresolved. Wheel and drive masses are unknown and are not silently treated as zero. Current documented corner hardware exceeds single-arm payload before the motor and wheel are added. Service-cover visualization is not executed repair; supported module removal requires rated external equipment and engineered lifting points.

## Reproduce bounded software checks

Run `node test-cad.mjs` for source FK, mimic joints, limits and robot source hashes. `node docs/contact/scripts/validate.mjs` reads saved contact results without rewriting them. Original CAD generators and source/dimensional assumptions accompany the assets. The historical `test-model.mjs` tests the legacy cost model only.

## Sources and permissions

UR graphical documentation retains its complete source terms and visible copyright notice. Robotiq, MuJoCo and Three.js retain their source-specific notices. Original body, frame, interface and source-backed wheel CAD are identified separately. Original tread and hidden rim/tire profiles are explicitly assumptions. The archived BSD Warthog assets are comparison references and are not loaded as the selected running gear. Restricted motor STEP/PDF, private review coupling STEP and user reference photographs are not distributed.

Buildability, autonomous peer assembly, self-repair and physical fabrication release remain open project goals.
