"""
Phase 4 — Scene assembly and structured JSON export.

The JSON scene is the internal source-of-truth output. The GLB is derived
from it via gltf.py.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .config import NIMAConfig
from .geometry import HighBayShell, MeshPart, StairOpening
from .materials import PALETTE, palette_id_for, palette_to_dict
from .openings import OpeningsBuild
from .validation import ValidationResult


@dataclass
class SceneBuild:
    config: NIMAConfig
    highbay: HighBayShell
    stair: StairOpening
    openings: OpeningsBuild
    validation: ValidationResult
    inferred_assumptions: list[dict[str, Any]] = field(default_factory=list)
    f2_floor_ft: float = 14.0
    pass_label: str = "minimal_first_pass"


def _serialize_part(part: MeshPart, palette_id: str) -> dict[str, Any]:
    return {
        "name": part.name,
        "role": part.role,
        "source_material_id": part.material_id,
        "palette_id": palette_id,
        "vertex_count": int(len(part.vertices)),
        "face_count": int(len(part.faces)),
        "metadata": part.metadata,
    }


def build_scene_json(scene: SceneBuild) -> dict[str, Any]:
    cfg = scene.config

    # Building parts
    highbay_parts = [
        _serialize_part(p, palette_id_for(p.material_id, p.role))
        for p in scene.highbay.parts
    ]
    stair_parts = [
        _serialize_part(p, palette_id_for(p.material_id, p.role))
        for p in scene.stair.parts
    ]

    # Openings: emitted parts only, plus placement metadata for all placed (including non-rendered).
    placed_records = []
    for placed in scene.openings.placed:
        rec = {
            "element_id": placed.element_id,
            "parent_wall_id": placed.parent_wall_id,
            "face": placed.face,
            "zone": placed.zone,
            "element_type": placed.element_type,
            "qty": placed.qty,
            "width_ft": placed.width_ft,
            "height_ft": placed.height_ft,
            "sill_ft": placed.sill_ft,
            "head_ft": placed.head_ft,
            "center_xy_ft": list(placed.center_xy),
            "palette_id": placed.palette_id,
            "render_emitted": placed.metadata.get("render_emitted", False),
            "metadata": placed.metadata,
            "parts": [
                _serialize_part(p, p.material_id)  # placed parts already store palette id
                for p in placed.parts
            ],
        }
        placed_records.append(rec)

    return {
        "schema_version": "nima-scene/1.0",
        "package": {
            "name": cfg.raw["package"]["name"],
            "version": cfg.raw["package"]["version"],
            "date": cfg.raw["package"]["date"],
            "scope_note": cfg.raw["package"]["scope_note"],
        },
        "build": {
            "pipeline_version": __version__,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "pass_label": scene.pass_label,
            "units": "feet",
            "grid_unit_ft": 8.0,
        },
        "source_of_truth": [
            "nima_master_build_config.json",
            "wall_schedule.csv",
        ],
        "applied_standards": [
            {"id": sid, "category": s["category"], "value": s["value"], "status": s["status"]}
            for sid, s in cfg.standards.items()
        ],
        "applied_geometry_locks": [
            {"id": gid, "item": g["item"], "status": g["status"], "values": g["values"]}
            for gid, g in cfg.geometry_locks.items()
        ],
        "inferred_assumptions": scene.inferred_assumptions,
        "materials_palette": palette_to_dict(),
        "source_material_rules": [asdict(m) if hasattr(m, "__dataclass_fields__") else m
                                  for m in cfg.materials],
        "door_rules": [asdict(d) for d in cfg.door_rules],
        "high_bay": {
            "outer_polygon_xy_ft": [list(p) for p in scene.highbay.outer_polygon_xy],
            "inner_polygon_xy_ft": [list(p) for p in scene.highbay.inner_polygon_xy],
            "perimeter_ft": scene.highbay.perimeter_ft,
            "footprint_sf": scene.highbay.footprint_sf,
            "roof_top_ft": scene.highbay.roof_top_ft,
            "wall_schedule": [
                {
                    "wall_id": w.wall_id,
                    "start_vertex": w.start_vertex,
                    "end_vertex": w.end_vertex,
                    "wall_type": w.wall_type,
                    "thickness_ft": w.thickness_ft,
                    "approx_length_ft": w.approx_length_ft,
                    "status": w.status,
                    "material_finish": w.material_finish,
                    "related_doors_openings": w.related_doors_openings,
                    "notes": w.notes,
                }
                for w in cfg.high_bay_walls
            ],
            "parts": highbay_parts,
        },
        "stair_opening": {
            "polygon_xy_ft": [list(p) for p in scene.stair.polygon_xy],
            "area_sf": scene.stair.area_sf,
            "f2_floor_ft": scene.stair.floor_elev_ft,
            "build_rule": "STD-015: cutout only; no stair geometry",
            "parts": stair_parts,
        },
        "openings_placed": placed_records,
        "openings_unplaced": scene.openings.unplaced,
        "wall_schedule_parents": [
            {
                "segment_id": w.segment_id,
                "floor": w.floor,
                "wall_type": w.wall_type,
                "thickness_ft": w.thickness_ft,
                "related_rooms_or_zones": w.related_rooms_or_zones,
                "door_refs": w.door_refs,
                "window_facade_refs": w.window_facade_refs,
                "material_finish": w.material_finish,
                "build_status": w.build_status,
                "notes": w.notes,
            }
            for w in cfg.wall_schedule
        ],
        "validation": scene.validation.to_dict(),
        "qa_register": cfg.qa_register,
    }


def write_scene_json(scene: SceneBuild, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = build_scene_json(scene)
    path.write_text(json.dumps(data, indent=2))
    return path
