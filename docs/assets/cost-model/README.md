# C04 + E05 separate mass, BOM and cost candidate

Prepared 9 October 2026. This is an isolated, offline-reproducible candidate patch. It does not change `app-C04`, the accepted `cost-model-C04` snapshot, the E05 source freeze, or the pending publication payload. No external write, order, supplier contact or publication is included.

## Result

| Known nominal subset component | Delta, kg |
|---|---:|
| Two LAPP 0060001 geometric route lengths | +4.074692045393900 |
| Eight original aluminium stands | +0.427410760119472 |
| Four holes in two existing aluminium partitions | −0.016159799689731 |
| **Net known-subset delta** | **+4.485943005823641** |
| C04 baseline known subset | 1268.064164099253700 |
| **Separate C04+E05 candidate known subset** | **1272.550107105077600** |

These are mixed nominal modeled/catalogue estimates, not weighed or complete installed masses. Full E05 installed mass, whole-vehicle mass, center of gravity and complete build cost remain unknown. Tiny last-digit differences from direct bore-volume arithmetic reflect floating-point summation only.

The priced subsets remain **USD 17,200** and **PLN 6,090**, separately and with the original dated/mixed-market restrictions. None of the 98 new rows has an accepted price. A zero change in priced subsets does not mean E05 is free. No currency conversion, raw-metal price, fastener allowance, cable allowance, gland price or labor estimate has been invented.

Actual operating cost/hour and runtime remain null. The entire C04 operating-cost object is preserved exactly: its 2/4/8 kW assumptions and illustrative partial USD/hour figures are unchanged. Added mass and an ideal-copper route-loss scenario do not justify a new measured demand or runtime claim.

## Cable source, lengths and boundaries

