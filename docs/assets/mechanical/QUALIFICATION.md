# Six-Wheel Builder original CAD: new frame R06 / adapter R03

This package contains newly constructed parametric B-rep geometry. Prior R04 frame and adapter source bytes were unavailable. R06 additionally corrects the initial R05 mounting-hole phase from30° to0° relative the manufacturer drawing +X. No historical test result, old mass, or claim of byte-for-byte recovery carries forward. The STEP and GLB files represent the same newly modeled original parts. No proprietary robot, gripper, or Robotiq coupling CAD is included.

## Status

**ENGINEERING DEVELOPMENT; NOT FABRICATION RELEASED.** These are editable solid CAD parts, not illustrative blocks. Nevertheless, manufacturing, mounting, and safety-critical structural details below remain unresolved. Passing geometric checks is not evidence of structural capacity or safe operation.

## Frame R06

- Vehicle coordinates: X forward, Y left, Z up. Overall 4000 × 1020 × 230 mm, bounds X −2000..2000, Y −510..510, Z −100..130.
- 18 separate solids: 2 longitudinal hollow RHS rails; 8 transverse hollow RHS members; 2 drilled arm plates; 6 triangular gussets.
- Main and transverse members: nominal RHS 200 high × 100 wide × 10 wall. Outside corner radius 20 and inside radius 10 mm are explicit NEW design assumptions, requiring stock-supplier confirmation.
- Transverse blanks extend to Y ±430 before being coped to the complete rounded outer envelopes of the main rails. Material does not intrude into the rail cavities. This provides coincident mating surfaces in nominal CAD with no deliberate weld root gap. A fabricator must specify edge prep and actual weld root gaps.
- Crossmember centers X = −1950, −1200, −400, 750, 1050, 1300, 1650, 1950 mm. This layout is NEW; it is not asserted to match old R04.
- Arm decks: 400 × 400 × 30 mm at (900, ±300), top Z130. Six Ø8.5 through pilot holes per plate on Ø210 PCD, phase0° from the drawing +X axis. These are M10×1.5 tap-drill pilots, not finished threads and not the robot base's Ø10.5 clearance holes.
- Main rail/deck/crossmember placement is a nominal weldment contact design. Weld beads, consumables, fasteners, coatings, machining allowances, cables, modules and wheel assemblies are excluded from reported CAD mass.
- Steel density 7850 kg/m³ is assumed. Steel grade, allowable stress, toughness, corrosion strategy and weldability are NOT selected. Mass/inertia are recomputed from R06 solid volume; the old 559.4416875 kg value is not used.

## Arm mounting verification

UR20 base footprint Ø245 mm; six M10 mount fasteners on Ø210 PCD; robot base holes Ø10.5. Required mounting-plane flatness 0.05 mm. The 5±1 mm drawing dimension is locating-pin protrusion, NOT mounting-plate thickness. Manufacturer locating-pin centers in the drawing are (−95,−10) and (+95,−10) mm, spacing190 mm. The drawing 30° arc is measured from +Y, corresponding to M10 phase0° from +X. Drawing page axes are not automatically robot software base axes; the visual registration remains a separate check. Pin seats are not fabricated by this model. Complete finished M10 thread engagement, bolts, dowel fits/retention, post-weld stress relief and machining sequence require engineering review.

Manufacturer references (retrieved 2026-10-09):
- https://www.universal-robots.com/manuals/EN/PDF/SW5_24/user-manual-UR20-PDF_online/718-818-00_UR20_User_Manual_en_Global.pdf , assembly and mounting drawing.
- https://www.universal-robots.com/media/1824603/ur20_data_sheet.pdf , one-page technical specification. Native tool flange ISO9409-1-80-6-M8; Ø50 H7 female recess, Ø100 h8 outer flange, Ø80 pitch circle, Ø8 H7 index, 6.20 recess depth. Drawing orientation must be reconciled to software tool0.

## Original adapter R03

A NEW steel adapter concept: Ø100 body, seating faces Z0 and Z23.5, nominal Ø50 UR-facing pilot Z−2.5..0, total envelope26 mm. The pilot is on the robot side, not the coupling side. Male pilot manufacturing fit is deliberately NOT inferred from the female H7 callout. Nominal geometry must not be treated as a toleranced fit.

