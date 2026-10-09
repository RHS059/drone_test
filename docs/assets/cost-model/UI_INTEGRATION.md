# Future integration handoff, not an app change

This folder is a separate C04+E05 candidate. Keep it outside the current app/publication payload until the parent deliberately chooses the matching geometry and model revision. The existing C04 app still correctly carries its prior C04-only known subset; do not silently advertise these E05 numbers against a scene that lacks E05.

For a later matched integration:

1. Preserve the 40-hole deck and every body part except the two exact names in `replacement_map.json`. Replace those parts; do not add duplicate old/new partitions.
2. Load the 98-node E05 main pair once. Its GLB is already in vehicle-C metres; no second mm-to-m conversion. Only two geometric jacket routes are closed. Keep physical electrical continuity false.
3. Use the new single `body_composed` row plus 98 individually named E05 rows. Existing E04 lugs/stacks remain counted once. Optional old local leads were not loaded or mass-counted; there is no subtractive mass correction for them.
4. Show `1272.5501071050776 kg` only as the known modeled/catalogue subset, never full installed vehicle mass. Explain that this includes unreleased nominal routed cable length and assumed aluminium stand density. Do not use the `steel` display key for mass.
5. Keep USD 17,200 and PLN 6,090 separate. Added E05 prices and complete build cost remain unknown. Preserve all operating scenarios and null actual hourly/runtime values.
6. Point links at the bundled file paths. The baseline technical/historical inputs now live under `inputs/C04/inputs/`; E05 inputs under `inputs/E05/main_routes_E05/`.
7. Re-run cost tests and the application's integration, composition and snapshot tests against the exact integrated build. This package alone is not app QA or publication approval.

Minimal review artifacts: `delta_summary.json`, `replacement_map.json`, `material_mass_ledger_E05.json`, `validation.json` and `dependency_manifest.json`.
