# Wheel C01 assumptions and limits

This is an original, source-backed parametric fit-development model. It is not manufacturer CAD, reverse-engineered OEM detail, a manufacturing drawing, or approved hardware. It deliberately does not reproduce the KM3 tread or EVO Corse paired-spoke design. No manufacturer logo, lettering, scan, downloaded wheel mesh, or proprietary CAD was used.

## Published dimensions used directly

- Tire selection: BFGoodrich Mud-Terrain T/A KM3, MSPN 72204, 35x12.50R18/E 123Q.
- Published overall diameter 34.5 in (876.3 mm), section width 12.5 in (317.5 mm), measured on a 10 in rim. Permitted rim width 8.5–11 in. Tread depth 18/32 in (14.2875 mm).
- Rim candidate: EVO Corse DakarZero SE5240060141, 18 x 8.5 in. Nominal bead-seat diameter 457.2 mm and width 215.9 mm. Offset +18 mm, five mounting holes on a 165.1 mm pitch circle, nominal center bore 114.1 mm. Flat nut seats.
- Published matching nut CM0750180040: M16x1.5, flat washer, 27 mm hex, 51.5 mm overall length and 38.5 mm exterior diameter. Nuts are not included in this asset.

## Provisional envelope

The tire dimensions above were measured by its manufacturer on a 10 in rim. This model changes bead spacing to 8.5 in while retaining those published outside dimensions as an explicitly provisional fit envelope. Actual inflated width, OD, sidewall shape and loaded radius on the selected rim must be measured or obtained from the manufacturer. Retaining the published dimensions does not establish conservatism. The nominal 35 in size is not used as the measured diameter.

## Original assumed construction

- Bead, sidewall, inner cavity, ply/cord omission and crown shape are original simplified geometry. They do not establish air sealing, pressure retention, wear, stiffness or bead retention.
- Tread is 160 original annular-sector blocks, four rows of 40. Pattern, block width, gaps, shoulder treatment and carcass thickness are assumptions. Only nominal radial depth is derived from the databook.
- Rim dropwell, hump, flange height and thickness, barrel thickness, perforated dish, vent holes, all fillets and final mass are unknown. The original five-window dish is intentionally different from the OEM paired-spoke appearance.
- Model flange height 16 mm, flange axial thickness 7 mm, barrel wall about 8 mm. These are construction assumptions, not J-profile/ETRTO compliance claims.
- Lug clearance holes are assumed 18 mm. The mounting pad is assumed 20 mm thick; its inboard face is y=18 mm and outboard flat washer seats are y=38 mm. Hole size, actual washer bearing area, pad thickness, stud projection, thread engagement and fit tolerances remain unverified.
- Lug phase 36 degrees in the XZ plane, measured from +X toward +Z, is an original integration choice to alternate with the drive adapter's input pattern. It has no OEM significance.
- No valve, beadlock, fasteners, finish thickness, casting draft, porosity, air channels, stamping, tire cord, balance weights, fillet stress concentrations or manufacturing tolerances are modeled.

## Assembly contract

Wheel center is the origin; +Y is axle/outboard, X forward and Z up. Left wheel mounting plane is local y=+18 mm. On the right side use a proper 180 degree rotation about Z, followed by translation. No reflected geometry or source scaling is allowed. GLB contains metres with the stated Z-up engineering convention; STEP and native source use millimetres. The GLB has separate tire and rim nodes.

A WD220 drive has a different five-hole 140 mm PCD and 94 mm pilot. It cannot directly fit this rim. The separate original adapter model must handle the mismatch. This asset includes no adapter and does not certify it. Nominal bore contact is not a finished fit specification.

## Ratings and release gate

The databook lists 3415 lb at 75 psi for the selected tire. The exact official rim page lists 1400 kg per wheel. Those are catalog component ratings under their stated conditions, not ratings of this original geometry, adapter, hub, suspension or complete rover. The model has not been structurally analyzed or certified. Do not manufacture or order an adapter from this fit model without supplier drawings, measured fit checks, fastener design, load cases, pressure safety and engineering review.
