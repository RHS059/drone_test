> Historical initial reconstruction record. For the current six-wheel assembly and steering limitations, see [the current assembly record](docs/RECONSTRUCTION.md).

# Six-Wheel Builder: real-CAD reconstruction R01

[Open the viewer](https://rhs059.github.io/drone_test/).

This is a new reconstruction of the previously unpublished local package, not recovery of that package or reuse of its audit results.

- Actual licensed UR20/Robotiq source meshes, original textures and source joint graphs; executable joint/mimic controls.
- Original parametric frame R06 and adapter R03 B-rep/STEP, source generators and fresh checks.
- Standalone MuJoCo native/WASM contact model, with software parity separated from task success. New nominal/heavy cases pass the 10 mm screen; low-friction case fails. These are new declared experiments, not the earlier lost experiments.
- Explicit GPU fallback: CPU kinematics remains usable where WebGPU/WebGL2 is unavailable. Rendered appearance was not independently verified before initial deployment because the QA executor cannot launch Chromium; post-deploy browser checks are separate.

No whole robot, rated drivetrain, collision-free motion, physical manufacturing release, autonomous assembly or repair capability is claimed. A nominal source-frame mating convention is not tolerance/preload/load qualification.

## Reproduce bounded checks

Run `node test-cad.mjs`, `node test-model.mjs` (historical estimates only), and `node docs/contact/scripts/validate.mjs`. Run contact native/WASM generators and mechanical/asset scripts as documented in their folders. Original robot conversion scripts are in `reconstruction/robots/`; retained upstream source/licences and fresh fixtures are in `docs/assets/robots/`. Source paths may need setting to your workspace; the pinned source commits are in the manifest.

## Licensing

Preserve per-asset notices. UR geometry is subject to the complete graphical-documentation terms at `docs/assets/robots/licenses/UR-GRAPHICAL-TERMS.txt`, including displayed copyright and use notice. Robotiq source, MuJoCo Menagerie assets and Three.js carry their respective notices. No blanket license replaces upstream conditions. No private/review-only coupling STEP is included.

## Supported main cable pair

E05 adds exactly 98 named cable/support/retention parts and replaces two partitions for four retained glands. Its graph binds 105 actual scene objects across 22 interface edges. Only the isolator-output to BMS-battery pair has modeled jacket routes; upstream battery wiring, conductor/crimp continuity and full-circuit protection remain unfinished. The 40-hole deck, BA02 parts and corrected terminal polarity are unchanged. The known modeled/catalogue subset is 1272.550107 kg; complete vehicle mass and electrical operation remain unverified. Run `node test-main-pair.mjs` for the actual-GLTFLoader composed regression.
