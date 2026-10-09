# Original source-backed rover wheel C01

An editable CadQuery tire/rim assembly tied to the published major dimensions of the selected BFGoodrich KM3 72204 tire and EVO Corse SE5240060141 rim. Two valid B-rep solids; source-scale GLB in metres with explicit Z-up and +Y axle convention. A useful dimensional fit candidate with honest detail assumptions, not OEM CAD or production approval.

## Deliverables

- `build_wheel.py`: native parametric construction and export source
- `parameters.json`: dimensions, including clearly named assumptions
- `wheel_C01.step`: named tire/rim assembly, millimetres
- `tire_C01.step`, `rim_C01.step`: individual millimetre solids
- `wheel_C01.glb`: separate tire and rim nodes, metres; Z up, axle +Y
- `interface_contract.json`: mounting plane, bolt coordinates, axes and fit gaps
- `verification.json`: measured bounds, solid validation, overlap and interface tests
- `SOURCES.json`: exact public source URLs and provenance
- `ASSUMPTIONS.md`: source facts versus original detail and unresolved fit
- `SHA256SUMS`: deliverable hashes

Run with Python, CadQuery 2.7 and numpy: `python build_wheel.py`. No internet, supplier file, extra geometry library, or protected mesh is required to rebuild. The output is deterministic geometry; STEP header timestamps can differ between builds.

## Important fit facts

Measured tire OD used is 876.3 mm, not nominal 889 mm. The retained 317.5 mm tire section width was measured on a 254 mm rim and remains unverified on the selected 215.9 mm rim. Both outside dimensions remain provisional in this fit model. Rim mounting plane is +18 mm outboard of wheel center. Five assumed 18 mm lug clearance holes lie on the published 165.1 mm PCD, clocked 36 degrees from +X toward +Z. The bore is nominally 114.1 mm. A separate adapter is required for the WD220's different 140 mm PCD / 94 mm pilot.

The original perforated wheel disc and generic tread are deliberately not marketed as the appearance of either manufacturer's product. A supplier STEP request or measurement program is needed before true OEM detailed CAD accuracy is possible. Ratings of the selected catalog parts do not transfer to this original geometry or the vehicle.

## License / provenance

The authored Python source, explanatory text, JSON, STEP and mesh geometry in this directory are original work prepared for this project. They may be reused and modified for the user's rover project. No additional permission or endorsement from BFGoodrich, Michelin, EVO Corse or their distributors is represented. Names and part numbers identify dimensional references only; applicable manufacturer names and marks belong to their owners. No third-party geometry or logos are distributed. Public dimensional facts are cited in `SOURCES.json`; the manufacturers' source documents remain subject to their own terms and are not relicensed here.
