#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_STAGE = ROOT / "code_inputs" / "scene_partial_expanded_scope_review.json"
BUILDING_ENVELOPE = ROOT / "code_inputs" / "building_envelope.json"
MATERIAL_RULES = ROOT / "code_inputs" / "material_finish_rules.json"
MASTER_CONFIG = ROOT / "code_inputs" / "nima_master_build_config.json"
OUTPUT_DIR = ROOT / "build_outputs" / "partial_mvp_spatial_review"


REQUIRED_HEADER_LINES = [
    "PARTIAL MVP SPATIAL-REVIEW BUILD",
    "NOT FINAL",
    "NOT FULL-SCENE MERGE",
    "UNRESOLVED GEOMETRY EXCLUDED",
    "GENERATED FROM scene_partial_expanded_scope_review.json ONLY",
    "REMAINING UNRESOLVED ITEMS REQUIRE MANUAL VECTOR CONFIRMATION OR LATER EXPLICIT PROXY APPROVAL",
]


class DupDict(dict):
    def __init__(self, pairs: list[tuple[str, Any]]) -> None:
        super().__init__()
        self._dups: list[str] = []
        for key, value in pairs:
            if key in self:
                self._dups.append(key)
            self[key] = value


def dup_hook(pairs: list[tuple[str, Any]]) -> DupDict:
    return DupDict(pairs)


def load_json_with_dups(path: Path) -> tuple[Any, int]:
    with path.open() as f:
        obj = json.load(f, object_pairs_hook=dup_hook)
    return to_plain(obj), count_dups(obj)


def count_dups(node: Any) -> int:
    if isinstance(node, DupDict):
        return len(node._dups) + sum(count_dups(v) for v in node.values())
    if isinstance(node, list):
        return sum(count_dups(v) for v in node)
    return 0


def to_plain(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: to_plain(v) for k, v in node.items()}
    if isinstance(node, list):
        return [to_plain(v) for v in node]
    return node


@dataclass
class IncludedItem:
    floor: str
    category: str
    item_id: str
    payload: dict[str, Any]


def gather_included_items(stage: dict[str, Any]) -> list[IncludedItem]:
    results: list[IncludedItem] = []
    for floor, floor_payload in stage["included_geometry"].items():
        for category, items in floor_payload.items():
            for item in items:
                item_id = (
                    item.get("segment_id")
                    or item.get("boundary_id")
                    or item.get("condition_id")
                    or item.get("opening_id")
                )
                results.append(
                    IncludedItem(
                        floor=floor,
                        category=category,
                        item_id=item_id,
                        payload=item,
                    )
                )
    return results


