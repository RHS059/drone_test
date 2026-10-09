# Six-Wheel Builder

[Open the viewer](https://rhs059.github.io/drone_test/).

Source-backed six-wheel vehicle development CAD with a faceted serviceable body, original corner hardware, two licensed UR20/Robotiq mechanisms, and a separate live MuJoCo gripper experiment. The current feature branch may contain newer geometry than deployed main.

See [the assembly record](docs/RECONSTRUCTION.md) for exact scope, source classifications and unresolved hardware. Front and rear rack/linkage geometry can be inspected at neutral suspension; actuation force and duty remain unqualified. Motor/shock geometry, full mass/CG, drive/brake/electrical qualification and autonomous assembly/repair are not complete.

Run `node test-steering.mjs`, `node test-controls-ready.mjs`, `node test-costs.mjs`, `node test-cad.mjs`, `node test-rover.mjs`, and `node docs/contact/scripts/validate.mjs`. `test-model.mjs` is a historical estimates regression only. Per-asset source terms and original model assumptions remain with the assets. The release manifest records the exact public source package. No private review-only manufacturer geometry is distributed.
