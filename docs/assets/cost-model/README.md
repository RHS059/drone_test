# Six-wheel UGV cost model · C03_R03

Observed 9 October 2026. Configuration: frame R07, body R01, four C03_R03 steering corners, two retained C02_R06 middle corners, two rack assemblies and original tool adapter R04. Public listing references are not supplier quotations, live inventory commitments or landed checkout totals. No orders or vendor contacts were made.

## Primary results

- **Complete build cost: unknown.** Essential fabrication, six exact WD220 drives, two UR20 arms, the final OEM DC controller revision and many integration/services categories remain unpriced.
- **Publicly priced subset: USD 20,019.90 and EUR 2,891.34, kept separate.** The EUR listing includes VAT. Destination taxes and freight are unresolved. These baskets do not include the major missing costs and are not an estimate of the finished machine.
- **Measured operating cost: unknown.** No representative rover energy measurement, tariff or maintenance record was supplied.
- **Illustrative partial operating scenarios: about USD 61, 63 or 66 per operating hour**, using explicitly assumed mean battery draw of 2, 4 or 8 kW, USD 0.15/kWh, 90% charging efficiency, one supervisor-hour at USD 50 plus 0.1 maintenance-hour at USD 100 per robot-hour, and a module-only replacement reserve. Energy alone is about USD 0.33, 0.67 or 1.33/h. These figures exclude capital recovery, maintenance parts, installed battery replacement labor, taxes/freight, insurance, consumables, connectivity, transport, parked energy and downtime. They are neither measured costs nor a promise of uninterrupted operation.

The model has 124 rows, including reference-only geometry and unresolved cost categories. Five rows have public component prices. One hundred sixteen required or unresolved rows/categories remain unpriced; this is a gap count, not an assertion that the manufacturing BOM is complete.

## Exact priced subset

