# BA02 polarity correction R01

This separate correction establishes the functional polarity of the four existing BA02 terminal interfaces. It changes viewer labels and semantic terminal colors only. It does not modify the frozen BA02 CAD, source generator, geometry, transforms, source node names, or original source/evidence ZIP. No vendor PDF, image, mesh, logo or manufacturer geometry is included.

## Result

In the installed BA02 frame, positive is **Y +275.25 mm** and negative is **Y −275.25 mm** on both batteries. The original node names assigned these polarities backwards.

| Frozen source alias, retained unchanged | Verified functional polarity | Terminal-axis top in CAD C, mm | Viewer color |
|---|---|---|---|
| `BA02_pack_1_negative_M8_interface` | Positive (+) | (−1029.05, +275.25, 169.6) | Red `#e53935` |
| `BA02_pack_1_positive_M8_interface` | Negative (−) | (−1029.05, −275.25, 169.6) | Dark `#20252b` |
| `BA02_pack_2_negative_M8_interface` | Positive (+) | (−679.05, +275.25, 169.6) | Red `#e53935` |
| `BA02_pack_2_positive_M8_interface` | Negative (−) | (−679.05, −275.25, 169.6) | Dark `#20252b` |

These colors are a deliberate viewer convention, not source evidence about physical terminal coating or insulation color. The frozen source used a shared bronze terminal material for both polarities and the top fittings.

## Exact source and orientation proof

