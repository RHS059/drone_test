# Standalone reconstructed gripper contact laboratory

This is a **new reconstruction**, not recovered historical test parameters or a claim that the original package survived. It does not validate a complete six-wheel robot, manipulator, compliant object, hardware, or a contact-calibrated digital twin.

## Reproduce

Serve this folder with an ordinary static HTTP server and open `index.html`. All browser imports are relative and vendored. It runs actual official MuJoCo WebAssembly locally in the browser; recorded CSV/JSON is not used to animate it.

Native: install official `mujoco==3.15.0` into your environment, then run `python scripts/run_native.py`. In the reconstruction workspace the invocation was `PYTHONPATH=/tmp/ugv-mjpy python scripts/run_native.py`.

WASM and parity: `node scripts/run_wasm.mjs && node scripts/validate.mjs`. Both runtimes report 3.15.0. `scripts/browser_qa.py` uses Playwright and Chromium against localhost port8788. `scripts/build_scenarios.py` regenerates the original coupon STEP/STL (requires CadQuery) and experiment XML. `scripts/fetch_sources.py` captures official pinned Menagerie files; see `sources.json` for immutable URLs and SHA256 checksums.

## Model and exact units

- Google DeepMind MuJoCo Menagerie Robotiq2F85, commit `0059d4335f8156206f63a35662313385f7ad6d74`. Source XML and eight STL geometry files are retained unchanged, together with BSD-2-Clause license, README and changelog.
- Menagerie meshes are millimetres; the upstream mesh scale remains `0.001 0.001 0.001`. Joint positions, inertias, masses, tendon, two closed four-bar connect constraints and driver equality remain sourced from that model.
- Coupon is an original analytic rectangular solid,40×40×30mm, centered at CAD origin. STEP and STL are in **millimetres**. It is freshly generated, not a recovered historical binary. MJCF collision is the exact equivalent box with half sizes `0.02 0.02 0.015` **metres**; no mesh simplification changes its shape.
- Simulation SI units: metres, kilograms, seconds, Newtons. Mass is independently assigned, not inferred from the coupon CAD material. Nominal and low-friction0.15kg; heavy2kg. These masses correspond to artificial test loads rather than a claimed material density.
- Upstream gripper pad collision proxies remain the original boxes. Link mesh collisions use MuJoCo convex collision geometry, as standard in Menagerie. This is not a soft silicone or deformable-contact model.

## Declared scenario

`scenario.json` is the authoritative parameter declaration. Gravity9.81m/s², timestep1ms, implicitfast integration,100 solver iterations, tolerance1e-10, elliptic friction cone. Duration5.5s;550samples at10ms intervals per case. Gripper mounted downward atz0.3m; coupon center initiallyz0.1512m. Source position actuator command ramps0→200 at0.2–1.2s, force limits remain upstream±5.

The only coupon weld is explicitly `initial_world_fixture`, coupon-to-world, active until1.5s. It is disabled permanently before transport. **There is no object-to-gripper weld or kinematic object following.** The gripper base follows a prescribed100mm horizontal smoothstep at2–3.5s. Gripper opens at4s. Coupon position, contact, normal forces, falling and slip are solved from dynamics.

Nominal friction0.7; low-friction0.015; heavy friction0.7. Coupon geom priority2 makes these sliding coefficients effective for contacts against upstream priority1 pads. Torsional and rolling friction are0.005 and0.0001. Strict task PASS means maximum Euclidean coupon-to-prescribed-center error is **less than10mm** over1.6≤t<4s. Heavy is a changed load, not necessarily a failing negative control.

## Fresh measured results

Native / WASM strict task results agree:

- Nominal: worst transport error2.61103mm, **PASS**.
- Low friction:152.31481mm, **FAIL**, real slip/drop before opening command.
- Heavy:2.37696mm, **PASS**.

Nominal/heavy commanded release is observed: coupon remains above0.1m immediately before4s and falls below0.05m by5.5s. Low-friction already dropped and is deliberately **not** counted as successful commanded release. The software regression harness can pass while the low-friction experiment fails.

Maximum sampled native/WASM coordinate difference is1.2915µm and contact-normal-force difference0.03704N. The initial1µm numerical gate **failed**. A documented10µm gate is used for nonsmooth-contact numerical agreement (1000× tighter than the10mm task gate); the original failure is preserved in `summary.json`. This is bounded numerical agreement, never exact bitwise parity or real-world validation.

Pad force is the sum of scalar normal forces only for coupon–pad contacts. Total contact normal force additionally includes the floor; a heavy coupon's floor impact peak must not be presented as gripper force. Raw sampled position, qpos, fixture status, command and forces are retained in native/WASM JSON.

## Browser QA status

Live Node execution of the same WASM module passed. Browser launch in this executor is blocked: Chromium cannot create its process-singleton socket (Operation not permitted), including an escalated retry. Browser screenshots, visual layout, pause/reset and actual browser loading therefore remain unverified until a permitted browser environment runs `scripts/browser_qa.py`. This is recorded separately in `results/browser-qa.json`.

## Browser module API

`createEngine(readBytes?)` loads official single-threaded WASM. Default asset loader uses relative fetch. `engine.createCase('nominal'|'low-friction'|'heavy')` returns `{model,data,mj,step(),sample(),dispose(),stepCount}`. Call5500steps and sample every10steps. `summarize(samples)` calculates declared metrics. `validateParameters()` rejects invalid nonfinite/nonpositive masses and negative/nonfinite friction; the shipped UI deliberately exposes only the three fixed declared cases.

## Attribution

Menagerie Robotiq model:BSD-2-Clause, retained `assets/robotiq_2f85/LICENSE`. Official MuJoCo3.15.0 JavaScript/WASM:Apache-2.0, retained `vendor/LICENSE-MUJOCO`, package README and metadata. Three.js renderer:MIT, retained `vendor/THREE-LICENSE.txt`. Original scenario, scripts, UI and coupon are new work for this reconstruction. No private soldier assets or external CAD are involved.

Validation is read-only by default. To intentionally regenerate the summary after new native/WASM runs: `node scripts/validate.mjs --write`.
