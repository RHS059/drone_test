# C04 matched build and operating cost model

Observed 9 October 2026. Development visualization only, not fabrication, procurement or operational release. This package changes no application files and makes no orders or vendor contacts.

## Results

- **Complete build cost is unknown.** The matched BOM contains 230 cost/mass rows, including original geometry and unresolved categories. This is not a complete manufacturing BOM.
- **Priced subset: USD 17,200 and PLN 6,090, kept separate.** No EUR rim basket survives. USD combines US gripper/coupling references with a clearly dated 2026 Q2 LATAM USD-C battery/BMS price list; these are not a current US quotation or a common landed-cost basis.
- **Known modeled/catalogue mass subset: 1268.0641640992537 kg.** Whole-vehicle mass and center of gravity remain unknown. No vehicle was weighed.
- **Actual hourly operating cost and runtime are unknown.** Preserved illustrative 2, 4 and 8 kW assumptions now use the selected 10.24 kWh nominal bank and USD 4,482 dated module-only replacement reference. Partial scenario results are USD 61.23, 61.76 and 63.52 per operating hour. These omit major costs and do not establish continuous operation.

## Price observations

| Selected item | Quantity | Unit reference | Extended reference | Basis |
|---|---:|---:|---:|---|
| Robotiq AGC-GRP-2F85 | 2 | USD 5,205 | USD 10,410 | Retained [Logic public listing](https://www.logic-control.com/robotiq-agc-grp-2f85); exact contents/lead time require confirmation |
| Robotiq GRP-CPL-062 | 2 | USD 644 | USD 1,288 | Retained [King Barcode listing](https://www.kingbarcode.com/GRP-CPL-062); controller-connected route, full cable/interface cost absent |
| Victron BAT548110620 | 2 | USD 2,241 | USD 4,482 | [Official 2026 Q2 LATAM USD-C price list](https://latam.victronenergy.com/wp-content/uploads/2026/04/Pricelist-Victron-2026-Q2-USD-C.pdf), ex VAT, dated indicative reference |
| Victron LYN034170310 | 1 | USD 1,020 | USD 1,020 | Same dated LATAM price list, ex VAT |
| Trelleborg SK-900 12-16.5 12PR, seller SKU 35546 | 6 | PLN 1,015 | PLN 6,090 | [TyreTrade listing](https://tyretrade.pl/opona/12-16-5-trelleborg-sk-900-12pr/), gross/brutto; manufacturer article identifier and six-unit allocation unverified |

Jantsa 10005240 rim price remains null. NRS 60027.01.112 is a four-foot Stealth Black retail pair, so two packages supply four straps. Its variant-specific price and purchased mass remain null; the family range is not used. No tax, import charge, freight, FX rate, current stock allocation or supplier quote is invented. Confirm commercial region, exact SKUs, package contents and destination costs before procurement.

## Matched configuration

- Mechanical structure C04 R05, bound to the 575-file public source freeze C04 R02: 126 original nodes, replacing old C03 steering and C02 middle structures. No EVO/BFG or pattern-adapter active rows remain.
- Six Jantsa 10005240 9.75 x 16.5 ET -70 rims, six Trelleborg SK-900 tires, thirty RIMA 22095 nuts.
- Two Thomson B068 200 mm M/M candidates at 7 kg each; six Eibach 1800.300.0200S springs at 3.54 kg each. Their simplified external CAD does not add another mass term.
- Frame R07, two UR20 arms, two original R04 adapters, two Robotiq grippers and controller-connected couplings retained. The exact arm/controller package remains unpriced and must count packaged controllers only once.
- Body is PR01, then the twenty SO02_E04P named replacements, then the nineteen-part E04 trough/gland delta, then BA02 removes thirty-four RELiON restraint parts and replaces the well floor.
- BA02 has two 37 kg Victron batteries. Its original metal additions are counted separately from the replacement floor. Strap, buckle, battery, terminal and vent external depictions do not contribute density-based mass.
- Selected E02 carrier and E04 electrical patches compose by their ledger's remove/replace flags. Trough mass is in body only. Purchased housing, lug and connector-contact representations remain excluded from accepted original mass. Current [Lynx 1000 A specifications](https://www.victronenergy.com/media/pg/Lynx_Smart_BMS_NG/en/technical-specifications.html) give 2.7 kg; the conflicting 2.5 kg price-list value is not used for mass.

## Mass reconciliation

| Separate group | Included known kg |
|---|---:|
| Frame R07 | 386.9529671773959 |
| Two arms, two controller reservations, two original adapters | 139.233693246 |
| Original structure C04 R05 | 347.912332809332 |
| Original joint details | 14.017320451359337 |
| Original shock/carrier/retention details | 16.93926994842406 |
| Six rims + two actuators + six springs | 152.24 |
| Composed original body, including replacement well floor | 113.5556902568118 |
| BA02 new original metal excluding floor | 7.2705448374377335 |
| Two battery modules | 74 |
| Lynx BMS | 2.7 |
| Selected original electrical support/hardware estimates, excluding trough | 13.242345372493395 |

`body_composition.json` preserves every final named body part, material assumption, volume and mass; records the removed parts; and records each intermediate subtotal. PR01 material changes to aluminium bosses/clips are sourced from its generator instead of incorrectly inheriting the old steel placeholder material. Its progression is:

1. PR01: 267 parts, 116.7967822162259 kg
2. SO02_E04P: 267 parts, 115.99386426207543 kg
3. E04 trough/glands: 271 parts, 115.88551866207544 kg, with four unknown-mass purchased representations
4. BA02 removals/floor: 237 retained body parts, 113.5556902568118 kg

The BA02 additions are separate: 7.2705448374377335 kg original metal plus 74 kg battery catalogue mass. Its replacement floor is 3.7848881760772164 kg and appears only in the composed body.

The installed mass of drives, tires, nuts, dampers, bearings, grippers/couplings, straps/buckles, unselected-grade guides, inverter variants, ABB devices, most electrical components and harness remains unresolved. Original nominal hardware estimates do not prove final purchased mass, grade, preload, tolerance or fatigue strength.

## Operating boundaries

The bank is **2 × 51.2 V × 100 Ah = 10.24 kWh nominal**. Usable energy and mission energy are unknown. The **180 A figure is a conditional warm-bank development ceiling with no implemented vehicle enforcement**, not qualified full-six-motor operation. Actual BMS discharge/charge limits, both module temperatures, current sharing, auxiliaries, inrush and pack availability can reduce the permissible power or disable motion. ATC/ATD mapping, regen inhibition, an independent brake/energy sink, branch protection and completed physical wiring remain open.

The 47 A drive nameplate value is not established DC demand. Six 2.2 kW ratings are S2 60 minutes, with S1 unknown. Even ideal 13.2 kW/51.2 V is 257.8125 A before arms/auxiliaries and conversion losses; this is a limiting arithmetic illustration, not a system demand measurement.

Preserved assumptions are USD 0.15/kWh, 90% charging efficiency, one supervisor hour at USD 50 and 0.1 maintenance hour at USD 100 per robot-hour; 2,000 cycles, 80% depth, five calendar years and 1,000 operating hours/year. The module reserve takes the larger of cycle or calendar reserve, never their sum. Only the module reference changes to USD 4,482 and nominal capacity changes to 10.24 kWh. These life and utilization assumptions are not validated. The BMS is not included in the module-only reserve. Capital, replacement installation labor, maintenance parts, taxes/freight, insurance, consumables, connectivity, transport, parked energy and downtime remain excluded.

## Reproduction and files

Run `python build_cost_model.py` then `python test_cost_model.py` in this directory. Both use the Python standard library. The builder needs only the bundled frozen inputs, performs no network calls and is byte-reproducible. The 24 passing tests cover arithmetic, CSV, null preservation, source hashes, replacements, quantities, thermal/control flags, no-proxy/double-counting and deterministic rebuild. They are not hardware or safety tests.

- `cost_model.json`, `BOM.csv`, `sources.json`: active matched cost model
- `mass_reconciliation.json`, `body_composition.json`, `electrical_mass_selection.json`: inspectable accepted/excluded mass evidence
- `inputs/`: factual frozen ledgers, baseline historical records and one original source script for material traceability; no vendor CAD, PDFs or fetched webpage captures
- `input-manifest.json`: exact source-file and SHA-256 mapping
- `validation.json`, `test_run.log`: local checks
- `UI_INTEGRATION.md`: required static-text changes when the parent integrates this model

`freeze_inputs.py` is a maintainer-only refresh tool for the original shared staging paths. It is not part of normal replay. Do not run it to silently follow new files: inspect the changes, refresh deliberately, rerun tests and update checksums. Historical C03 data is preserved solely under named historical input records and is not included in active totals.
