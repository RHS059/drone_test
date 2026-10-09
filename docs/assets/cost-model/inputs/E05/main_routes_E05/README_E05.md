# E05: two supported main DC cable routes

This original module closes only the geometric jacket routes from Q0:P_OUT to LYNX:BAT+ and Q0:N_OUT to LYNX:BAT−. It is a non-energizable installation candidate. It does not close battery-to-Q0 wiring, upstream protection/merge, traction branches, motor pigtails, arm wiring, control mapping, safety permissions or regeneration handling.

## Integration

Load main_pair_supported_E05.glb with the same placement as E04. GLB vertices are already in metres with Z up; STEP and contract coordinates are C millimetres. Do not apply an additional millimetre-to-metre scale to the GLB. Replace exactly controller_battery_partition and battery_tool_partition with the two names in partition_main_glands_E05.glb. Preserve the forty-hole deck and all other selected body parts. Remove optional old Q0_P_OUT_service_lead_bend and Q0_N_OUT_service_lead_bend overlays. The other E04 local open lead segments remain unfinished overlays.

All 98 added source nodes appear in main_pair_graph_E05.json: two continuous jacket envelopes, eight original stands and sixteen clamp halves, sixty-four M4 stack components, four source-sized glands and four locknuts. Nominal cylindrical threads model retained contact without helical thread strength claims. Original stand feet contact the actual deck. The intended joint is aluminium-to-matched-aluminium welding; exact deck/stand alloy, temper, filler, heat-affected-zone and thin-deck strength qualification remain open. Mere bearing does not establish a commissioned welded load path.

## Evidence and limits

Actual STEP checks cover the composed body/electronics, all new self-pairs, source-positioned original lug mouths, support/clamp/retainer contacts, four full partition bores and all cable segment seams. Separate checks cover 78 sampled corner poses against R13 towers and guided shock modules. These are finite-pose geometry checks, not dynamic flexible-cable, continuous-motion, tool-access or service validation.

LAPP ÖLFLEX HEAT 180 SiF 0060001 provides the 70 mm², nominal 14.2 mm OD and fixed-installation 6D bend dimensions. Exact CAD arcs reach the nominal 85.2 mm minimum; actual OD tolerances still require release. The model renders silicone insulation envelopes, with no conductor strands or qualified crimp interface. Positive identification, cable thermal rating, abrasion protection and gland sealing/pullout remain open. The source black cable is not a moving-corner harness selection.

cable_source_and_scenario_E05.json contains source provenance and a declared ideal-copper 180 A scenario. The proposed bank cap is unenforced; calculated loss is not ampacity or protective-coordination approval. Upstream pack fuses, covered merge hardware and main-fuse coordination are absent. Do not energize.

Battery polarity uses the separate R01 correction: positive Y+275.25, negative Y−275.25. E05 itself connects no battery terminal. Motor connector XYZ remain unknown.

## Public scope

PUBLIC_FILES_E05.json is the only allowlist. Included CAD and scripts are original work. Supplier CAD/PDF/images, rejected revisions, review images and logs are excluded. E04 is immutable and supplied separately. The existing C04 cost freeze excludes this new E05 module; its cable-length estimate must not silently enter an accepted whole-vehicle subtotal.
