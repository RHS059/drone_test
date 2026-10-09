# C03 R01: four-corner steering development CAD

This original design adapts independent suspension to the six-wheel rover. Front and rear corners steer through spherical-joint uprights and connected tie links; the middle two corners retain C02 R06 fixed uprights. The reference vehicle photographs depict a four-wheel vehicle and provide no manufacturing dimensions.

## Current deliverables

- `interface_contract_C03_R01.json`: authoritative frames, handed parts, motion groups, limits and open gates.
- `original_steering_C03_R01.step`: 76 named original component groups in vehicle coordinates, millimetres.
- `original_steering_C03_R01.glb`: matching named meshes, metres, Z-up. No implicit root rotation.
- `original_steering_C03_R01_manifest.json`: node/motion-group mapping and CAD-derived mass properties.
- `kinematics_C03_R01.js`: executable handed closure solver. Its inputs are suspension angle, rack translation, side and front/rear sign. Wheel yaw is an output, not an independent animation control.
- `mass_cost_ledger_C03_R01.json` and `original_parts_C03_R01.csv`: original fabricated-part subtotal and purchased components whose mass/cost remain unknown.

The assembly contains four original corner mechanisms and two racks. Frame, body, wheels and fixed middle corners are supplied separately. Purchased drive internals, bearings, spacers, rod ends, actuators and dampers are not invented or counted as solid material. The restricted drive STEP/PDF and derived meshes are absent.

## Geometry and checks

Wheel centres are X = −1.35, 0, +1.35 m, Y = ±0.94 m, Z = −0.25 m. The source tire diameter is 876.3 mm. Published 317.5 mm section width was measured on a 10-inch rim; the selected 8.5-inch rim's actual section is unknown. A separate solid 340 mm-wide annular reservation is tested.

The new rack travels ±75 mm. Tie eye spacing is 310.367524 mm. Both tie pins use inclined axes and the 12-10HB interface. The nominal 200 mm industrial actuator has 25–175 mm extension over that travel. Its suitability for steering is unresolved.

Completed, bounded checks include:

- 29,161 analytical closure cases, no closure or catalogue angular-screen failures.
- 74 sampled upright, arm, pin and retainer Boolean checks, zero positive intersections.
- Rack, liner, clamp, fastener, body and frame checks at −75, 0 and +75 mm, zero positive intersections.
- 36 combined poses against the body/frame for both the original wheel CAD and the separate 340 mm tire reservation, zero positive intersections.
- Sampled tie/fork envelopes: minimum 6.637 mm at the inner rod-end housing reservation.
- Revised lever: 6.439 mm to the reserved tire and 8.747 mm to the moving lower arm in the tested samples.
- S01 static fixture compatibility at zero suspension/rack input: 88 checks of the 76 actual baked nodes plus 12 conservative reservations against 302 fixture solids, zero interference; closest conservative tie reservation gap 8.062 mm.

These are unloaded nominal-geometry results. They do not establish continuous swept clearance, tolerance/deflection margin, dynamics, structural strength, or safe operation. The current private-drive fit review is recorded separately in the contract when available.

## Mass and actuation

The four original steering corners and two racks total 238.204930 kg using the stated density assumptions. Including the two fixed middle corners gives 328.887508 kg of original running-gear material, 56.839774 kg above C02. This is not the complete vehicle mass. EVO nut weight metadata has unverified units and is excluded.

An illustrative 1500 kg, equal-wheel-load, friction-coefficient 0.6 screen produces 2.226 kN static rack force and 6.678 kN with the same friction model at 3g. It omits contact-patch torsion and losses. The 4.5 kN B045 actuator therefore remains a packaging candidate; its 25% duty and approximately 7.9-second rated-speed lock-to-lock time also need application review.

## Build and service gates

No fabrication or operation release is issued. Required work includes:

1. Finished bearing fits, spacers, preload, retainers, pins, thread classes, weld processes and fastener stacks.
2. Steering actuator force/speed/duty, sensing, endplay, fault response and stop-load qualification.
3. Exact coilover mounting drawing, spring selection, damping/thermal performance, reservoir routing and bump/rebound limits.
4. Adapter stud/nut/tool access and fatigue. The 30 mm adapter currently leaves zero nominal input-stud-tip stand-off to the rim pad.
5. Simultaneous wheel, bearing, braking and steering loads; structural deflection, buckling, fatigue and weld assessment.
6. Supported service sequence with stored spring energy controlled. S01 compatibility applies only at the neutral pose. The earlier long pin corridor intersects the installed tire; wheel-first or another accessible release sequence must be proven with the actual tools. No autonomous repair sequence is established.

## Reproduction

Use CadQuery 2.7.0 and the repository's original `generate_cad.py` helper. Frozen source generators include `generate_steering_corner.py`, `generate_spherical_housing.py`, `add_steering_lever.py`, `generate_rack_R11.py`, `generate_rack_mount_interfaces.py`, `generate_tie_link.py`, `generate_tie_pins.py`, `bake_rear_steering_parts.py` and `build_original_steering_assembly.py`. They depend on the stated original C02 source parts. Run the version-labelled test scripts and regenerate their reports after any dimensional change. Historical rejected revisions remain distinguishable by filename; never combine their tests with this checkpoint.