def validate(stage: dict[str, Any], building: dict[str, Any], materials: list[dict[str, Any]]) -> dict[str, Any]:
    items = gather_included_items(stage)
    included_ids = [item.item_id for item in items]
    stage_ids = stage["included_geometry_ids"]
    unresolved_ids = stage["validation_carry_forward"]["unresolved_item_ids"]
    material_ids = {row["Material_ID"] for row in materials}
    allowed_statuses = {"EXTRACTED", "EXTRACTED_PROXY"}
    allowed_included = set(stage_ids)

    extra_ids = sorted(set(included_ids) - allowed_included)
    missing_ids = sorted(allowed_included - set(included_ids))
    excluded_present = sorted(set(included_ids) & set(unresolved_ids))
    unresolved_promoted = bool(stage["validation_carry_forward"]["unresolved_items_promoted"])

    thickness_checks: list[dict[str, Any]] = []
    thickness_ok = True
    for item in items:
        payload = item.payload
        status = payload.get("geometry", {}).get("status") or payload.get("extraction_status")
        if status not in allowed_statuses:
            thickness_ok = False
        if item.category == "exterior_wall_segments":
            ok = math.isclose(payload["thickness_ft"], 1.0, abs_tol=1e-6)
            thickness_ok = thickness_ok and ok
            thickness_checks.append({"item_id": item.item_id, "expected_ft": 1.0, "actual_ft": payload["thickness_ft"], "ok": ok})
        elif item.category == "interior_parent_wall_segments":
            ok = math.isclose(payload["thickness_ft"], 0.4167, abs_tol=1e-4)
            thickness_ok = thickness_ok and ok
            thickness_checks.append({"item_id": item.item_id, "expected_ft": 0.4167, "actual_ft": payload["thickness_ft"], "ok": ok})

    material_ok = True
    material_audit: list[dict[str, Any]] = []
    for item in items:
        payload = item.payload
        mat = payload.get("material_zone_ref")
        if mat is not None:
            ok = mat in material_ids
            material_ok = material_ok and ok
            material_audit.append({"item_id": item.item_id, "material_zone_ref": mat, "ok": ok})

    high_bay_ref = stage["read_only_context_refs"]["high_bay"]
    stair_ref = stage["read_only_context_refs"]["stair_opening"]
    tyler_refs = stage["read_only_context_refs"]["sealed_existing_tyler_refs"]
    locked_context_ok = (
        high_bay_ref["status"] == "LOCKED_READ_ONLY_REFERENCE"
        and stair_ref["status"] == "LOCKED_READ_ONLY_REFERENCE"
        and all(ref["status"] == "REFERENCE_ONLY" for ref in tyler_refs)
    )

    no_stair_geometry = all(item.item_id != "OV-F2-STAIR-OPENING" for item in items)
    existing_tyler_sealed = all("EXISTING-SEAL" not in item.item_id for item in items)

    guard_edge = next(item for item in items if item.item_id == "W-F2-HIGHBAY-OPEN-BELOW-BOUNDARY")
    guard_ok = (
        guard_edge.payload.get("classification") == "guard_edge_parent"
        and guard_edge.payload.get("segment_role") == "guard_edge_not_full_wall"
        and guard_edge.payload.get("provenance") == "DERIVED_FROM_STAIR_POLYGON_EDGE"
        and guard_edge.payload.get("review_flags") == ["CONFIRM_AGAINST_F2_SVG_BEFORE_LOCKING"]
    )

    building_gate = building["post_extraction_validation_gate"]
    checks = building_gate["checks"]
    passing = sum(1 for check in checks if check["status"] == "PASS")
    all_pass = passing == len(checks)

    return {
        "included_ids": stage_ids,
        "included_ids_missing": missing_ids,
        "included_ids_extra": extra_ids,
        "excluded_unresolved_ids": unresolved_ids,
        "excluded_unresolved_present_in_geometry": excluded_present,
        "no_unresolved_promoted": not unresolved_promoted,
        "locked_read_only_context_preserved": locked_context_ok,
        "high_bay_preserved": high_bay_ref,
        "stair_opening_preserved": stair_ref,
        "sealed_existing_tyler_refs": tyler_refs,
        "no_stair_geometry_generated": no_stair_geometry,
        "existing_tyler_sealed_no_entry": existing_tyler_sealed,
        "guard_edge_metadata_preserved": guard_ok,
        "wall_thickness_rules_preserved": thickness_ok,
        "wall_thickness_audit": thickness_checks,
        "material_rules_preserved": material_ok,
        "material_audit": material_audit,
        "full_scene_merge_ready": stage["validation_carry_forward"]["full_scene_merge_ready"],
        "glb_regeneration_blocked": stage["validation_carry_forward"]["glb_regeneration_blocked"],
        "merge_ready_for_current_extracted_scope": stage["validation_carry_forward"]["merge_ready_for_current_extracted_scope"],
        "overall_readiness_note": stage["validation_carry_forward"]["overall_readiness_note"],
        "building_validation_gate": {
            "total_checks": len(checks),
            "passing_checks": passing,
            "all_checks_pass": all_pass,
        },
    }


