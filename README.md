# Six-Wheel Builder

[Open the viewer](https://rhs059.github.io/drone_test/).

Source-backed six-wheel engineering viewer with original retained drive/suspension/steering interfaces, body panels and battery/electrical components, plus licensed UR20/Robotiq mechanisms and a separate live MuJoCo gripper experiment.

See [the current assembly record](docs/RECONSTRUCTION.md) and [original source downloads](docs/assets/connected-sources/index.html). Independent front/rear steering, wheel spin and optional unloaded suspension study are executable. Purchased profiles, wheel-seat approval, load/fatigue ratings, complete wiring, UR controller mounting and vehicle operation remain open. The old workshop cradle is disabled because it intersects this revision.

The supported main isolator-to-BMS cable pair has its own [source and limits](docs/assets/main-pair-E05/index.html). Full electrical continuity remains unfinished.

Run `node test-main-pair.mjs`, `node test-real-gltf-body.mjs`, `node test-connected-mechanics.mjs`, `node test-current-rover.mjs`, `node test-composed-body.mjs`, `node test-electrical-scene.mjs`, `node test-rigid-matrix.mjs`, `node test-controls-ready.mjs`, `node test-costs.mjs`, `node test-cad.mjs`, and `node docs/contact/scripts/validate.mjs`. Historical C03 tests and assets are retained as history, not current assembly qualification.

The exact public files are listed in the release manifest. Restricted manufacturer CAD, private credentials and review-only geometry are excluded. Source-specific licenses and original modeling assumptions remain with each package.
