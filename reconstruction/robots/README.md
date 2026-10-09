# Rebuild the OEM robot assets

These instructions work from the repository root in a fresh clone. They require
Python 3.12 or newer with `venv`, a POSIX shell and the files already included in
this repository. No Blender, ROS installation, private CAD files, credentials or
manual source-path edits are needed.

This is a new reconstruction. It does not recover the earlier lost package or
reuse that package's audit result. The retained OEM visual geometry is intended
for visualization and kinematic simulation, not a manufacturing release.

## 1. Prepare a Python environment

Run from the repository root:

```sh
python3 -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'"
python3 -m venv .venv-robot-assets
. .venv-robot-assets/bin/activate
python -m pip install -r reconstruction/robots/requirements-build.txt
```

Dependency installation requires access to PyPI. After dependencies are present,
the source-subset build below requires no network access. The original asset
build used NumPy 2.5.3, PyYAML 6.0.3, pycollada 0.9.3 and SciPy 1.17.0.

## 2. Verify the retained source subset

Stay in the repository root. This verifies every retained source file against
the source manifest before it is used:

```sh
python - <<'PY'
import hashlib, json
from pathlib import Path
assets = Path('docs/assets/robots')
manifest = json.loads((assets / 'source-manifest.json').read_text())
for entry in manifest['files']:
    path = assets / entry['path']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != entry['sha256']:
        raise SystemExit(f'Source hash mismatch: {path}')
print(f"Verified {len(manifest['files'])} retained source files")
PY
```

The manifest identifies these source commits:

- UniversalRobots/Universal_Robots_ROS2_Description:
  `6662e15f32c23c12ece57d0050aee9a716e4fc41`
- Robotiq/ros: `adb20dc0048ff2ef51c5a86fe2f7880a8618f099`

A copied source subset is not a Git checkout. File hashes prove agreement with
the retained manifest, while the online method below can independently fetch
the commits from their upstream repositories.

## 3. Build in a fresh temporary directory

The scripts resolve `upstream/`, `dist/` and `conversion-plan.json` relative to
their parent directory. This exact staging procedure provides that layout
without changing the scripts or overwriting the shipped viewer:

```sh
REPO_ROOT="$PWD"
BUILD="$(mktemp -d "${TMPDIR:-/tmp}/six-wheel-robots.XXXXXX")"
export REPO_ROOT BUILD
cp -R reconstruction/robots/scripts "$BUILD/scripts"
cp -R reconstruction/robots/tests "$BUILD/tests"
cp -R docs/assets/robots/source "$BUILD/upstream"
python "$BUILD/scripts/build_metadata.py"
python "$BUILD/scripts/convert_meshes.py"
python "$BUILD/tests/validate_assets.py"
printf 'Rebuilt assets: %s/dist\n' "$BUILD"
```

Expected final test summary: `status: passed`, 17 geometry assets, four arm FK
poses and three gripper FK poses. The largest measured source-vertex difference
in the original reconstruction was approximately `4.42e-8` metres.

The build generates:

- `dist/ur20/`: seven per-link GLB visual meshes
- `dist/robotiq/`: nine gripper-link GLBs and the matching coupling GLB
- `dist/robot-kinematics.json`: source frame graph, limits, mimics and notices
- `dist/fk-fixtures.json`: fresh independently checked transforms
- `dist/geometry-report.json` and `dist/validation-report.json`
- `dist/source/`, `dist/source-manifest.json` and complete `dist/licenses/`

The converter also writes `conversion-plan.json` beside `scripts/` and `tests/`.
No code in these steps publishes files or modifies `docs/`.

## 4. Compare the newly generated GLBs with this release

Keep the same shell, where `BUILD` and `REPO_ROOT` are set:

```sh
python - <<'PY'
import hashlib, json, os
from pathlib import Path
build = Path(os.environ['BUILD']) / 'dist'
shipped = Path(os.environ['REPO_ROOT']) / 'docs/assets/robots'
report = json.loads((build / 'geometry-report.json').read_text())
for entry in report:
    name = entry['asset']
    rebuilt = hashlib.sha256((build / name).read_bytes()).hexdigest()
    released = hashlib.sha256((shipped / name).read_bytes()).hexdigest()
    if rebuilt != released:
        raise SystemExit(f'GLB differs from release: {name}')
print(f'All {len(report)} rebuilt GLBs match the shipped release byte for byte')
PY
```

Validation reports can contain library-version metadata. Compare geometry files
with the command above, and review regenerated reports rather than assuming
that every text file must be byte-identical across different environments.

## Optional: fetch the complete pinned upstream repositories

This is an alternative to copying `docs/assets/robots/source`, not an additional
step inside a source-subset build. Start a separate empty temporary build. It
requires Git and network access to GitHub:

```sh
REPO_ROOT="$PWD"
BUILD="$(mktemp -d "${TMPDIR:-/tmp}/six-wheel-robots-upstream.XXXXXX")"
export REPO_ROOT BUILD
cp -R reconstruction/robots/scripts "$BUILD/scripts"
cp -R reconstruction/robots/tests "$BUILD/tests"
bash "$BUILD/scripts/rebuild.sh"
printf 'Rebuilt assets from upstream commits: %s/dist\n' "$BUILD"
```

The script clones/fetches the two pinned commits, confirms each checked-out
commit, extracts the source subset, converts the meshes and runs the tests.
Do not invoke it in the copied source-subset directory: those folders have no
`.git`, and Git cannot clone over existing source-subset folders.

## Updating the viewer after review

The source-subset build intentionally leaves the existing viewer untouched.
After reviewing a new build, this command copies its generated files into the
viewer asset folder:

```sh
cp -R "$BUILD/dist/." "$REPO_ROOT/docs/assets/robots/"
cd "$REPO_ROOT"
node test-cad.mjs
```

This is only a local file update. Review the diff, run the repository's other
applicable tests, and use its normal authorized commit/deployment process.
Preserve all original source notices and graphical-documentation terms.

## Coordinate and qualification contract

- Units are metres and radians. GLBs retain native right-handed ROS Z-up;
  do not add a Y-up conversion at load time.
- Joint origin order is `T(xyz) * Rz(yaw) * Ry(pitch) * Rx(roll)`, followed by
  joint-axis rotation. Apply `visual.origin` after the link-frame transform.
- `fk-fixtures.json` matrices are row-major 4×4. Three.js `Matrix4.fromArray`
  expects column-major arrays, so transpose/convert when consuming a fixture.
- UR20 has six revolute joints. Robotiq 2F-85 has nine links, six moving joints
  and five mimics. `wrist_3_link → flange → tool0` composes to identity.
- The correct coupling is the source `2f_85/ur_to_robotiq_adapter.dae`, whose
  dedicated URDF specifies zero visual origin and +11 mm to gripper base.
  Its −3 mm outer skirt needs clearance in the custom adapter.
- The project-defined adapter transform and seating remain subject to the
  mechanical interface report. The robot tests do not qualify physical fit,
  tolerances, strength, preload, collisions or robot-specific calibration.
- Source UR20 mass is 64.96 kg, including an explicitly uncertain 4 kg base;
  catalogue 64 kg is retained separately, with no normalization.

Full UR graphical terms and both Robotiq/PickNik BSD notices are retained under
`docs/assets/robots/licenses/`. Original UR texture/logo bytes are embedded in
the GLBs unchanged. Keep the on-screen UR copyright/use notice and the full
terms with the software package. These source meshes confer no blanket
manufacturing license.