| Baseline component | Qty | Unit reference | Extended reference | Source and limitation |
|---|---:|---:|---:|---|
| BFGoodrich KM3, MSPN 72204, 35x12.50R18/E 123Q | 6 | USD 486.99 | USD 2,921.94 | [Vivid Racing](https://www.vividracing.com/bfgoodrich-mudterrain-km3-35x1250r18-p-152504463.html); stock statement and USD 10 ground-shipping promotion are not a verified six-unit delivered quote |
| RELiON 48V030-GC2, non-LT | 4 | USD 1,349.99 | USD 5,399.96 | [West Marine](https://www.westmarine.com/relion-48v030-gc2-lithium-iron-phosphate-deep-cycle-battery-48v-30ah-20659967.html); product page says out of stock; serial-clearance gate below |
| Robotiq AGC-GRP-2F85 | 2 | USD 5,205.00 | USD 10,410.00 | [Logic](https://www.logic-control.com/robotiq-agc-grp-2f85); lead time and exact fingertip contents require confirmation |
| Robotiq GRP-CPL-062, controller-connected | 2 | USD 644.00 | USD 1,288.00 | [King Barcode](https://www.kingbarcode.com/GRP-CPL-062); backorder, public standard price requiring confirmation; full cable/interface cost absent |
| EVO Corse SE5240060141 + CM0750180040-5 road kit | 6 | EUR 481.89 | EUR 2,891.34 | [EVO Corse](https://shop.evocorse.com/en/catalog/catalog_item/dakarzero-85x18-se5240060141.aspx?k=cm0752170010-5); VAT and five-nut kit included; cached availability conflicts |

Thirty EVO nuts are already covered by the rim bundles. Their separate allocated cost is null, not zero or a second charge. No foreign-exchange rate is assumed.

## Safety and integration gates

### Serial-specific battery recall

RELiON's [official U.S. notice](https://www.relionbattery.com/product-recall-us) covers certain 48V030-GC2 batteries in these serial ranges:

- RB48300020210314057–RB48300020210314729
- RB48300020210330001–RB48300020210330715
- RB48300020210507012–RB48300020221016550

The reported hazard is overheating/fire; the U.S. remedy is repair. Require traceable unaffected or manufacturer-remedied units before procurement/use. An owner of an affected unit should stop using it and follow the manufacturer's instructions. This CAD contains proposed batteries, with no known purchased-unit serials. It does not establish that any candidate unit is affected.

### Coupling routes are different products

The displayed baseline remains GRP-CPL-062 with the original ISO80-to-ISO50 adapter. Robotiq identifies [GRP-CPL-062 as controller-connected](https://robotiq.zendesk.com/hc/en-us/articles/360060115033-Couplings-and-cables-UR). Its separate cable, power and communications route is unresolved here.

For direct wrist connection, Robotiq's [connector article, updated 21 September 2026](https://blog.robotiq.com/knowledge/how-to-identify-the-type-of-connector-at-the-flange-of-universal-robots-e-series-robot-5-1736280763712) identifies UR20's female connector and GRP-ES-CPL-077. That is an alternative, not a relabeling of the current mesh or proof of equal coupling geometry. The two e-Series entries share an ISO50-4-M6 bolt pattern. Robotiq also [supports a controller-connected CB-series coupling with a 10 m cable](https://blog.robotiq.com/knowledge/longer-e-series-cable).

The alternatives array records GRP-ES-CPL-077 at USD 680 and ACC-APL-UR20 at USD 667.97 as replacement options only. Neither is added to baseline baskets. Robotiq says the [UR20 normally includes a flange adapter](https://blog.robotiq.com/knowledge/plug-and-play-on-ur20-5-1736280730313); package scope must be checked before adding a replacement plate. The modeled original R04 adapter remains unqualified and unpriced.

### Arm/controller packages must be counted once

A standalone [CB5.5 OEM DC SKU 200143 listing](https://automationdistribution.com/universal-robots-controller-box-oem-dc-cb5-5/) is USD 8,217 each, tariff surcharge included. This is a candidate reference because the final controller revision is unresolved. Commercial [UR20 configurations can already include OEM DC controllers](https://automationdistribution.com/universal-robots-ur20-collaborative-robot/). An integrated package quote must replace the separate arm/controller rows rather than duplicate controllers.

### Reject attractive prices for nonmatching motors

An [EVSHOP WD220 listing](https://evshop.it/en/products/motor-wheel-wd220-48v-3kw) at EUR 2,499 is a 3.0 kW, four-bolt variant. It does not price the selected 2.2 kW, five-stud WD220-SMAC132-050-48V-EMB-5STUDS. The latter price and mass remain null.

## Operating model boundaries

Four selected batteries provide **6.144 kWh nominal**, not a measured usable-energy value. The six motor ratings are 2.2 kW, **S2 60 minutes**, with S1 continuous capability unknown. The 47 A motor rating is not established as DC-bus current. Individually published battery currents cannot be summed into a qualified system rating.

The illustrative battery-module reserve uses USD 5,399.96 of module reference prices, assumed 2,000 cycles at 80% depth, five calendar years and 1,000 operating hours/year. It takes the greater of cycle and calendar reserves, avoiding a duplicate charge for the same replacement. These are planning assumptions, not guaranteed lifetime or actual replacement cost.

To establish an actual operating rate, record grid charging energy and tariff, mission energy/peaks/temperatures, operator time, recovery and setup, maintenance parts and labor, installed replacement prices, and achieved utilization. Complete operating and fully burdened hourly outputs stay null until required costs are known. The files intentionally produce no whole-rover runtime number.

## Files and integration contract

- `cost_model.json`: baseline parts, alternatives, currency-separated baskets, gaps, gates, actual-null inputs, scenarios and formulas.
- `BOM.csv`: the same baseline rows and values. Unknown fields contain literal `null`; they must not be parsed as zero.
- `sources.json`: short factual observations, URLs, exact SKU, seller/region, retrieval date, tax/shipping/availability limitations. No quote date is fabricated.
- `build_cost_model.py`: reproducible builder reading the approved mechanical ledgers; changes no application files.
- `test_cost_model.py` and `validation.json`: quantity, source, arithmetic, null, revision and bundle checks.

UI: show `build_summary.complete_build_cost` as unknown. Show `public_price_baskets` with the explicit label “Priced subset only.” Show `operating_cost.actual_cost_per_operating_hour` as unknown and scenario `modeled_partial_usd_per_operating_hour` as assumptions-only and incomplete. Round scenario display; retained decimals serve arithmetic checks.

The pinned modeled-mass subtotal is **1127.4662815201427 kg**, not whole-rover mass. This includes six exact-SKU EVO rims at 15.1 kg net each (90.6 kg total), verified by the manufacturer API field and its product-script kg formatter. It excludes tire and nut masses. Do not substitute base-SKU 14.96 kg, unit/package 16.5 kg or gross 17.3 kg values. The manufacturer page displays a nut weight field of 212 without units, while Product JSON-LD specifies 0.217 kg. These fields require reconciliation. Nut mass remains unknown and is excluded from that snapshot; no mass is inferred from an undocumented raw page field or shipping weight.

## Historical estimates and updates

The old `docs/costs.json` workshop base of USD 311,495.60 is a superseded planning scenario: eight LT batteries, different drive/tire selections, assumed steering, and broad allowances. Its totals and runtime are not current quotes or current rover predictions.

To roll to a later approved corner revision, update the builder's `REV`, inspect the new ledger and integrated mass snapshot, and deliberately update the expected snapshot mass and test pin. Do not silently follow the newest file in the directory. Re-run builder and tests after source or quantity changes. Reconfirm supplier price, package scope, stock, destination tax/freight and recall serial clearance before procurement.

### C03 revision reconciliation

All 84 original rows are preserved node-by-node from mass_cost_ledger_C03_R03.json: 76 steering-corner/rack rows at quantity one and eight middle-corner rows at quantity two. Their original modeled subtotal is 332.56466061455905 kg. They replace the eight old fabrication rows that each represented six C02 corners, without retaining or duplicating those rows. The two C02 bearing-envelope rows remain reference-only at quantity two each.

The independent snapshot and cost model agree on 1127.4662815201427 kg known subset. Prices, battery architecture and the three numerical operating scenarios are unchanged. Those generic assumed battery draws do not validate the new steering energy demand. Measured steering energy, actual actuator input power and qualified steering duty remain null/unknown.

New purchased candidates, all with unknown accepted installed mass and price:

| Candidate | Quantity | Scope |
|---|---:|---|
| GE20ES root/middle bearings | 56 | Replaces old all-C02 count of 72 |
| FK AIN16 outer spherical bearings | 8 | One per outer joint |
| FK 16-12HB misalignment spacers | 16 | Two per outer joint |
| FK JMX12 right-hand tie ends | 4 | Right-hand threaded candidates |
| FK JMXL12 left-hand tie ends | 4 | Left-hand threaded candidates |
| FK 12-10HB tie-joint spacers | 16 | Two per tie end |
| Housing retainer M5 screws | 32 | Grade and length unselected |
| Thomson HD48-B045, 200 mm stroke, M/M | 2 | Packaging candidates; supersedes 150 mm study; complete order code and force/duty suitability unresolved |
| King RS2008 Pure Race coilovers | 6 | Exact configuration and springs unselected |
| Wheel output studs/input nuts | 60 aggregate | Mixed hardware count, not 60 identical selected SKUs |

The residual steering row covers controls, wiring, sensing, commissioning, safety and service integration; it excludes separately itemized geometry, actuators, bearings and rod ends. Offboard service fixtures remain an unpriced external-workcell category and do not enter vehicle mass.

The builder works in the local cost-model staging folder or the published docs/assets/cost-model layout. It reads the pinned steering ledger and contract, the retained C02 middle ledger, body evidence and independently audited mass snapshot. `manufacturer-mass-evidence.json` is included so the exact net-mass evidence remains reproducible. No vendor CAD or full webpage content is included.

### R03 selection and delta

The selected C03_R03 revision replaces four upper arms with upper_wishbone_C03_R06 and four lower arms with lower_wishbone_C03_R04. Original running gear increases by 3.6771523172603 kg versus C03_R01; other original geometry and purchased requirements are unchanged. The separate B068/B100 actuator comparison is research only. It has not replaced the B045 200 mm packaging candidate and adds no baseline price or mass.
