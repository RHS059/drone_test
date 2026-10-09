# Current connected-component engineering model

This source revision replaces the earlier omitted motors, bearings, rod ends, rack retention and guided spring mounting with inspectable original/source-dimensioned parts. Six direct-drive wheel interfaces use Jantsa 10005240 / Trelleborg SK-900 dimensions. The source manufacturer motor geometry remains private; the public exterior is an original dimensional model.

## Selected geometry and checks

- 126-node structural assembly; continuous mitered hollow arms, restored eight-screw motor mounts, captured rack liners and extended spring supports.
- 816 joint-hardware nodes, six 20-node drive modules, six guided spring modules and direct rim/tire models. Balls and races follow their distinct motion groups.
- Runtime mechanical graph addresses every selected mechanical part; 27 combined motion states are tested. A graph edge records its actual modeled interface and unresolved engineering gates, rather than treating proximity as retention.
- Retained body panels plus selected battery tray and electrical trough changes compose by name into 287 unique parts. Service view removes 92 cover/fastener parts while retained nutplates remain.
- Six controller case interfaces, isolators, BMS, retained carrier hardware and moving breakout boxes are visible. Actual full harness continuity is unfinished; the two UR OEM DC cases have unresolved mounting interfaces.
- STEP-based, sampled private-motor fit results are published only as scoped numeric reports. Restricted manufacturer geometry is excluded.
- The former workshop cradle intersects the revised wheels and lower supports. Its placement control is disabled; failed evidence is preserved.

## Motion and engineering limits

Normal view starts at neutral. Optional unloaded motion studies use q ±12 degrees, independent front/rear rack ±75 mm and wheel spin. The middle pair remains at neutral suspension. The 200 mm raised display is a free-space viewing offset, not a lifting, ground contact or suspension-force result. Sampling does not prove continuous clearance. No physical actuation or vehicle control is connected.

The wheel-seat B14/M16 application, exact supplier profiles, spring rate/preload, guide fits, long-support loads/fatigue, steering force/duty, battery restraint, weather sealing and electrical safety/control integration remain open. Purchased component internal mechanisms are not reverse-engineered. Buildability, driving, peer assembly and autonomous repair are not established.

## Sources and reproduction

[Complete original source packages](assets/connected-sources/index.html), [selected mechanical contract](assets/connected/mechanical-contract.json), [retained interface graph](assets/connected/retained-graph.json), [body composition](assets/connected-body/body-contract.json), [electrical scope](assets/connected-electrical/electrical-contract.json), [numeric audit whitelist](assets/connected-audit/whitelist.json), and [matched cost/BOM](assets/cost-model/cost_model.json).

Run the repository's selected connected-mechanics, composed-body, electrical-scene, rigid-matrix, readiness, costs and UR source-kinematics tests. Historical C03 tests/assets remain as revision history and do not qualify this revision. The standalone MuJoCo contact experiment remains a separate fixed-base task.

## Cost and mass

The known modeled/catalogue subtotal is partial; complete vehicle mass and center of gravity remain unknown. USD and PLN price references are kept separate. Battery reserve calculations use two 5.12 kWh modules and the dated module-price reference. All hourly values are explicit adjustable scenarios, not measured operating costs or runtime claims.

## Battery terminal correction

[Verified polarity and source proof](assets/battery-polarity/README.md) supersedes the frozen BA02 assumed terminal names. Installed +Y is positive and −Y negative. Runtime labels and isolated colors use this mapping; immutable source aliases are retained for traceability. Geometry and hardware qualification are unchanged.

## Supported main cable pair

E05 adds exactly 98 named cable/support/retention parts and replaces two partitions for four retained glands. Its graph binds 105 actual scene objects across 22 interface edges. Only the isolator-output to BMS-battery pair has modeled jacket routes; upstream battery wiring, conductor/crimp continuity and full-circuit protection remain unfinished. The 40-hole deck, BA02 parts and corrected terminal polarity are unchanged. The known modeled/catalogue subset is 1272.550107 kg; complete vehicle mass and electrical operation remain unverified. Run `node test-main-pair.mjs` for the actual-GLTFLoader composed regression.