def flatten_scene(stage: dict[str, Any], level_z: dict[str, Any]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for item in gather_included_items(stage):
        payload = item.payload
        flattened.append(
            {
                "item_id": item.item_id,
                "floor": item.floor,
                "category": item.category,
                "base_level_elevation_ft": level_z[item.floor]["floor_elevation_ft"],
                "classification": payload.get("classification", payload.get("boundary_type")),
                "material_zone_ref": payload.get("material_zone_ref", "MAT-NEW-GENERAL"),
                "thickness_ft": payload.get("thickness_ft"),
                "geometry": payload["geometry"],
                "door_refs": payload.get("door_refs", []),
                "associated_openings": payload.get("associated_openings", []),
                "source_trace": payload.get("source_trace", []),
            }
        )
    return flattened


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def bounds_for_floor(floor_payload: dict[str, Any]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for bucket_items in floor_payload.values():
        for item in bucket_items:
            for x, y in item["geometry"]["vertices"]:
                xs.append(x)
                ys.append(y)
            for opening in item.get("associated_openings", []):
                x, y = opening["center_pt_ft"]
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def transform(x: float, y: float, bounds: tuple[float, float, float, float], panel: tuple[float, float, float, float]) -> tuple[float, float, float]:
    min_x, min_y, max_x, max_y = bounds
    left, top, width, height = panel
    margin = 30.0
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin
    world_w = max_x - min_x
    world_h = max_y - min_y
    scale = min(usable_w / world_w, usable_h / world_h)
    tx = left + margin + (x - min_x) * scale
    ty = top + height - margin - (y - min_y) * scale
    return tx, ty, scale


def color_for_material(material_zone_ref: str) -> tuple[str, str]:
    mapping = {
        "MAT-NEW-GENERAL": ("#F5E8C7", "#4F4A45"),
        "MAT-STOREFRONT": ("#DDEAF6", "#305E8A"),
        "MAT-HIGHBAY": ("#DDDDDD", "#555555"),
        "MAT-OVERLOOK": ("#F6E3B4", "#8A6222"),
    }
    return mapping.get(material_zone_ref, ("#EFEFEF", "#555555"))


def midpoint(vertices: list[list[float]]) -> tuple[float, float]:
    if len(vertices) == 1:
        return vertices[0][0], vertices[0][1]
    if len(vertices) == 2:
        return ((vertices[0][0] + vertices[1][0]) / 2.0, (vertices[0][1] + vertices[1][1]) / 2.0)
    return (
        sum(v[0] for v in vertices) / len(vertices),
        sum(v[1] for v in vertices) / len(vertices),
    )


def polygon_points(vertices: list[list[float]], bounds: tuple[float, float, float, float], panel: tuple[float, float, float, float]) -> tuple[str, float]:
    pts: list[str] = []
    last_scale = 1.0
    for x, y in vertices:
        tx, ty, scale = transform(x, y, bounds, panel)
        last_scale = scale
        pts.append(f"{tx:.2f},{ty:.2f}")
    return " ".join(pts), last_scale


def polyline_points(vertices: list[list[float]], bounds: tuple[float, float, float, float], panel: tuple[float, float, float, float]) -> tuple[str, float]:
    return polygon_points(vertices, bounds, panel)


def build_svg(stage: dict[str, Any], output_path: Path) -> None:
    width = 1800
    height = 1600
    header_h = 260
    panel_gap = 40
    panel_h = (height - header_h - panel_gap - 80) / 2
    panel_w = width - 80
    f1_panel = (40.0, header_h, panel_w, panel_h)
    f2_panel = (40.0, header_h + panel_h + panel_gap, panel_w, panel_h)
    panels = {"F1": f1_panel, "F2": f2_panel}

    floor_bounds = {
        floor: bounds_for_floor(stage["included_geometry"][floor])
        for floor in ("F1", "F2")
    }

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FAFAF8"/>',
    ]

    y = 44
    for idx, text in enumerate(REQUIRED_HEADER_LINES):
        size = 26 if idx == 0 else 18
        weight = "700" if idx == 0 else "600"
        lines.append(
            f'<text x="40" y="{y}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="#8A1F11">{svg_escape(text)}</text>'
        )
        y += 34

    lines.append('<text x="40" y="226" font-family="Arial, sans-serif" font-size="15" fill="#333">Read-only context carried in manifest only: locked high-bay geometry, finalized stair-opening polygon, sealed Existing Tyler refs.</text>')
    lines.append('<text x="40" y="248" font-family="Arial, sans-serif" font-size="15" fill="#333">Unresolved items are excluded from geometry payload and listed in the manifest/README for manual follow-up.</text>')

    for floor in ("F1", "F2"):
        panel = panels[floor]
        left, top, p_w, p_h = panel
        bounds = floor_bounds[floor]
        lines.append(f'<rect x="{left}" y="{top}" width="{p_w}" height="{p_h}" rx="12" fill="#FFFFFF" stroke="#C8C5BF" stroke-width="2"/>')
        lines.append(f'<text x="{left + 16}" y="{top + 28}" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#333">{floor} Accepted Geometry Only</text>')
        lines.append(f'<text x="{left + 16}" y="{top + 50}" font-family="Arial, sans-serif" font-size="13" fill="#666">Plan preview derived from accepted staged geometry only</text>')

        floor_payload = stage["included_geometry"][floor]
        for boundary in floor_payload["floor_plate_boundaries"]:
            pts, _ = polygon_points(boundary["geometry"]["vertices"], bounds, panel)
            fill, stroke = color_for_material("MAT-NEW-GENERAL")
            lines.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.45" stroke="{stroke}" stroke-width="2"/>')
            mx, my = midpoint(boundary["geometry"]["vertices"])
            tx, ty, _ = transform(mx, my, bounds, panel)
            lines.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#555">{svg_escape(boundary["boundary_id"])}</text>')

        for category in ("exterior_wall_segments", "interior_parent_wall_segments"):
            for item in floor_payload.get(category, []):
                pts, scale = polyline_points(item["geometry"]["vertices"], bounds, panel)
                fill, stroke = color_for_material(item.get("material_zone_ref", "MAT-NEW-GENERAL"))
                thickness = item.get("thickness_ft", 0.25)
                stroke_px = max(2.0, thickness * scale)
                dash = ' stroke-dasharray="12 8"' if item.get("classification") == "guard_edge_parent" else ""
                lines.append(
                    f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{stroke_px:.2f}" stroke-linecap="round"{dash}/>'
                )
                mx, my = midpoint(item["geometry"]["vertices"])
                tx, ty, _ = transform(mx, my, bounds, panel)
                lines.append(f'<text x="{tx:.2f}" y="{ty - 8:.2f}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#222">{svg_escape(item["segment_id"])}</text>')
                for opening in item.get("associated_openings", []):
                    ox, oy = opening["center_pt_ft"]
                    tox, toy, _ = transform(ox, oy, bounds, panel)
                    lines.append(f'<circle cx="{tox:.2f}" cy="{toy:.2f}" r="5" fill="#FFFFFF" stroke="#A83232" stroke-width="2"/>')
                    lines.append(f'<text x="{tox + 8:.2f}" y="{toy - 8:.2f}" font-family="Arial, sans-serif" font-size="11" fill="#A83232">{svg_escape(opening["opening_id"])}</text>')

    lines.append("</svg>")
    output_path.write_text("\n".join(lines))


def build_readme(stage: dict[str, Any], validation: dict[str, Any], output_files: list[str]) -> str:
    unresolved = stage["validation_carry_forward"]["unresolved_item_ids"]
    included = stage["included_geometry_ids"]
    return "\n".join(
        [
            "# PARTIAL MVP SPATIAL-REVIEW BUILD",
            "",
            "- NOT FINAL",
            "- NOT FULL-SCENE MERGE",
            "- UNRESOLVED GEOMETRY EXCLUDED",
            "- GENERATED FROM `scene_partial_expanded_scope_review.json` ONLY",
            "- REMAINING UNRESOLVED ITEMS REQUIRE MANUAL VECTOR CONFIRMATION OR LATER EXPLICIT PROXY APPROVAL",
            "",
            "## Source",
            "",
            f"- `{SOURCE_STAGE.relative_to(ROOT)}`",
            "",
            "## Output Files",
            "",
            *[f"- `{name}`" for name in output_files],
            "",
            "## Included Geometry IDs",
            "",
            *[f"- `{item_id}`" for item_id in included],
            "",
            "## Excluded Unresolved IDs",
            "",
            *[f"- `{item_id}`" for item_id in unresolved],
            "",
            "## Locked / Read-Only Context Preserved",
            "",
            "- locked high-bay geometry",
            "- finalized stair-opening polygon",
            "- sealed Existing Tyler references",
            "- `W-F2-HIGHBAY-OPEN-BELOW-BOUNDARY` metadata/provenance preserved",
            "",
            "## Validation",
            "",
            f"- `building_envelope.json` valid JSON: `{validation['building_envelope_valid_json']}`",
            f"- `scene_partial_expanded_scope_review.json` valid JSON: `{validation['source_stage_valid_json']}`",
            f"- duplicate-key audit `building_envelope.json`: `{validation['building_envelope_duplicate_keys']}`",
            f"- duplicate-key audit `scene_partial_expanded_scope_review.json`: `{validation['source_stage_duplicate_keys']}`",
            f"- inclusion audit missing IDs: `{validation['included_ids_missing']}`",
            f"- inclusion audit extra IDs: `{validation['included_ids_extra']}`",
            f"- exclusion audit unresolved present in geometry: `{validation['excluded_unresolved_present_in_geometry']}`",
            f"- no unresolved promoted: `{validation['no_unresolved_promoted']}`",
            f"- wall thickness rules preserved: `{validation['wall_thickness_rules_preserved']}`",
            f"- material rules preserved: `{validation['material_rules_preserved']}`",
            f"- no stair geometry generated: `{validation['no_stair_geometry_generated']}`",
            f"- Existing Tyler sealed/no-entry preserved: `{validation['existing_tyler_sealed_no_entry']}`",
            f"- building validation gate: `{validation['building_validation_gate']['passing_checks']}/{validation['building_validation_gate']['total_checks']} PASS`",
            f"- full scene merge ready: `{validation['full_scene_merge_ready']}`",
            f"- GLB regeneration blocked: `{validation['glb_regeneration_blocked']}`",
            "",
            "## Known Limitations",
            "",
            "- This package excludes all unresolved `NEEDS_VECTOR_CONFIRMATION` geometry.",
            "- This package is suitable for limited spatial review only; it is not a BIM/CD-complete model.",
            "- Read-only context is referenced in metadata/manifest and is not promoted into new geometry.",
            "- The preview scene is derived only from accepted staged geometry and does not resolve missing conditions, stair geometry, or Existing Tyler access.",
        ]
    )


def main() -> None:
    stage, stage_dups = load_json_with_dups(SOURCE_STAGE)
    building, building_dups = load_json_with_dups(BUILDING_ENVELOPE)
    materials, _ = load_json_with_dups(MATERIAL_RULES)
    master_config, _ = load_json_with_dups(MASTER_CONFIG)

    validation = validate(stage, building, materials)
    validation.update(
        {
            "building_envelope_valid_json": True,
            "source_stage_valid_json": True,
            "building_envelope_duplicate_keys": building_dups,
            "source_stage_duplicate_keys": stage_dups,
        }
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scene_json_path = OUTPUT_DIR / "partial_mvp_spatial_review_scene.json"
    svg_path = OUTPUT_DIR / "partial_mvp_spatial_review_plan.svg"
    manifest_path = OUTPUT_DIR / "PARTIAL_MVP_SPATIAL_REVIEW_BUILD_MANIFEST.json"
    readme_path = OUTPUT_DIR / "README_PARTIAL_MVP_SPATIAL_REVIEW.md"

    scene_payload = {
        "document_type": "partial_mvp_spatial_review_scene",
        "labels": REQUIRED_HEADER_LINES,
        "source_artifact": str(SOURCE_STAGE.relative_to(ROOT)),
        "full_scene_merge_ready": False,
        "glb_regeneration_blocked": True,
        "read_only_context_refs": stage["read_only_context_refs"],
        "included_geometry_ids": stage["included_geometry_ids"],
        "excluded_unresolved_ids": stage["validation_carry_forward"]["unresolved_item_ids"],
        "source_normalization_flags": stage["validation_carry_forward"]["source_normalization_flags"],
        "level_z": building["level_z"],
        "materials_reference": {row["Material_ID"]: row for row in materials},
        "flattened_geometry": flatten_scene(stage, building["level_z"]),
    }
    scene_json_path.write_text(json.dumps(scene_payload, indent=2))

    build_svg(stage, svg_path)

    output_files = [
        str(scene_json_path.relative_to(ROOT)),
        str(svg_path.relative_to(ROOT)),
        str(manifest_path.relative_to(ROOT)),
        str(readme_path.relative_to(ROOT)),
    ]

    manifest_payload = {
        "document_type": "partial_mvp_spatial_review_manifest",
        "labels": REQUIRED_HEADER_LINES,
        "source_artifact": str(SOURCE_STAGE.relative_to(ROOT)),
        "output_files": output_files,
        "included_geometry_ids": stage["included_geometry_ids"],
        "excluded_unresolved_ids": stage["validation_carry_forward"]["unresolved_item_ids"],
        "read_only_context_refs": stage["read_only_context_refs"],
        "validation": validation,
        "topology_assertions": stage["topology_assertions"],
        "validation_gate_snapshot": stage["validation_gate_snapshot"],
        "master_config_reference": {
            "package": master_config["package"],
            "standards": {
                "interior_wall_thickness_ft": 0.4167,
                "exterior_wall_thickness_ft": 1.0,
                "high_bay_floor_material": "Cement slab",
                "new_non_high_bay_floor_material": "Uniform refined floor material",
                "high_bay_trim": "No wood trim",
                "connector_lobby_overlook_finish": "Refined lobby/connector feel allowed",
            },
        },
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2))

    readme_path.write_text(build_readme(stage, validation, output_files))

    print(
        json.dumps(
            {
                "output_files": output_files,
                "validation": validation,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