The [official LAPP ÖLFLEX HEAT 180 SiF catalogue](https://products.lappgroup.com/online-catalogue/power-and-control-cables/expanded-ambient-temperatures/silicone-single-cores/oelflex-heat-180-sif.html) was checked on 9 October 2026. The exact article 0060001 row gives 70 mm², black insulation, 14.2 mm nominal OD, and nominal cable weight 724 kg/km, equivalent to 0.724 kg/m. The adjacent 672 kg/km value is the separate copper index; it is not the full cable mass. Manufacturer values are nominal, with detailed tolerances available on request.

The frozen geometry supplies the lengths, not the manufacturer:

- MAIN_positive, Q0:P_OUT → LYNX:BAT+: 2.7697464313510465 m
- MAIN_negative, Q0:N_OUT → LYNX:BAT−: 2.8582812556571024 m
- Total 5.628027687008149 m × 0.724 kg/m = 4.0746920453939 kg

This is a nominal routed-length cable estimate. Procurement cut lengths are unreleased and remain null. It excludes additional stripping/cut allowances, slack or service allowance beyond the modeled routes, waste, new terminations and other hardware. Cable jacket volumes are never multiplied by copper, silicone or other bulk density; doing that as well as applying catalogue mass would double count the cable.

Two geometric jacket routes are present. Conductive crimp contact, installed ampacity, protection coordination, upstream pack/merge/main-fuse wiring, traction branches, motor pigtails, arm wiring, safety mapping and regeneration handling are still unresolved. End-to-end electrical continuity and operational acceptance remain false. Do not energize. The source's 180 A ideal-copper calculation is preserved in the frozen evidence only; it is not injected into operating scenarios or treated as ampacity approval.

## Exact part accounting

`replacement_map.json` records full old/new named body records and masses:

| Body name | Old kg | Replacement kg |
|---|---:|---:|
| controller_battery_partition | 1.9023945235218704 | 1.8943146236770079 |
| battery_tool_partition | 1.9677206001606726 | 1.9596407003158060 |

Only these two existing parts are replaced. Each loses two 25.2 mm bores through 3 mm material. They remain included once through the single `body_composed` BOM row. All other 235 final body records, including the forty-hole `main_base_deck_3mm`, are unchanged. The final body still contains 237 named records; its known original mass is 113.53953045712207 kg.

There are 98 added source nodes and exactly 98 added BOM rows, for 328 rows total. Source nodes are individually traceable to the contract, connection graph and GLB:

- 2 cable runs: nominal manufacturer mass × source geometry length accepted
- 8 original welded stands: 2700 kg/m³ assumed aluminium density matched to the retained deck
- 16 original clamp halves: mass and material/liner selection unknown
- 16 M4×30 screws, 32 washers and 16 M4 nuts: purchased SKU, installed mass and price unknown
- 4 LAPP 53111030 glands and 4 LAPP 53119030 locknuts: installed mass and price unknown

The eight stands add 0.4274107601194724 kg of nominal original aluminium. The E05 generator's legacy `steel` display-palette key is explicitly rejected as a material specification. An exact-name material ledger binds each node to the frozen contract's `actual_material`, then accepts only the declared aluminium density for stands. Alloy, temper, filler, weld process, heat-affected-zone strength and fatigue remain unqualified. Original clamp material is not assigned a guessed polymer density. Nominal steel fastener geometry is not used to invent commercial masses.

Existing E04 lugs and M8/M10 terminal stacks are reused without an extra mass or purchase term. Optional old Q0_P_OUT_service_lead_bend and Q0_N_OUT_service_lead_bend were absent from both the frozen runtime source-node selection and accepted C04 mass ledger. They are neither added nor subtracted here. Their conditional removal list is recorded explicitly. Remaining-harness scope excludes already itemized E05 rows and reused terminal hardware.

## Reproduce and inspect

Use Python 3 with only its standard library:

```sh
python build_cost_model.py
python test_cost_model.py
```

Normal replay is offline, uses only bundled inputs and writes only this folder. No CAD kernel, browser, upstream directory or external service is required. The builder refuses altered frozen inputs. It also verifies the original C04 checksum set, E05 public allowlist and freeze pins before calculating. The prior C04 builder can reproduce its model in an isolated temporary copy.

The 36 regression tests cover input hashes, actual GLB node names, exact replacements, unchanged deck/body rows, bore arithmetic, explicit aluminium materials, null commercial parts, cable units, no duplicate optional leads, reused terminal hardware, row counts, mass/baskets, identical scenarios, null actuals, electrical scope, CSV roundtrip, deterministic replay and rejection of a tampered input. They are calculation/source-accounting tests, not independent CAD-kernel, metrology, structural, electrical, procurement or operational approval. Frozen upstream geometry-check reports are evidence from the E05 source freeze; their CAD analyses were not rerun for this cost patch.

Key files:

- `cost_model.json`, `BOM.csv`, `sources.json`: separate complete candidate cost/BOM data
- `delta_summary.json`: small machine-readable numerical change and unresolved boundaries
- `body_composition.json`, `replacement_map.json`: exact final body and replacements
- `material_mass_ledger_E05.json`: all 98 added named nodes with explicit material/mass decisions
- `mass_reconciliation.json`: full final mass rows and groups
- `input-manifest.json`: 76 immutable local input files and SHA-256 pins
- `dependency_manifest.json`: E05 freeze/geometry pins plus 12 verified separately supplied upstream dependencies
- `output-checksums.json`: deterministic generated-output hashes
- `validation.json`, `test_run.log`: local regression results
- `isolation_verification.json`: source/app/publication comparison against the pre-build read-only snapshot
- `UI_INTEGRATION.md`: future integration handoff; no app changes have been made

`inputs/C04/` preserves the prior model and its complete factual input package. `inputs/E05/` contains only the E05 public allowlist plus its freeze/allowlist records: original CAD, scripts and factual ledgers, no supplier CAD/PDF/images. `inputs/runtime_C04/` records the frozen runtime loader/selection used for the optional-lead check. Manufacturer provenance is a compact factual observation with a direct source link, not a copied webpage.

The 12 upstream geometry dependencies are hash-pinned and were checked against their actual local bytes. They remain separately supplied and are not required to replay this mass calculation; a CAD regeneration would require them and the E05 CAD toolchain. `freeze_inputs.py` is a maintainer-only one-time snapshot tool, deliberately refusing an existing freeze. Do not use it to silently update sources during replay.