Six proposed Ø8.5 M8 clearance bores at Ø80 PCD, angles0,60,...300°. Proposed Ø14 counterbores depth12 from the coupling side leave11.5 mm nominal underhead material. These clearances/counterbores are original design choices, not UR specifications. Screw head, length, engagement and assembly access remain unapproved. Install UR mounting screws before the coupling; coupling Ø75 envelope covers part of the access region. A conservative nominal Ø13×8 mm M8 head envelope clears the adapter and skirt, but does not approve a fastener or installation torque.

R03 corrects an interference identified during fresh source review: the coupling has an outer annular skirt, R31.5..37.5, projecting3 mm below its central robot-contact plane. The adapter therefore has a NEW nonlocating annular relief R31..38, depth3.5 from Z23.5 (floorZ20). The skirt bottom sitsZ20.5, giving0.5 mm nominal radial/axial clearance. These are custom clearance choices, not manufacturer fits. The 12 mm-deep M8 counterbores put nominal8 mm heads atZ19.5, 1 mm below skirt bottom. R02's9 mm counterbores and unrelieved flat face were superseded because they clashed. R02 is not a released deliverable.

Four Ø5 blind tap-drill pilots, depth12, at Ø50 PCD and45,135,225,315°, intended M6×1. Threads, drill tip geometry, lead-in/chamfers and effective engagement are not modeled/released. Index pin seats are deferred. Official coupling STEP confirms nominal Ø6 index location (0,+25), but cannot establish a manufacturing fit or sufficient blind depth by itself. UR index at (0,+40) must also be reconciled with the retained tool0→adapter Rz(pi) convention.

The mandatory GRP-CPL-062 is a separate purchased electronics-containing Robotiq coupling. It cannot be replaced by this adapter. Its official overall axial envelope is16.9 mm. The +11 mm coupling→gripper transform is verified in the licensed Robotiq 2F85 coupling URDF; it is a reference-frame convention, NOT physical coupling thickness. Its Ø71 F8 /2.9 deep recess faces the gripper; it is NOT an adapter-side locating pilot.

Sources:
- https://blog.robotiq.com/hubfs/support-files/2F-85_2F-140_General_PDF_20210623.pdf , page68 Fig5-6: coupling Ø75 outside,16.9 total,4×Ø6.4 clearance on Ø50 PCD, Ø11.4 counterbores depth7.5.
- https://assets.robotiq.com/website-assets/support_documents/document/GRP-CPL-062_20190819.STEP , inspected only to confirm nominal index position; proprietary file NOT redistributed.
- https://assets.robotiq.com/website-assets/support_documents/document/online/2F-85_2F-140_Instruction_Manual_Gen_HTML_20190524.zip/2F-85_2F-140_Instruction_Manual_Gen_HTML/Content/6.%20Specifications.htm , mandatory coupling electronics and ISO50-4-M6 interface.

## Required release gates

1. Independent design review: material/stock radii, dimensions/tolerances, bolt/index orientation, fits and thread engagement; purchasing traceability.
2. Structural calculations/FEA and test covering arm manufacturer reaction envelope, emergency stops, dynamic amplification, torsional loads, obstacle/impact loads, wheel/suspension loads, asymmetric dual-arm poses, fatigue and local deck/rail-wall behavior. No such checks passed in this reconstruction.
3. Weld design, access and procedure qualification; distortion/stress relief and post-weld machining to arm-plane flatness0.05 mm. Nominal coincident faces are not a weld procedure.
4. Vehicle stability/tip-over, braking, payload and human-safety risk assessment; electrical, control and e-stop integration.
5. Full actual-purchased-part interference and assembly-tool access checks over moving arm/gripper/wheel ranges. Pairwise frame checks do not cover vendor parts, fasteners, wires or swept volumes.
6. Adapter proof/loading review, approved fits, dowel seats, drill-tip/chamfer details, screw selection and tool payload/inertia settings. Full vendor part and tool0 reference-frame reconciliation.

## Reproduction

Python3 with CadQuery2.7/OCP and numpy: run `python generate_cad.py`. STEP uses mm. GLB vertices explicitly use metres and Z-up (no implicit axis rotation); viewers must apply their own declared axis mapping. Named nodes correspond to CAD solids. Verification JSON reports fresh volume, mass, center of mass, central inertia matrix and pairwise contacts/intersections. Inertia units are kg·m² about assembly/part center of mass in the stated axes. Geometric tests use ideal nominal surfaces; they do not verify manufacturing tolerances or strength.
