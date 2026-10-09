# Body/power R01: original engineering CAD

This package replaces an exposed ladder-only appearance with functional compartment geometry. It is a manufacturing-development assembly, not fabrication-released, electrically qualified, weatherproof, crash-rated or ready to operate.

## Coordinate and source contract

All original construction is parametric CadQuery B-rep in millimetres, frame C: X forward, Y left, Z up. GLB vertex positions are metres and Z-up; no root correction rotation is required. Mount origins remain the R06 frame origins. Geometry is not stretched to match photographs.

- `body_power_R01.step` / `.glb`: original sheet parts, rail straps, stiffeners, hatches, gaskets, hardware approximations and cable troughs. No purchased electronics are disguised as detailed CAD.
- `cots_reservations_R01.step` / `.glb`: six explicitly named DIMENSION_ONLY cuboids: four RELiON batteries and two UR OEM DC controllers. Load only as a separate optional translucent packaging layer.
- `build_body_power.py`: reproducible source. `python build_body_power.py` rebuilds and verifies. CadQuery 2.7 and NumPy are required.
- `verification.json`: current solid validity, actual bounds, geometric mass/CG assumptions and intersections. Frame, arms, wheels and drive masses are excluded.
- `original_cutlist.csv`: one row per original part. This is a finished-geometry list, not a released flat-pattern/nesting set.
- `sourced_bom.csv`, `SOURCES.json`: primary-source identity, dimensions, mass and limitations. No purchase or vendor approval is claimed.

## Mechanically useful features

The recessed battery well sits between the existing X −1200 and −400 crossmembers, inside the rails. Four upright 260×180×276 mm reservations rest on 4 mm isolator pads; the reserved bank weighs 62.4 kg. Its original aluminium floor/walls, low stops and top crossbar provisions are explicit solids. Terminal positions and a validated hold-down contact interface remain unknown; the bars have a 12 mm nominal clearance and must not be represented as a completed restraint design.

The rear bay has two distinct elevated controller mounting trays with actual adapter slots, free connector/air volume and removable top access. The middle bay is retained as tool/payload volume. The forward compartment uses a real planar sloping nose and removable hatch. No weapon, targeting system or weapon mounting interface is included.

The outer body has separate 3 mm panels, shaped transverse bulkheads, sloping shoulder plates, four side inspection panels, top hatch joints with gasket solids, M6 clearance holes/nutplate provisions, simplified socket-head screws, cable troughs and actual connector/vent apertures. The top remains segmented for access. Rails are attached using wrap-around strap-clamp provisions, with no undisclosed new holes in the inherited frame. Fastener threads, bolt preload, rivet-nut choice, weld details, bend allowance, insulation and bonding still need engineering release.

The broad upper-hull span is a design choice suggested by non-dimensional reference-image cues. Its underside respects the current provisional suspension reservation; that does not establish swept-envelope clearance. The lower body has explicit cutouts for the current station-centred wishbone clamp reservation, at X −1350, 0 and +1350 mm. Do not use the superseded trailing-arm relief positions.

## Service and access

The battery hatch removes vertically; all four battery envelopes can then lift vertically with restraints removed. The controller bay is top-accessible; full connector extraction and fan service remain to be validated against acquired supplier CAD. Side inspection panels are supplemental, not battery-extraction doors. Front and middle tool hatches are separate from arm mounting plates. The arm bases at X900, Y±300, Z130 mm retain their existing bolt patterns; arm-link clearances must be checked in the actual default and motion poses.

Finger slots and ventilation openings are intentionally open geometry. The concept gaskets do not confer IP protection: sealed handles, fans/filters, drains, glands, cable penetrations and full thermal/environmental qualification are outstanding. The design must not be sold or described as a sealed battery enclosure or a certified safety system.

## Power architecture limits

