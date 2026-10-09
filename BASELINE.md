# Six-Wheel Builder — baseline 01

Static Three.js engineering workbench for a conceptual six-wheel UGV. Serve `docs/` with GitHub Pages from the `main` branch. Relative imports/assets support the `/drone_test/` project path. HTTPS is required for WebGPU. No authentication service, account data or backend is included.

Original dimensioned procedural envelopes, not production CAD. Two planning variants, travel-only quasi-static mobility calculations, source-backed reference components and clearly marked unquoted cost allowances. Assembly animation is a kinematic plan, not proof of autonomous assembly or structural safety.

## Verification
`node test-model.mjs` checks ten independently generated scenario fixtures plus parameter sensitivities. CI checks JavaScript syntax and these calculations. Actual browser rendering and hardware WebGPU activation are separate checks. WebGL2 fallback and renderer failure are displayed explicitly.

## Pages
Repository Settings → Pages → Deploy from a branch → `main` → `/docs`. The existing README/history are preserved. A root index redirects to the viewer when Pages serves /(root); /docs serves the viewer directly.

## Attribution
Three.js 0.186.1 is vendored unchanged under its MIT license in `docs/vendor/THREE-LICENSE.txt`. OrbitControls is from the same release. Vehicle geometry and application code are original. Manufacturer data/source references are recorded in `docs/mobility.json`, `docs/assembly.json`, `docs/costs.json` and the evidence panel. Manufacturer CAD has not been copied or redistributed.

## Known gates
Continuous motor/inverter and brake selection; bus/thermal duty; steering/suspension clearance; real support geometry; structural joints/fatigue; disabled-target repair; fail-safe lifting; independently deployable field gantry; printer bootstrap/acceptance; measured intervention and throughput data. Passing analytical margins is not engineering certification.
