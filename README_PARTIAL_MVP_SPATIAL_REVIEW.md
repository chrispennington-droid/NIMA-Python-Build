# PARTIAL MVP SPATIAL-REVIEW BUILD

- NOT FINAL
- NOT FULL-SCENE MERGE
- UNRESOLVED GEOMETRY EXCLUDED
- GENERATED FROM `scene_partial_expanded_scope_review.json` ONLY
- REMAINING UNRESOLVED ITEMS REQUIRE MANUAL VECTOR CONFIRMATION OR LATER EXPLICIT PROXY APPROVAL

## Source

- `code_inputs/scene_partial_expanded_scope_review.json`

## Output Files

- `build_outputs/partial_mvp_spatial_review/partial_mvp_spatial_review_scene.json`
- `build_outputs/partial_mvp_spatial_review/partial_mvp_spatial_review_plan.svg`
- `build_outputs/partial_mvp_spatial_review/PARTIAL_MVP_SPATIAL_REVIEW_BUILD_MANIFEST.json`
- `build_outputs/partial_mvp_spatial_review/README_PARTIAL_MVP_SPATIAL_REVIEW.md`

## Included Geometry IDs

- `F1-PLATE-PRIMARY`
- `F2-PLATE-PRIMARY`
- `W-F1-MAIN-ENTRY-STOREFRONT`
- `W-F1-SOUTH-WINDOW-BAND`
- `W-F2-NORTH-DESIGNCENTER-GLAZING`
- `W-F1-LAB-CORRIDOR-EAST`
- `W-F1-SUPPORT-CORRIDOR-WEST`
- `W-F2-HIGHBAY-OPEN-BELOW-BOUNDARY`
- `W-F2-SUPPORT-WEST`
- `W-F2-LARGE-MEETING-EAST`
- `W-F2-PROJECT-SOUTH`
- `W-F2-PROG-LAB-WEST`
- `W-F2-PALETTE-STORAGE-WEST`

## Excluded Unresolved IDs

- `W-F1-CONNECTOR-CLOSE`
- `W-F1-OFFICE-CORRIDOR-WEST`
- `W-F1-RR-JAN-NORTH`
- `CND-F1-ABY`
- `W-F2-LAB-CORRIDOR-EAST`
- `W-F2-RESEARCH-NORTH`
- `W-F2-MEZZ-STOR-WEST`
- `W-F2-STAIR-CORRIDOR`
- `CND-F2-ABW`
- `CND-F2-AAU`
- `CND-F2-OPEN-LOBBY`
- `CND-F2-LOADING-BELOW`
- `CND-F2-TERRACE`

## Locked / Read-Only Context Preserved

- locked high-bay geometry
- finalized stair-opening polygon
- sealed Existing Tyler references
- `W-F2-HIGHBAY-OPEN-BELOW-BOUNDARY` metadata/provenance preserved

## Validation

- `building_envelope.json` valid JSON: `True`
- `scene_partial_expanded_scope_review.json` valid JSON: `True`
- duplicate-key audit `building_envelope.json`: `0`
- duplicate-key audit `scene_partial_expanded_scope_review.json`: `0`
- inclusion audit missing IDs: `[]`
- inclusion audit extra IDs: `[]`
- exclusion audit unresolved present in geometry: `[]`
- no unresolved promoted: `True`
- wall thickness rules preserved: `True`
- material rules preserved: `True`
- no stair geometry generated: `True`
- Existing Tyler sealed/no-entry preserved: `True`
- building validation gate: `12/12 PASS`
- full scene merge ready: `False`
- GLB regeneration blocked: `True`

## Known Limitations

- This package excludes all unresolved `NEEDS_VECTOR_CONFIRMATION` geometry.
- This package is suitable for limited spatial review only; it is not a BIM/CD-complete model.
- Read-only context is referenced in metadata/manifest and is not promoted into new geometry.
- The preview scene is derived only from accepted staged geometry and does not resolve missing conditions, stair geometry, or Existing Tyler access.