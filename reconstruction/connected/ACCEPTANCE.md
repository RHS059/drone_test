# Connected drivetrain release acceptance

This revision must replace absent hardware with source-backed parts and explicit interfaces, rather than infer connections from kinematic motion.

## Mechanical evidence required

For each of six corners, identify the ordered torque/load path: wheel rim, correctly seated wheel fasteners, direct wheel pilot, motor output flange/studs (no adapter in the selected C04 direct-drive candidate), motor bearings/housing and fixed mounting flange/fasteners, upright, spherical or pivot joints, wishbones, chassis pivots/clamps and frame. For four steering corners also identify rack actuator mount, actuator eye and pin, rod/carriage connection, rack guides, inner rod-end ball/spacers/pin, threaded tie tube/insert/jam nuts, outer rod-end and upright lever. Include spring/damper eye hardware and attachments at both ends.

Each interface record must have component IDs, source-backed mating datum/axis, rendered node names, local mating anchor transforms, joint type and permitted movement, exact source or original drawing, retention method and unresolved tolerances. A merely coincident center is insufficient to establish a retained joint. Distinguish physical purchased component models from original designs and dimensional assumptions.

Across the displayed motion domain, verify actual rendered transforms of all connected hardware: bearing ball vs housing, rod-end bodies vs tie rods, spacer/pin axes, actuator endpoint/length closure, shock endpoints and wheel/motor/coaxial flange transforms. Record sampled angular misalignment, engagement/retention limits and tested geometry. Do not substitute snapshot arithmetic for actual scene-matrix checks.

## Electrical evidence required

Every powered component must trace to a source through actual compatible drive/control hardware and protected conductors, including return paths. Identify each motor's winding/type, feedback and brake interface; selected controller compatibility; battery configuration/BMS; branch protection, isolation, contactors and precharge; regeneration handling; arm power input; steering power/control; auxiliary supply; communications and emergency-stop architecture. Unknown supplier interfaces remain explicit blockers, not invented terminals.

Use manufacturer ratings with their duty, temperature, phase-vs-bus-current and configuration conditions. Provide source-backed enclosure/mounting/connector geometry and conductor endpoint data. Visual cables must terminate on named terminals/connectors and follow moving parts with documented bend/slack allowances. Routing appearance does not establish cable ampacity, fault interruption, EMC, thermal performance or functional safety.

## Visual QA

Close views with body visible and removed must show all six wheel-to-drive paths and every steering/suspension connection. Highlight by component identity, never obscure omissions with wireframe reservations. Inspect neutral and combined motion extrema. Missing purchased profiles may use accurately dimensioned original interface models only when the modeled dimensions and assumptions are explicit; do not derive public geometry from restricted vendor CAD.

## Completion boundary

A model with attached solids and continuity tests is a connected engineering design, not a fabrication release. Do not call it buildable while specific mounting, hardware stack, controller compatibility, load support or electrical protection requirements remain unresolved. Preserve prior failed configurations and qualification limits.

Current viewer motion scope: front/rear four-corner suspension and independent racks. The middle pair remains fixed at neutral; wheel-spin binding can be studied on all six. This does not establish middle suspension travel clearance.
