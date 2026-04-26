# Ready-to-Code Handoff Prompt Outline

Use this package to generate a lightweight 1:1 spatial-review model for NIMA Phase II.

## Primary input

Read `code_inputs/nima_master_build_config.json` first. It contains the consolidated build standards, geometry locks, high-bay vertices/walls, stair opening polygon, door rules, facade/window baseline, material rules, and QA register.

## Coordinate and unit setup

- Use feet as model units.
- Convert grid values using 1 grid = 8 ft when needed.
- Treat all dimensions as deployable proxies for spatial review, not CD-grade construction geometry.

## Build sequence

1. Initialize the model coordinate system.
2. Create the sealed Existing Tyler context as a no-entry mass/boundary.
3. Create the new building as one connected building.
4. Create the high-bay shell from the locked high-bay vertices:
   - HB-V1 = (91, 126)
   - HB-V2 = (151, 116)
   - HB-V3 = (120, -56)
   - HB-V4 = (60, -46)
5. Use 1.0000 ft exterior walls and 0.4167 ft interior partitions.
6. Create floor surfaces:
   - high-bay = cement slab
   - all other new areas = uniform refined floor material
7. Cut the F2 stair/open-to-lobby opening using the four-vertex stair opening polygon.
8. Do not generate stair geometry.
9. Place door/opening proxies:
   - typical 3 ft / 6 ft simplification as scheduled
   - restroom doors are solid warm light wood
   - covered-loading overhead doors are three 12 ft W x 14 ft H sectional doors
10. Place window/facade proxies from `window_facade_baseline.json`.
11. Apply materials:
   - warm off-white painted walls throughout
   - no wood trim in high-bay production area
   - refined wood/lobby feel at high-bay overlook, lobby, connector, and entry
12. Add review labels and optional presentation boards for stakeholder walkthrough.

## QA

Do not fail the build on exact mullion spacing or final vector centerline refinements. Use the QA register to flag those as later refinements.
