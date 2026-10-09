# Integration handoff — make the Six-Wheel Builder physically connected

Owner of this spec and the checks: Claude. Builder: Aella and her lanes. Each task has a pass/fail test you run yourself;
a task is done only when its test passes on the committed files. Keep all existing rules (no vendor CAD redistribution,
no qualification claims).

## Tools you run (all in this repo)
| Check | Command (repo root) | Pass |
|---|---|---|
| Connectivity | `python docs/assets/mechanical/assembly_check.py --corner` (fast) / no flag (full vehicle) | `0 floating, 0 interferences` |
| Coilover sweep | `python docs/assets/integration/coilover_C02.py` | every sweep row `clashes_mm3: []` |
| Buildability | `python docs/assets/mechanical/dfm_check.py <part>.step` | `PASS` |
| Known-answer | `python docs/assets/mechanical/test_dfm.py` | `PASS` |

Add every new part to `assembly_check.build()` (with its rover.js transform) so connectivity covers it.

## Current state (Claude, this branch)
- `integration/drive_envelope_WD220.*` — public-dimension hub-drive solid. Stator seats on upright face Y797, rotor on adapter face Y928, inside drive-reservation bounds, 0 clashes. **Closes wheel → frame.** Middle-left corner: 58/58 parts connected.
- `integration/coilover_C02.*` — coilover envelope + spring sizing. Motion ratio 0.516 (spring/wheel), stroke 56.5 mm for ±12° (109 mm wheel travel).
  Spring rate at 1.4 Hz ride: 37 / 51 / 71 N/mm for 1300 / 1600 / 2000 kg vehicle.
- **Blocking finding:** the contract coilover line (fixed eye Y560 Z170 → lower eye Y720 Z-367.5) passes **through the hub drive** (≈620 000 mm³ at ride) and clips the stationary clamp (13–990 mm³, worse in bump).

## Task A — relocate the coilover (corner C02 and the steered C03 corners)
Problem above. Requirements:
1. No clash with drive envelope, upright, pins, arms, clamp, wheel, body over the full ±12° sweep (and with steering ±max on C03).
2. Options, pick one and justify: (a) shock ahead of or behind the drive — offset in X by ≥ 140 mm (drive flange half-width 124 + 16 clearance), lower eye on the corresponding lower-arm leg; (b) twin shocks at X ±150 mm; (c) lower eye on the upper arm with a rocker. (a) is simplest.
3. Keep motion ratio 0.45–0.65; recompute with `coilover_C02.py` (update eye points via the contract) and keep the spring-rate table.
4. Select a real 2.0–2.5 in coilover by catalogue: eye-to-eye at ride within its range, stroke ≥ needed + 10 mm, spring rate from the table for the current mass ledger. Record part number, eye width/bushing, source link. No OEM CAD redistribution — envelope only.
5. Pass: coilover sweep has no clashes; connectivity shows the coilover connected (upper eye touches clamp bracket, lower eye touches arm bracket — add real clevis brackets, M12 eye bolts per STANDARD).

## Task B — 48 V power distribution and harness
Requirements (house standard: 48 V LiFePO4 bus, fuse every branch):
1. Batteries: the four RELiON reservations in parallel → two copper busbars (+/−) in the battery well. Model busbars (e.g. 40×6 mm Cu), battery lugs/terminals at the published terminal positions (get them from the datasheet; if unknown, say so and use a declared assumption).
2. Main path: busbar → main fuse (Class T or ANL, rating ≥ 1.25× continuous) → main contactor (≥ 300 A continuous at 48 V, with **precharge resistor + relay**, required because of UR OEM DC 400 A inrush) → distribution block.
3. Branches, each with its own fuse: 6× drive controllers, 2× UR OEM DC controllers, 1× DC-DC 48→24 V and 48→12 V (compute, sensors, fans), e-stop loop.
4. Drive controllers: WD220 needs an external controller — choose a real 48 V controller rated ≥ 47 A continuous (S2 nameplate), place one per corner near the drive (short phase leads) or centrally; justify.
5. Cable sizing (copper, ≤ 3 % drop, ampacity with ≥ 25 % margin):
   - trunk ~300 A → 70 mm² (2/0 AWG): 1 m out+back ≈ 0.49 mΩ → 0.15 V at 300 A.
   - each drive feed 47 A → 10 mm² (≈7 AWG): 2 m run out+back ≈ 6.9 mΩ → 0.32 V (0.6 %).
   - UR feeds per UR inrush/continuous data; DC-DC per its input current.
   Use `cad_stuff/generators/wire.py` (`route(awg, points, od)`) or equivalent sweeps with bend radius ≥ 6× cable OD. Routes go through the existing cable troughs and body pass-throughs, clipped every ≤ 300 mm.
6. Connectors: XT90 / Anderson SB per STANDARD for removable modules; M12 for outdoor signals; CAN-FD daisy chain to every drive controller + BMS.
7. Pass: an electrical connectivity table (JSON) where every load has a path battery → fuse → contactor → its fuse → load, every cable has gauge/length/drop, and every cable solid touches its two terminals in the connectivity check. Viewer shows the harness layer.

## Task C — viewer
1. Load `integration/drive_envelope_WD220.glb` at every corner (same transforms as the drive reservation; right corners via Rz(pi)), and the coilover once Task A passes.
2. Load the bearing envelopes (currently skipped in rover.js) or real bushing solids, so wishbones don't float.
3. Battery reservations visible by default with the harness layer; label "dimension-only" where true.
4. Pass: screenshot QA from all corners shows no visible gaps between wheel, drive, upright, arms, clamp, frame.

## Task D — body panels
17 body solids float 4–30 mm off supports (hatch/cover nodes). Add the fasteners/hinges/latches that hold them (nutplates + M6 screws are already provisioned) so each removable panel touches its holder. Pass: full connectivity run, 0 floating.

## Task E — flange protrusion regression (small)
Add a test: adapter grip = head-seat Z − UR face Z (R04: 11.5 mm); for the chosen ISO 4762 M8 length, protrusion = L − grip ≤ 7 mm (UR limit) and ≥ 4 mm engagement. Today only M8×16 (4.5) and M8×18 (6.5) pass. Fail CI if the selected length violates it.

## Task F — tire-change drone v0 (after A–C)
Design per `RHS059/cad_stuff/designs/tire_drone/MAINTENANCE.md` and `STANDARD.md`, from `cad_stuff` parts (wheels by size code, lug sockets/nuts, house LRU plate, NEMA/BLDC, fans, etc.). Every LRU ≤ 4 fasteners, ≤ 15 kg or lift points. Pass: connectivity 0 floating, DFM pass on all original parts, and a written test of each job step (jack, unbolt, lift wheel, swap, torque, inflate) with the forces from MAINTENANCE.md.

Report progress in the thread; Claude reviews each task with the checks above.
