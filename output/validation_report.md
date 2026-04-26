# NIMA Phase II — First-Pass Build Validation Report

- Pass: **minimal_first_pass**
- Generated: 2026-04-26T23:49:13.491432+00:00
- Package: NIMA Code Development Master Package v1.0 (2026-04-26)

## 1. Locked geometry — computed vs. baseline

| Metric | Baseline (package) | Computed | Match |
|---|---|---|---|
| High-bay perimeter (LF) | 471.2 | 471.1978 | OK |
| High-bay footprint (SF) | 10630 | 10630.0 | OK |
| Roof / east top (ft) | 38.9569377990431 | 38.9569377990431 | OK |
| Stair opening area (SF) | ~433 | 433.5 | OK |

## 2. Locked assumptions applied

- STD-001: Purpose / LOD = Lightweight 1:1 spatial-review model for adjacency, circulation, workflow, equipment fit, and stakeholder discussion
- STD-002: Units = Feet for all model output dimensions
- STD-003: Building treatment = One connected building
- STD-004: Existing Tyler = Sealed / no-entry in simplified model
- STD-005: Interior wall thickness = 0.4167 ft / 5 in
- STD-006: Exterior wall thickness = 1.0000 ft / 12 in
- STD-007: Default floor material = Use one consistent refined floor material throughout new non-high-bay areas
- STD-008: High-bay floor material = Cement slab
- STD-009: Wall finish = Warm off-white / neutral painted walls throughout, including high-bay
- STD-010: High-bay trim = No wood fixtures/trim in high-bay production area
- STD-011: High-bay overlook finish = Refined lobby/connector feel allowed, including light wood trim
- STD-012: Restroom doors = Solid wood, warm light woodwork match
- STD-013: Default doors = Glass/aluminum where scheduled, except restroom wood doors and high-bay/service doors
- STD-014: Covered-loading overhead doors = 3 overhead/sectional doors, each 12 ft W x 14 ft H
- STD-015: Stairs = Do not auto-generate stairs
- STD-016: High/east roof top = 38.9569377990431 ft controlling value
- STD-017: Small-room ceilings = Sub-500 SF rooms use suspended ceilings at 13.1144 ft except named exceptions
- STD-018: Door/window placement rule = Use door/window centerpoints or visual evidence; do not force midpoint of parent wall
- GEO-001: High-bay footprint (LOCKED_DEPLOYABLE_BASELINE)
- GEO-002: High-bay vertices (LOCKED_DEPLOYABLE_BASELINE)
- GEO-003: High-bay roof/east top (LOCKED)
- GEO-004: F2 stair/open-to-lobby opening (FINALIZED_DEPLOYABLE_PROXY)
- HighBay vertices HB-V1..V4 match locked baseline (clockwise order)
- Roof/east top = 38.9569377990431 ft
- F2 stair/open-to-lobby opening: 4-vertex polygon, slab cut only, no stair mesh
- DR-DEFAULT-GLASS: Typical new interior/exterior scheduled glass doors (Glass / aluminum where scheduled)
- DR-DOUBLE-GLASS: Double doors / major entry pairs (Glass / aluminum storefront or pair)
- DR-RESTROOM-WOOD: Restroom doors (Solid wood, warm light woodwork match)
- DR-HIGHBAY-OVERHEAD: Covered loading overhead doors (Overhead sectional doors)
- DR-EXISTING-BLOCKED: Existing Tyler connectors (Reference only / blocked)
- Material MAT-NEW-GENERAL present
- Material MAT-HIGHBAY present
- Material MAT-OVERLOOK present
- Material MAT-RESTROOM-DOOR present
- Material MAT-STOREFRONT present

## 4. Errors

None.

## 5. Proxy flags (acceptable for first pass, refine later)

- HB-W-005 Interior partition is DEPLOYABLE_PROXY — start/end vertices defer to wall schedule
- QA-003: Stair opening polygon (FINALIZED_PROXY)
- QA-005: Window/facade dimensions (MOVE_FORWARD_BASELINE)
- QA-006: Exact mullion spacing (DEFERRED)
- QA-007: Low/west exact wall endpoints (DEPLOYABLE_PROXY)

## 6. Inferred assumptions (NOT locked in package — please confirm)

- **f2_floor_ft** = 14.0  
  Reason: Inferred from facade window sill data: F1 windows head ~14 ft, F2 lower windows sill = 14 ft, F2 project-room windows sill = 14 ft. Not explicitly locked in the package.
- **non_highbay_envelope** = not_built  
  Reason: Package gives wall_schedule parent rows but no endpoint coordinates for the new non-high-bay portion. First pass intentionally skips fabricating coordinates; needs vector extraction from SVG plans.
- **roof_pitch** = flat_cap  
  Reason: GEO-003 locks roof top elevation only. No pitch/parapet detail in the package; first pass uses a flat cap.
- **openings_centerpoints** = centered_on_parent_wall_or_evenly_spaced  
  Reason: STD-018: use centerpoints or visual evidence. Package does not give per-element centerpoints. First pass centers on parent wall, and evenly distributes the 3 covered-loading overhead doors.