The official Victron Energy BAT548110620 drawing is [LiFePO4 Battery 51.2 V / 100 Ah NG, Dimension Drawing](https://www.victronenergy.com/upload/documents/LiFePO4-Battery-51.2V100Ah-NG.pdf), page 1, top plan view. Its rendered polarity marks were visually inspected on 2026-10-09: positive on drawing-left and negative on drawing-right.

Exact inspected PDF SHA-256:

`d153636d0bb1cb84ea4c3c339746618c97fd02859398404febbc8a92a2a27d4b`

1. The drawing's overall width is 647.6 mm. Its asymmetric top fitting is 376.3 mm from the left edge, hence 376.3 − 647.6 / 2 = **+52.5 mm toward drawing-right**.
2. The frozen BA02 fitting center is **Y −52.5 mm** on both packs. Therefore drawing-right maps to **CAD −Y**. The asymmetric fitting, not terminal names or existing wires, resolves the orientation.
3. Positive is on drawing-left, so it maps to **Y +275.25 mm**. Negative is on drawing-right, so it maps to **Y −275.25 mm**. The absolute axis offset is the frozen symmetric terminal pitch, 550.5 / 2 = 275.25 mm.
4. The terminal depth-edge offset establishes X = pack center − (161.5 / 2 − 26.7) = pack center −54.05 mm. Pack centers are X −975 and −625 mm.
5. Z 169.6 mm is the preserved BA02 terminal-reservation top. It is not a newly qualified hardware height. The existing source-height discrepancy remains unresolved.

The drawing's rounded 48.5 mm end offset differs by 0.05 mm from its symmetric pitch-derived location. This metadata-only correction preserves the frozen axis placement. The source/mesh regression uses a 0.01 mm tolerance only for tessellated-circle extrema and float32 mesh positions; exact manifest and contract dimensions use 1e-7 mm tolerance.

The frozen generator's note that installed polarity is an orientation choice is superseded by this correction. Its legacy names remain trace aliases only. Do not use those words to infer electrical polarity.

## Runtime integration

Copy `apply-battery-polarity.mjs` and `battery-polarity-contract.json` together with the viewer's original runtime assets. After all named body patches have composed BA02 and the normal asset loader has assigned its labels, call:

```js
import { applyBatteryPolarity } from './apply-battery-polarity.mjs';
const polarityContract = await fetch('./battery-polarity-contract.json').then(r => {
  if (!r.ok) throw new Error('Battery polarity contract unavailable');
  return r.json();
});
const polarityResult = applyBatteryPolarity(body, polarityContract);
```

`body` is the composed source-frame Object3D, not a newly generated or moved battery. The helper is import-free and supports Three.js Object3D and Material APIs already used by the viewer. It:

- Validates the exact drawing hash, source dimensions, marked sides, asymmetric-fitting sign, all four functional mappings, labels, colors and open qualification gates.
- Resolves all four legacy aliases uniquely before staging changes. Missing or duplicate source nodes throw without modifying the scene.
- Stages all material clones and metadata before applying them. A late clone failure leaves the scene unchanged. Each cloned material must have its own color object.
- Retains each `node.name` exactly, and stores its source alias and verified functional identity under `userData.batteryPolarity`.
- Sets `userData.label` and `userData.displayLabel` on each terminal source node and every descendant mesh, so the viewer's mesh-selection label reports the functional polarity.
- Gives every corrected mesh an independent cloned material; array materials are supported. It does not recolor shared original metal, either top fitting, or unrelated hardware.
- Never writes geometry, node names, hierarchy, position/quaternion/scale, visibility, local/world matrices or update flags.

The proposed functional identity is `BA02_pack_{1,2}_{positive,negative}_M8_interface_VERIFIED_R01`. This is metadata only, not a silent runtime `node.name` rename. A circuit or endpoint graph must retain the exact source alias for geometry resolution and use the verified functional polarity/name for its electrical semantics. Existing cable paths do not establish polarity or authorize their own connections. The electrical owner must separately reconcile any affected edge labels and endpoints.

Suggested viewer download notice:

> Frozen BA02 CAD keeps its original source node names, which invert the terminal polarity wording. The viewer applies the separate BA02 polarity correction R01: positive Y +275.25 mm and negative Y −275.25 mm. Consult the correction map before using terminal names. Wiring and terminal/lug qualification remain open.

Link that notice directly to this correction package when publishing the immutable BA02 download.

## Regressions and preserved inputs

`battery-polarity-contract.json` records the source facts, derivation, source-to-functional map, labels/colors, gates and SHA-256 hashes of all 17 frozen inputs, including the BA02 generator, all frozen BA02 artifacts and original archive.

Run the independent, read-only source/mesh regression from any directory:

```sh
python verify-source-polarity.py --ba02-root /path/to/battery-alternative --source-pdf /private/path/to/official-drawing.pdf
```

The PDF argument is optional for a redistributable text-only package. When supplied, its exact bytes are hash-verified without copying it. Without it, the report explicitly says `not_supplied`; the script does not claim a fresh PDF verification. The script checks actual GLB vertices, the asymmetric fitting, four terminal positions, functional polarity, semantic colors and preservation of all frozen hashes. It does not machine-read the plus/minus artwork; that observation comes from visual inspection of the hashed source document.

Run the runtime regression in the original workspace layout:

```sh
node test-battery-polarity.mjs
```

For another workspace, point `THREE_MODULE`, `CAD_READER_MODULE`, and `BA02_GLB` to existing viewer dependencies and the frozen BA02 GLB. The reader must return Three.js Object3D meshes in unchanged source coordinates. No dependencies or vendor meshes are bundled here.

The recorded runtime result passes 14 tests against the actual frozen BA02 GLB: source/fitting derivation; measured terminal/fitting positions; all four labels/colors; preserved geometry/matrices; shared-material isolation including array materials; missing-node and duplicate-node atomic failure; late clone failure; shared-color clone rejection; reversed-source/coordinate/gate negative tests; and repeat application.

Files `source-regression-results.json` and `runtime-regression-results.json` are bounded test evidence, not certificates of a working electrical assembly.

## Qualification limits

Only polarity interpretation is source-verified. The following remain false or open:

- Terminal hardware, recess, lug, bolt and cable-contact qualification
- Full harness completion and physical electrical continuity
- Protection, BMS, fusing, isolation, controls and conductor selection
- The underlying source-height discrepancy or exact vendor hardware reconstruction
- Vehicle operational or electrical safety qualification

No cable continuity test is used as proof of polarity, no physical reconnection is performed, and no complete-wiring gate is closed by this patch.
