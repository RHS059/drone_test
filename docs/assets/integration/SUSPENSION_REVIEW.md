# C04 suspension review (Claude)

Numbers from `node docs/assets/integration/suspension_review.mjs`, which runs the viewer's own `kinematics_C04_R03.mjs`.

## How it works
- Six double-wishbone corners on clamps around the frame rails. Equal, parallel upper/lower links (0.302 m), so the
  upright translates without camber change. Declared range ±12° arm rotation = −51 / +58 mm wheel travel (109 mm total).
- Front and rear pairs steer: vertical kingpin, tie rods to a rack carriage driven by a Thomson Electrak HD candidate,
  max 20° at ±75 mm rack. Middle pair is fixed (skid/Ackermann compromise not analysed).
- Spring/damper: 2.0-in class shock with Eibach 1800.300.0200S (200 lb/in = 35 N/mm, 457 mm free, 161 mm block).
  To clear the hub drive, the shock is moved 550 mm forward (steered corners) / 350 mm (middle) of the arm station;
  the lower arm and clamp are lengthened to reach it. Motion ratio 0.517 → wheel rate 9.4 N/mm.

## Findings (largest first)
1. **Spring only suits a 1.6–2.0 t vehicle.** At 1.6 t the spring sits at 361 mm (inside the 300–370 mm screened
   range); at 2.0 t 325 mm; at the 2.92 t workshop stress case 242 mm (outside the range); at 3.94 t 151 mm, below the
   161 mm block height = coil bind. Close the mass ledger, then size rate/preload (or dual-rate) to it.
2. **Ride height is very mass-sensitive.** 9.4 N/mm wheel rate means each extra 100 kg of vehicle mass drops each corner
   ~17 mm, against only 109 mm total travel. Payload, arms and batteries will move ride height a lot.
3. **Spring load is applied on a 380 mm cantilever.** The lower eye sits at X 1.90 m, 380 mm beyond the front arm bushing
   (X 1.52). At 3.4–7.5 kN spring force that is 1.3–2.9 kN·m bending in the arm extension and roughly 2× spring force
   prying the front bushing. Heavy and fatigue-prone; shocks normally load the arm between the bushing line and the
   ball joint.
4. **High scrub.** Links are inclined ~30° at ride, so the wheel moves 0.57 mm sideways per mm of bump
   (−37 / +26 mm track change per side). Tyre scrub, jacking and a high roll centre. Aim for ≤ 0.1–0.2 near ride
   (links near horizontal at ride, or tuned unequal lengths).
5. **186 mm kingpin-to-wheel offset with a vertical kingpin.** Large scrub radius → high static steering torque and
   kickback through the rack on a ~200–400 kg corner. Add kingpin inclination and/or reduce offset; size the actuator
   force from the resulting steering torque.
6. OK: tyre-to-spring clearance ≥ 87 mm across full travel × steer; no bump stops are modelled yet (travel limits are
   software only).
