"""
Phase 5 — Validation report.

Produces a human-readable report (Markdown) and a structured JSON report
showing which locked assumptions were applied, which proxies were used,
which inputs are missing/ambiguous, and the geometric outputs that match
the locked baselines.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import NIMAConfig
from .scene import SceneBuild


def build_report_dict(scene: SceneBuild) -> dict[str, Any]:
    cfg = scene.config
    placed = scene.openings.placed
    unplaced = scene.openings.unplaced

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pass_label": scene.pass_label,
        "package": {
            "name": cfg.raw["package"]["name"],
            "version": cfg.raw["package"]["version"],
            "date": cfg.raw["package"]["date"],
        },
        "locked_assumptions_applied": scene.validation.locked_applied,
        "warnings": scene.validation.warnings,
        "errors": scene.validation.errors,
        "proxy_flags": scene.validation.proxy_flags,
        "inferred_assumptions": scene.inferred_assumptions,
        "high_bay_geometry_check": {
            "expected_perimeter_lf_proxy": cfg.high_bay_meta["perimeter_lf_proxy"],
            "computed_perimeter_ft": round(scene.highbay.perimeter_ft, 4),
            "expected_footprint_sf_proxy": cfg.high_bay_meta["footprint_sf_proxy"],
            "computed_footprint_sf": round(scene.highbay.footprint_sf, 1),
            "expected_roof_top_ft": cfg.high_bay_meta["roof_top_ft"],
            "computed_roof_top_ft": scene.highbay.roof_top_ft,
        },
        "stair_opening_check": {
            "expected_area_sf": scene.config.stair_opening_meta.get("Approx_Area_SF"),
            "computed_area_sf": round(scene.stair.area_sf, 1),
            "f2_floor_ft_used": scene.stair.floor_elev_ft,
        },
        "openings_summary": {
            "placed_count": len(placed),
            "unplaced_count": len(unplaced),
            "rendered_count": sum(1 for p in placed if p.metadata.get("render_emitted")),
            "unplaced_elements": [u["element_id"] for u in unplaced],
            "placed_elements": [p.element_id for p in placed],
        },
    }


def render_markdown(report: dict[str, Any], scene: SceneBuild) -> str:
    cfg = scene.config
    L = []
    L.append(f"# NIMA Phase II — First-Pass Build Validation Report")
    L.append("")
    L.append(f"- Pass: **{report['pass_label']}**")
    L.append(f"- Generated: {report['generated_at_utc']}")
    L.append(
        f"- Package: {report['package']['name']} {report['package']['version']} "
        f"({report['package']['date']})"
    )
    L.append("")

    L.append("## 1. Locked geometry — computed vs. baseline")
    hb = report["high_bay_geometry_check"]
    L.append("")
    L.append("| Metric | Baseline (package) | Computed | Match |")
    L.append("|---|---|---|---|")
    L.append(
        f"| High-bay perimeter (LF) | {hb['expected_perimeter_lf_proxy']} | "
        f"{hb['computed_perimeter_ft']} | "
        f"{'OK' if abs(hb['expected_perimeter_lf_proxy'] - hb['computed_perimeter_ft']) < 0.5 else 'CHECK'} |"
    )
    L.append(
        f"| High-bay footprint (SF) | {hb['expected_footprint_sf_proxy']} | "
        f"{hb['computed_footprint_sf']} | "
        f"{'OK' if abs(hb['expected_footprint_sf_proxy'] - hb['computed_footprint_sf']) < 5 else 'CHECK'} |"
    )
    L.append(
        f"| Roof / east top (ft) | {hb['expected_roof_top_ft']} | "
        f"{hb['computed_roof_top_ft']} | "
        f"{'OK' if hb['expected_roof_top_ft'] == hb['computed_roof_top_ft'] else 'CHECK'} |"
    )
    so = report["stair_opening_check"]
    L.append(
        f"| Stair opening area (SF) | ~{so['expected_area_sf']} | "
        f"{so['computed_area_sf']} | "
        f"{'OK' if abs((so['expected_area_sf'] or 0) - so['computed_area_sf']) < 5 else 'CHECK'} |"
    )
    L.append("")

    L.append("## 2. Locked assumptions applied")
    L.append("")
    for entry in report["locked_assumptions_applied"]:
        L.append(f"- {entry}")
    L.append("")

    if report["warnings"]:
        L.append("## 3. Warnings")
        L.append("")
        for w in report["warnings"]:
            L.append(f"- {w}")
        L.append("")

    if report["errors"]:
        L.append("## 4. Errors")
        L.append("")
        for e in report["errors"]:
            L.append(f"- {e}")
        L.append("")
    else:
        L.append("## 4. Errors")
        L.append("")
        L.append("None.")
        L.append("")

    L.append("## 5. Proxy flags (acceptable for first pass, refine later)")
    L.append("")
    for p in report["proxy_flags"]:
        L.append(f"- {p}")
    L.append("")

    L.append("## 6. Inferred assumptions (NOT locked in package — please confirm)")
    L.append("")
    if report["inferred_assumptions"]:
        for a in report["inferred_assumptions"]:
            L.append(f"- **{a['key']}** = {a['value']}  \n  Reason: {a['reason']}")
    else:
        L.append("- None.")
    L.append("")

    L.append("## 7. Openings — placed and unplaced")
    L.append("")
    summary = report["openings_summary"]
    L.append(
        f"- Placed: {summary['placed_count']} "
        f"(of which {summary['rendered_count']} produced render meshes; "
        f"the rest are coordination references)"
    )
    L.append(f"- Unplaced (pending non-high-bay envelope): {summary['unplaced_count']}")
    L.append("")
    L.append("### 7a. Placed (high-bay-anchored)")
    L.append("")
    L.append("| Element | Parent wall | Type | W x H | Sill / Head | Status |")
    L.append("|---|---|---|---|---|---|")
    for p in scene.openings.placed:
        L.append(
            f"| {p.element_id} | {p.parent_wall_id} | {p.element_type} | "
            f"{p.width_ft} x {p.height_ft} | {p.sill_ft} / {p.head_ft} | "
            f"{p.metadata.get('status','')} |"
        )
    L.append("")
    L.append("### 7b. Unplaced (need new-building envelope coordinates)")
    L.append("")
    L.append("| Element | Face | Zone | W x H | Reason |")
    L.append("|---|---|---|---|---|")
    for u in scene.openings.unplaced:
        L.append(
            f"| {u['element_id']} | {u['face']} | {u['zone']} | "
            f"{u['unit_width_ft']} x {u['unit_height_ft']} | {u['reason_unplaced']} |"
        )
    L.append("")

    L.append("## 8. Missing / ambiguous inputs (blocking full build)")
    L.append("")
    L.append(
        "The package locks the high-bay shell, the F2 stair-opening polygon, "
        "all material rules, all door rules, and 12x14x3 covered-loading doors. "
        "The following are not locked and are needed to complete the model "
        "beyond the minimal first pass:"
    )
    L.append("")
    L.append(
        "1. **New non-high-bay building envelope coordinates.** The wall "
        "schedule names parent segments (storefront, south window band, F2 "
        "north design-center glazing, F2 high-bay open-below boundary) but "
        "gives no endpoint coordinates. SVGs/PDF would need to be vector-"
        "extracted to draw the rest of the connected building."
    )
    L.append(
        "2. **F2 floor elevation.** Inferred at 14.0 ft from facade window sill "
        "data; not explicitly locked. Please confirm or provide a value."
    )
    L.append(
        "3. **HB-W-005 interior partition endpoints** (DEPLOYABLE_PROXY). "
        "Listed as 'see wall schedule' for start/end vertices. Need a 2D "
        "centerline to extrude."
    )
    L.append(
        "4. **Per-element placement on individual walls** (STD-018 says use "
        "centerpoints / visual evidence). For the first pass, elements are "
        "centered on their parent wall and overhead doors are evenly spaced. "
        "Visual cross-check against SVGs may shift these."
    )
    L.append(
        "5. **Roof shape** beyond a flat cap. Package locks roof top elevation "
        "but not pitch / parapet / transition to lower mass."
    )
    L.append(
        "6. **Existing Tyler context mass extents.** STD-004 says sealed/no-"
        "entry; the first pass does not yet emit a context boundary mesh."
    )
    L.append("")

    L.append("## 9. Recommended next development step")
    L.append("")
    L.append(
        "Vector-extract the new non-high-bay outline from the F1 + F2 SVG "
        "schematics and the elevation SVG, store as a new `building_envelope.json` "
        "input alongside the master config, and re-run the build. After that, "
        "all currently unplaced facade elements can attach to real parent walls."
    )
    L.append("")

    return "\n".join(L)


def write_reports(scene: SceneBuild, output_dir: Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = build_report_dict(scene)

    json_path = output_dir / "validation_report.json"
    json_path.write_text(json.dumps(report, indent=2))

    md_path = output_dir / "validation_report.md"
    md_path.write_text(render_markdown(report, scene))

    return json_path, md_path
