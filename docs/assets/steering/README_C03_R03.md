# Original rover steering C03 R03

This is an original six-wheel rover adaptation, with four steerable corners and two fixed middle corners. The selected assembly contains four upper R06 arms, four lower R04 arms, the unchanged handed carriers, and two R11 guided racks. The 76-node assembly excludes purchased drive internals, bearings, shocks and actuators. STEP units are millimetres; GLB units are metres, vehicle X forward, Y left, Z up.

## Current scope

The R03 contract and manifest select the current geometry. Earlier R01-named sources and reports in this package are retained dependencies and historical regression evidence. C03 R02 was rejected because upper R03 touched the tire. Intermediate upper R04 failed the 340 mm reservation; upper R05 touched a root clevis. R06 changes the original tube routes while retaining every joint center and the existing kinematic solver.

Normal display starts at suspension q = 0. After final export binding, an explicitly labeled unqualified motion-study mode may expose q within ±12° and racks within ±75 mm. Front and rear racks may be posed independently; workshop fixtures require suspension and both racks at zero. Sampled geometric clearance does not qualify loaded motion, ground contact, tire deformation, spring/damper behavior, structural strength or safe operation. Approximately 3 mm nominal local margins are unqualified for tolerances, weld distortion and deflection.

## Reproduction

Use Python 3.11, CadQuery 2.7.0, NumPy and SciPy from the normal package registry. Preserve this directory tree. Frozen geometry bytes and the public SHA256 whitelist are authoritative; new OpenCascade exports can differ in bytes.

From mechanical/running_gear_C03, the baseline generators retain their original output names. Generate baseline dependencies in the R01 sequence if needed, then run generate_upper_wishbone_R06.py and generate_lower_wishbone_R04.py, build_original_steering_assembly_R03.py, write_mass_ledger_C03_R03.py, and check_export_C03_R03.py. The selected contract is interface_contract_C03_R03.json. Its source builder deliberately starts with pending checks; finalize_contract_C03_R03.py binds the completed evidence after verification. The unchanged executable solver is kinematics_C03_R01.js. The final release evidence list identifies current tests; historical tests alone cannot establish R03 fit.

Changed-arm checks are under steering_optimization/travel_arm_U06_L04. They use the included original frame, body, wheel and fixture STEP files. Motor fit reports are numerical evidence from restricted vendor geometry; that geometry is deliberately absent, so those checks require separately authorized access to the exact source hash. No OEM CAD, PDF or derived mesh is in this archive.

## Remaining engineering gates

No fabrication, operation, lifting or autonomous repair release is granted. Open items include finished tolerances, bearing/spacer profiles and retention, weld process and fatigue, wheel stud/nut/tool stacks, drive bearing loads, steering force/speed/duty and fault behavior, shock/spring selection, tire size on the selected rim, loaded ground contact, and collision-free service access. The installed tire blocks the previously proposed long pin-withdrawal corridor; static fixture clearance is not a removal procedure.

The mass ledger is an original-CAD subtotal under stated density assumptions. Unknown purchased masses and prices remain null. The EVO nut's raw catalogue weight has no verified unit. Actuator comparison is a bounded sourcing study, not a changed or qualified hardware selection.
