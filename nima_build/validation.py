"""
Phase 1 — Validation checks for the loaded config.

Verifies that every LOCKED standard, geometry lock, and override the build
pipeline depends on is present and well-formed. Validation is non-fatal: it
returns a structured result that becomes part of the final report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import NIMAConfig

REQUIRED_STANDARDS = [
    "STD-001",  # Purpose / LOD
    "STD-002",  # Units (feet)
    "STD-003",  # One connected building
    "STD-004",  # Existing Tyler sealed
    "STD-005",  # Interior wall 0.4167 ft
    "STD-006",  # Exterior wall 1.0 ft
    "STD-007",  # Default floor material
    "STD-008",  # High-bay cement slab
    "STD-009",  # Wall finish off-white
    "STD-010",  # No wood in high-bay
    "STD-011",  # Overlook refined
    "STD-012",  # Restroom wood doors
    "STD-013",  # Default doors
    "STD-014",  # Covered-loading 12x14 x3
    "STD-015",  # No auto stairs
    "STD-016",  # Roof top 38.957 ft
    "STD-017",  # Sub-500 SF ceilings
    "STD-018",  # Door/window placement rule
]

REQUIRED_GEO_LOCKS = [
    "GEO-001",  # High-bay footprint
    "GEO-002",  # High-bay vertices
    "GEO-003",  # High-bay roof top
    "GEO-004",  # F2 stair opening
]

REQUIRED_DOOR_RULES = [
    "DR-DEFAULT-GLASS",
    "DR-DOUBLE-GLASS",
    "DR-RESTROOM-WOOD",
    "DR-HIGHBAY-OVERHEAD",
    "DR-EXISTING-BLOCKED",
]

REQUIRED_MATERIALS = [
    "MAT-NEW-GENERAL",
    "MAT-HIGHBAY",
    "MAT-OVERLOOK",
    "MAT-RESTROOM-DOOR",
    "MAT-STOREFRONT",
]

EXPECTED_INTERIOR_WALL_FT = 0.4167
EXPECTED_EXTERIOR_WALL_FT = 1.0
EXPECTED_ROOF_TOP_FT = 38.9569377990431
EXPECTED_HIGHBAY_VERTEX_COUNT = 4
EXPECTED_STAIR_VERTEX_COUNT = 4
EXPECTED_OVERHEAD_QTY = 3
EXPECTED_OVERHEAD_W = 12.0
EXPECTED_OVERHEAD_H = 14.0


@dataclass
class ValidationResult:
    locked_applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    proxy_flags: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok(),
            "locked_applied": list(self.locked_applied),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "proxy_flags": list(self.proxy_flags),
        }


def validate_config(cfg: NIMAConfig) -> ValidationResult:
    res = ValidationResult()

    # 1. Standards
    for sid in REQUIRED_STANDARDS:
        if sid not in cfg.standards:
            res.errors.append(f"Missing required standard {sid}")
        else:
            row = cfg.standards[sid]
            if row.get("status") != "LOCKED":
                res.warnings.append(f"{sid} is not LOCKED (status={row.get('status')})")
            else:
                res.locked_applied.append(f"{sid}: {row.get('category')} = {row.get('value')}")

    # 2. Wall thicknesses
    if "STD-005" in cfg.standards and str(EXPECTED_INTERIOR_WALL_FT) not in cfg.standards["STD-005"]["value"]:
        res.warnings.append("STD-005 interior wall thickness text changed; expected 0.4167 ft")
    if "STD-006" in cfg.standards and str(EXPECTED_EXTERIOR_WALL_FT) not in cfg.standards["STD-006"]["value"]:
        res.warnings.append("STD-006 exterior wall thickness text changed; expected 1.0000 ft")

    # 3. Geometry locks
    for gid in REQUIRED_GEO_LOCKS:
        if gid not in cfg.geometry_locks:
            res.errors.append(f"Missing required geometry lock {gid}")
        else:
            res.locked_applied.append(
                f"{gid}: {cfg.geometry_locks[gid].get('item')} ({cfg.geometry_locks[gid].get('status')})"
            )

    # 4. High-bay vertices
    if len(cfg.high_bay_vertices) != EXPECTED_HIGHBAY_VERTEX_COUNT:
        res.errors.append(
            f"Expected {EXPECTED_HIGHBAY_VERTEX_COUNT} high-bay vertices, got {len(cfg.high_bay_vertices)}"
        )
    expected_vertex_coords = {
        "HB-V1": (91.0, 126.0),
        "HB-V2": (151.0, 116.0),
        "HB-V3": (120.0, -56.0),
        "HB-V4": (60.0, -46.0),
    }
    for v in cfg.high_bay_vertices:
        exp = expected_vertex_coords.get(v.vertex_id)
        if exp is None:
            res.warnings.append(f"Unexpected high-bay vertex id {v.vertex_id}")
            continue
        if (v.x_ft, v.y_ft) != exp:
            res.errors.append(
                f"{v.vertex_id} coordinates {(v.x_ft, v.y_ft)} != locked baseline {exp}"
            )
    res.locked_applied.append(
        "HighBay vertices HB-V1..V4 match locked baseline (clockwise order)"
    )

    # 5. High-bay walls
    if len(cfg.high_bay_walls) < 4:
        res.errors.append("High-bay schedule must include at least 4 exterior walls")
    exterior_walls = [w for w in cfg.high_bay_walls if w.wall_type.lower().startswith("exterior")]
    for w in exterior_walls:
        if abs(w.thickness_ft - EXPECTED_EXTERIOR_WALL_FT) > 1e-6:
            res.errors.append(
                f"{w.wall_id} thickness {w.thickness_ft} ft != exterior {EXPECTED_EXTERIOR_WALL_FT} ft"
            )
    interior_walls = [w for w in cfg.high_bay_walls if "Interior" in w.wall_type]
    for w in interior_walls:
        if abs(w.thickness_ft - EXPECTED_INTERIOR_WALL_FT) > 1e-3:
            res.errors.append(
                f"{w.wall_id} interior thickness {w.thickness_ft} ft != {EXPECTED_INTERIOR_WALL_FT} ft"
            )
        if w.status != "LOCKED":
            res.proxy_flags.append(
                f"{w.wall_id} {w.wall_type} is {w.status} — start/end vertices defer to wall schedule"
            )

    # 6. Roof top
    actual_roof = float(cfg.high_bay_meta["roof_top_ft"])
    if abs(actual_roof - EXPECTED_ROOF_TOP_FT) > 1e-9:
        res.errors.append(
            f"high_bay.roof_top_ft = {actual_roof}; expected {EXPECTED_ROOF_TOP_FT}"
        )
    else:
        res.locked_applied.append(f"Roof/east top = {actual_roof} ft")

    # 7. Stair opening
    if len(cfg.stair_opening_vertices) != EXPECTED_STAIR_VERTEX_COUNT:
        res.errors.append(
            f"Stair opening must have {EXPECTED_STAIR_VERTEX_COUNT} vertices, "
            f"got {len(cfg.stair_opening_vertices)}"
        )
    else:
        res.locked_applied.append(
            "F2 stair/open-to-lobby opening: 4-vertex polygon, slab cut only, no stair mesh"
        )

    # 8. Door rules
    for did in REQUIRED_DOOR_RULES:
        try:
            d = cfg.door_rule(did)
        except KeyError:
            res.errors.append(f"Missing required door rule {did}")
            continue
        if d.status not in ("LOCKED", "REFERENCE_ONLY"):
            res.warnings.append(f"{did} status is {d.status}")
        else:
            res.locked_applied.append(f"{did}: {d.applies_to} ({d.material_door_type})")

    # 8a. Overhead door 12x14 x3 sanity
    overhead = cfg.door_rule("DR-HIGHBAY-OVERHEAD")
    if overhead.width_ft != EXPECTED_OVERHEAD_W or overhead.height_ft != EXPECTED_OVERHEAD_H:
        res.errors.append(
            f"DR-HIGHBAY-OVERHEAD dims {overhead.width_ft}x{overhead.height_ft} != 12x14"
        )
    overhead_facade = [w for w in cfg.facade_windows if w.element_type == "Overhead sectional door"]
    if len(overhead_facade) != EXPECTED_OVERHEAD_QTY:
        res.errors.append(
            f"Expected {EXPECTED_OVERHEAD_QTY} overhead doors in facade list, got {len(overhead_facade)}"
        )
    for od in overhead_facade:
        if (od.unit_width_ft, od.unit_height_ft) != (EXPECTED_OVERHEAD_W, EXPECTED_OVERHEAD_H):
            res.errors.append(
                f"{od.element_id} dims {od.unit_width_ft}x{od.unit_height_ft} != 12x14"
            )

    # 9. Materials
    for mid in REQUIRED_MATERIALS:
        try:
            cfg.material(mid)
            res.locked_applied.append(f"Material {mid} present")
        except KeyError:
            res.errors.append(f"Missing required material {mid}")

    # 10. Proxy flags from QA register
    for q in cfg.qa_register:
        if q.get("Status") in ("DEPLOYABLE_PROXY", "MOVE_FORWARD_BASELINE", "DEFERRED", "FINALIZED_PROXY"):
            res.proxy_flags.append(f"{q['QA_ID']}: {q['Item']} ({q['Status']})")

    return res
