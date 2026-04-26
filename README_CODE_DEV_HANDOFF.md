# NIMA Phase II Code Development Master Package v1.0

Date: 2026-04-26

## Purpose

This package is the move-forward build baseline for code development of the NIMA Phase II 1:1 spatial-review model.

It consolidates:
- source authority and build standards
- high-bay locked geometry
- stair/open-to-lobby opening polygon
- wall parent coordination rows
- door rules and material overrides
- window/facade deployment baseline
- material finish zones
- QA and code-development tasks

## Controlling workbook

Use `NIMA_Code_Development_Master_Baseline_v1.xlsx` as the human-readable master.

Use the files in `code_inputs/` and `csv_exports/` for code parsing.

## Key locked decisions

- Model intent: lightweight 1:1 spatial-review model, not BIM/CD precision.
- Coordinate units: feet.
- Grid scale: 1 grid unit = approximately 8 ft.
- Interior wall thickness: 0.4167 ft.
- Exterior wall thickness: 1.0000 ft.
- Existing Tyler: sealed/no-entry context.
- Stairs: do not generate stairs; preserve opening/cutout only.
- High-bay geometry: locked rotated parallelogram.
- High/east roof top: 38.9569377990431 ft.
- High-bay floor: cement slab.
- Restroom doors: solid wood matching the warm light woodwork reference photos.
- Covered-loading overhead doors: 3 doors, each 12 ft W x 14 ft H.
- Ignore the earlier temporary 12 ft height estimate for covered-loading doors.

## Package layout

- `NIMA_Code_Development_Master_Baseline_v1.xlsx` — master workbook.
- `code_inputs/` — JSON files for code/model generation.
- `csv_exports/` — CSV table exports of the key master sections.
- `source_schedules/` — latest supporting schedule workbooks.
- `source_drawings_and_references/` — source plan/elevation/reference files used for review.

## Build note

The package is ready for a first-pass code/model build using deployable proxy dimensions. Exact mullion spacing, final vector centerlines, and low/west wall endpoint cleanup can be refined later without blocking the initial model.