## 7. Openings — placed and unplaced

- Placed: 8 (of which 6 produced render meshes; the rest are coordination references)
- Unplaced (pending non-high-bay envelope): 15

### 7a. Placed (high-bay-anchored)

| Element | Parent wall | Type | W x H | Sill / Head | Status |
|---|---|---|---|---|---|
| NF-001 | HB-W-001 | Large translucent/panelled opening | 51.2 x 32.0 | 4.0 / 36.0 | DEPLOYABLE_PROXY |
| NF-002 | HB-W-001 | Vertical dark accent strip | 8.0 x 36.0 | 0.0 / 36.0 | COORDINATION_REFERENCE |
| SF-008 | HB-W-003 | Overhead sectional door | 12.0 x 14.0 | 0.0 / 14.0 | LOCKED |
| SF-009 | HB-W-003 | Overhead sectional door | 12.0 x 14.0 | 0.0 / 14.0 | LOCKED |
| SF-010 | HB-W-003 | Overhead sectional door | 12.0 x 14.0 | 0.0 / 14.0 | LOCKED |
| SF-011 | HB-W-003 | High-bay patterned/translucent window | 24.0 x 11.2 | 14.0 / 25.2 | DEPLOYABLE_PROXY |
| EF-001 | HB-W-002 | Vertical window / screened opening | 8.0 x 32.0 | 4.0 / 36.0 | DEPLOYABLE_PROXY |
| EF-002 | HB-W-002 | Ornamental facade treatment | 8.0 x 32.0 | 4.0 / 36.0 | COORDINATION_REFERENCE |

### 7b. Unplaced (need new-building envelope coordinates)

| Element | Face | Zone | W x H | Reason |
|---|---|---|---|---|
| NF-003 | North | F2 Design / Discovery | 62.4 x 23.2 | no high-bay parent wall identified |
| NF-004 | North | Main entry / vestibule | 8.8 x 30.4 | no high-bay parent wall identified |
| NF-005 | North | Entry canopy / connector edge | 25.6 x 9.6 | no high-bay parent wall identified |
| SF-001 | South | Connector / new entrance | 11.2 x 7.2 | no high-bay parent wall identified |
| SF-002 | South | Secure Access / connector | 12.8 x 4.8 | no high-bay parent wall identified |
| SF-003 | South | Open stair / lobby | 4.0 x 27.2 | no high-bay parent wall identified |
| SF-004 | South | Second-floor office/lab rooms | 10.4 x 10.4 | no high-bay parent wall identified |
| SF-005 | South | First-floor office/lab rooms | 10.4 x 10.4 | no high-bay parent wall identified |
| SF-006 | South | Open stair / lobby | 7.2 x 32.0 | no high-bay parent wall identified |
| SF-007 | South | High-bay support/lab interface | 26.4 x 9.6 | no high-bay parent wall identified |
| IG-001 | Interior/F2 | Project Room 1 north/sloped exterior wall | 12.0 x 8.0 | no high-bay parent wall identified |
| IG-002 | Interior/F2 | Project Room 2 north/sloped exterior wall | 12.0 x 8.0 | no high-bay parent wall identified |
| IG-003 | Interior/F2 | Covered Terrace north/sloped wall | 28.0 x 8.0 | no high-bay parent wall identified |
| IG-004 | Interior/F2 | High-Bay Overlook end wall | 10.0 x 8.0 | no high-bay parent wall identified |
| IG-006 | Interior/F2 | High-Bay Overlook open-to-below edge | 20.0 x 4.0 | no high-bay parent wall identified |

## 8. Missing / ambiguous inputs (blocking full build)

The package locks the high-bay shell, the F2 stair-opening polygon, all material rules, all door rules, and 12x14x3 covered-loading doors. The following are not locked and are needed to complete the model beyond the minimal first pass:

1. **New non-high-bay building envelope coordinates.** The wall schedule names parent segments (storefront, south window band, F2 north design-center glazing, F2 high-bay open-below boundary) but gives no endpoint coordinates. SVGs/PDF would need to be vector-extracted to draw the rest of the connected building.
2. **F2 floor elevation.** Inferred at 14.0 ft from facade window sill data; not explicitly locked. Please confirm or provide a value.
3. **HB-W-005 interior partition endpoints** (DEPLOYABLE_PROXY). Listed as 'see wall schedule' for start/end vertices. Need a 2D centerline to extrude.
4. **Per-element placement on individual walls** (STD-018 says use centerpoints / visual evidence). For the first pass, elements are centered on their parent wall and overhead doors are evenly spaced. Visual cross-check against SVGs may shift these.
5. **Roof shape** beyond a flat cap. Package locks roof top elevation but not pitch / parapet / transition to lower mass.
6. **Existing Tyler context mass extents.** STD-004 says sealed/no-entry; the first pass does not yet emit a context boundary mesh.

## 9. Recommended next development step

Vector-extract the new non-high-bay outline from the F1 + F2 SVG schematics and the elevation SVG, store as a new `building_envelope.json` input alongside the master config, and re-run the build. After that, all currently unplaced facade elements can attach to real parent walls.
