# C04 viewer integration contract

The existing `cost-ui.js` data fields and `cost-math.js` formulas remain compatible. Copy this package to the selected viewer's `docs/assets/cost-model` and bump JSON request cache versions. Do not modify historical app data by accident.

Required static copy changes in the corrected viewer:

1. Replace “EUR rim listing includes VAT” with “Priced subset: separate USD and PLN references. PLN tires are gross/brutto; Victron prices are dated 2026 Q2 LATAM USD-C ex VAT. Destination tax and shipping are unresolved.”
2. Remove the RELiON recall warning from the active selection. Keep it only with historical RELiON records. Replace it with current BA02 dry-location, battery restraint/thermal and unimplemented electrical control gates.
3. Replace BFGoodrich/EVO body/wheel labels with Jantsa 10005240, Trelleborg SK-900 12-16.5 12PR and RIMA 22095. Do not present the B14/M16 interface as application-approved.
4. Replace old capacity/count references with two BAT548110620 modules, 10.24 kWh nominal. State that 180 A is a conditional warm-bank development ceiling, not commissioned power capability. Temperature, BMS limits, regen/ATC/ATD and pack-loss stop gates remain unresolved.
5. Change the cost date note to “References reviewed 2026-10-09. Victron values are the dated 2026 Q2 LATAM price list. Listings are not supplier quotations; confirm stock, destination costs and package contents.”
6. Scenario reserve uses USD 4,482 module-only reference and 10.24 kWh nominal capacity. The existing formula will pick these up from JSON; keep user-adjustable assumptions and all actual/complete/runtime outputs null.
7. Show mass as “Known modeled/catalogue subtotal,” not whole-vehicle mass. Preserve unknown entries for drives, tires, nuts, straps/buckles and other omitted purchased components. The accepted subtotal is 1268.0641640992537 kg; linked mass ledgers explain scope and name-based replacement.

Expected default 4 kW scenario: energy USD 0.6666666667/h; labor USD 60/h; module reserve USD 1.09423828125/h; partial subtotal USD 61.760904947916664/h. These are illustrative, incomplete assumptions, not measured or qualified operating results.

The package intentionally does not publish a whole-rover runtime, convert currencies, procure components or label the development model buildable. Supplier images, full web captures, PDFs and restricted manufacturer CAD are absent.