The four proposed batteries provide 6.144 kWh nominal arithmetic energy, not usable energy or range. Their individual ratings do not imply system current capability. The UR source lists OEM DC input 19–72 VDC, up to 400 A inrush and 350 W control-unit heat per UR20. Two controllers require verified precharge/soft-start, fuse coordination and thermal design; nominal voltage overlap is insufficient. Standard UR control boxes require AC and are not equivalent to these provisional OEM DC reservations.

At a hypothetical 15 K air rise, removing the 700 W combined controller heat bound would require roughly 0.039 m³/s ideal airflow using assumed air density 1.2 kg/m³ and heat capacity 1005 J/(kg K). This calculation excludes pressure losses, ambient extremes, drive losses, battery heat and fan derating. It is a sizing warning, not fan selection or a cooling-performance claim. Current small vent slots alone are not qualified to deliver this flow.

Traction motors/controllers, regeneration, contactors, fuse ratings, BMS coordination, charger, emergency stop architecture, functional safety and grounding are all unresolved. No WD220 proprietary/restricted CAD is part of this package. No electrical connections are portrayed as a qualified system.

## Verification meaning

Mass is computed from CAD volume using stated nominal densities. Battery/controller masses come from manufacturer data; their CGs are placed at envelope centres as assumptions. This does not validate full-vehicle CG, tip stability, axle loads, braking or manipulator reaction loads. Frame mass and structure remain a separate package and may be redesigned. Pairwise positive-volume checks are CAD interference checks, not strength, safety or manufacturability certification.

The original bumper tubes are open-ended hollow-section geometry with separate caps. They are unqualified guards, not towing/recovery points or impact-rated bumpers. No recovery rating is invented.

## Traction candidate and optional second bay

The WD220 drawing lists47A within the motor block, without explicitly defining DC-bus input current. Six such ratings sum282A arithmetically; that is not verified battery demand. Inverter current/efficiency data are needed. A separate power check is possible: if six drives simultaneously deliver2.2kW mechanical output each,13.2kW/51.2V requires257.8A even at ideal100% efficiency, before arms/auxiliaries. Actual input would be higher. This exceeds the four batteries'180A summed individual recommended discharge, but does not by itself exceed the400A sum of individual maxima; neither sum is a qualified pack rating. The motor duty is S2 for60minutes, not continuous. Drive price and exact mass are unquoted/unknown. No motor/controller/battery compatibility is claimed. Controller heat is used for cooling sizing only and is not added again as independent electrical input power.

A separately recessed optional four-unit bay is geometrically possible within the R06 opening between crossmembers X−400 and+750mm, provisionally at X[−300,+350],Y±360,Z[−80,+337]mm. It is not modeled or included in mass/capacity. The present tool-bay interior is234mm high and cannot hold276mm batteries above its unmodified floor. This variant requires a new lowered well, changed floor, qualified retention and loss of that tool/payload volume; electrical limits do not disappear by adding units. See reservation_checks.json.

## Portable / Colab execution

The package includes the original reference_frame_R06.step solely for body/frame interference checks. Run the included requirements installation in an authorized Python/Colab environment, then build_body_power.py. Main STEP/GLB generation does not depend on private assets or network downloads. The optional arm-screen scripts require the separately licensed original robot asset folder; set its path in check_arm_clearance.py before use. This package was executed in the current engineering environment; it does not claim execution in Colab.

## C02 suspension packaging update

Current provisional wheel centres are Y±0.94m and Z−0.25m, superseding Y±0.86m. The lower corner relief is480mm wide belowZ132mm. Local160mm-wide coilover service notches extend toZ215mm. C02 shock envelopes are Xstation±60mm, |Y|520–800mm and Z−430..200mm; no actual spring has been selected. The source-dimension tyre concept is876.3mm OD and317.5mm provisional section. The analytic parallel-link, locked-steering ±12° check gives about94mm minimum lateral body-to-tyre envelope separation; this is not actual tyre/rim fit, loaded clearance or certified travel. See tire_envelope_screen_C02.json and reservation_checks.json.
