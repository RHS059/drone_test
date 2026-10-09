# Archived source reference

These BSD-licensed Clearpath Warthog models were acquired for comparison. They are not loaded by the current six-wheel vehicle scene and are not the selected wheel or drivetrain. The selected source-backed wheel model is in ../wheels/. Original four-wheel Warthog ratings do not qualify this six-wheel design.

# Genuine running-gear source assets

Retrieved 2026-10-09 from the official Clearpath Warthog ROS description distribution:
https://github.com/warthog-cpr/warthog/tree/kinetic-devel/warthog_description

## What this contains

- Original OEM-distributed STL simulation meshes: wheel, two-wheel rocker enclosure, fenders, differential link and suspension link.
- GLB conversions in metres, Z up. Wheel, rocker and fender GLBs rotate the source by Z+90 degrees, preserving every triangle and applying NO scale. Remaining links preserve source coordinates. See interface-contract.json.
- Source Xacro graph, package BSD declaration and repository BSD-3-Clause LICENSE.
- Per-file upstream Git blob IDs and URLs in source-manifest.json, actual downloaded SHA256 hashes, triangle counts and bounds in geometry-report.json.

These are CAD-derived source **meshes**, not STEP/B-rep solids or toleranced manufacturing drawings. Wheel geometry is 12,680 triangles. It is not watertight after exact vertex merging; no topology repair or invented hub was introduced.

## License evidence

The root BSD-3-Clause license and robot-description package.xml BSD license are included. The mesh directory listing contains no separate license/exclusion. This is the published distribution's license evidence, not an additional legal opinion or grant of patent/trademark/manufacturing rights. Retain LICENSE in source and redistributed GLB documentation; do not imply Clearpath endorses the new assembly.

## Fit and limitations

Wheel GLB origin is the OEM axle center; axle +Y; nominal tire 610 mm; actual rotating mesh envelope radius 304.931 mm; actual width 254.300 mm. The source's 15 kg mass and radius 300 mm are simulation parameters. Hub bolt circle, pilot, axial mounting plane, rim offset, tire pressure/load curve and radial/axial load limits are NOT verified. Wheel has simplified filled low-poly center faces, but no identifiable lug holes; it does not provide an independent hub or motor assembly. A ray along its axle intersects mesh at sourceX -0.08654228 and +0.001998188 m (GLB Y after rotation), not certified mounting planes. Do not label a newly designed spindle as OEM-compatible without the supplier drawing.

Source Warthog is four-wheel, 1.52 x 1.38 x .83 m. Its whole-vehicle 280 kg base and 272 kg payload do not qualify the sedan-size six-wheel design. Its unmodified rocker holds TWO wheels at 914.734 mm wheelbase and cannot be transplanted onto the six single-wheel stations. Rocker and link GLBs are reference-only unless used in a fully redesigned and verified layout. The source labels the diff-link purely visual and does not model a constrained suspension linkage or motor internals.

## Purchasable candidates, not CAD/fit matches

The OEM manual identifies a 610 mm Argo Turf tire but does not identify an exact stock wheel part. A dealer offers a current 24x10-8 Argo XT115 tire (10002C) at USD380.74 and standard steel mounted left/right assemblies (10002C-STD-LEFT/RIGHT) at USD498.45 each, observed2026-10-09:
https://www.argoadventure.com/10002C--24x10-8--ARGO-XT115--TIRE-ONLY_p_18093.html
https://www.argoadventure.com/Standard-8-Rim-and-Tire_c_3689.html
These are procurement leads only: XT115 is not verified as the source's Argo Turf tire, and no load/bolt/mounting equivalence is established. Price excludes shipping/tax.

A separate dealer identifies Argo125-13BL 8x7 steel rim as five-lug,4.5-inch pattern, but this is NOT proof that the Warthog mesh depicts that rim:
https://adair-argo-sales.myshopify.com/products/rim-8x7-5-bolt-black

Timken32008X official CAD/product lead (not downloaded; page returned410 through web fetch):
https://cad.timken.com/item/tapered-roller-bearings-ts-tapered-single-/tapered-roller-bearings-ts-tapered-single-metric/x32008xm-y32008xm

No suitably sized license-safe motor/geared-hub CAD was acquired. Do not replace this gap with invented internals or a toy motor design.

## Rebuild

Run convert_assets.py with numpy/trimesh available. Exact source mesh arrays are retained; per-vertex visual gray is assigned only for visibility. Validate wheel rotation/contact using interface-contract.json; glTF loader must honor the documented Z-up content, because glTF conventions otherwise commonly assume Y-up.
