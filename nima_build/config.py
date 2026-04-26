"""
Phase 1 — Config loader.

Reads the consolidated master config (`nima_master_build_config.json`) and the
wall_schedule CSV (only domain not already mirrored inside the master JSON),
exposes typed accessors.

Source-of-truth ranking (from the package intake report):
  1. nima_master_build_config.json
  2. wall_schedule.csv
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class HighBayVertex:
    vertex_id: str
    label: str
    x_ft: float
    y_ft: float
    grid_x: float
    grid_y: float
    notes: str = ""


@dataclass
class HighBayWall:
    wall_id: str
    start_vertex: str
    end_vertex: str
    wall_type: str
    thickness_ft: float
    approx_length_ft: float
    related_doors_openings: str
    material_finish: str
    status: str
    notes: str = ""


@dataclass
class StairOpeningVertex:
    vertex_id: str
    description: str
    x_ft: float
    y_ft: float


@dataclass
class DoorRule:
    rule_id: str
    applies_to: str
    width_ft: float | None
    height_ft: float | str | None
    material_door_type: str
    status: str
    notes: str


@dataclass
class FacadeWindow:
    element_id: str
    face: str
    zone: str
    element_type: str
    qty: int
    unit_width_ft: float
    unit_height_ft: float
    sill_ft: float
    head_ft: float
    build_as: str
    status: str
    notes: str


@dataclass
class MaterialRule:
    material_id: str
    applies_to: str
    floor_finish: str
    wall_finish: str
    trim_accent: str
    status: str
    notes: str


@dataclass
class WallScheduleRow:
    segment_id: str
    floor: str
    wall_type: str
    thickness_ft: float
    related_rooms_or_zones: str
    door_refs: str
    window_facade_refs: str
    material_finish: str
    build_status: str
    notes: str


@dataclass
class NIMAConfig:
    raw: dict[str, Any]
    standards: dict[str, dict[str, Any]]
    geometry_locks: dict[str, dict[str, Any]]
    high_bay_vertices: list[HighBayVertex]
    high_bay_walls: list[HighBayWall]
    high_bay_meta: dict[str, Any]
    stair_opening_meta: dict[str, Any]
    stair_opening_vertices: list[StairOpeningVertex]
    door_rules: list[DoorRule]
    facade_windows: list[FacadeWindow]
    materials: list[MaterialRule]
    qa_register: list[dict[str, Any]]
    wall_schedule: list[WallScheduleRow] = field(default_factory=list)

    def standard(self, std_id: str) -> dict[str, Any]:
        return self.standards[std_id]

    def geometry_lock(self, geo_id: str) -> dict[str, Any]:
        return self.geometry_locks[geo_id]

    def material(self, material_id: str) -> MaterialRule:
        for m in self.materials:
            if m.material_id == material_id:
                return m
        raise KeyError(material_id)

    def door_rule(self, rule_id: str) -> DoorRule:
        for d in self.door_rules:
            if d.rule_id == rule_id:
                return d
        raise KeyError(rule_id)


def _to_float_or_none(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _height_field(v: Any) -> float | str | None:
    """Door heights may be 'Per schedule' string or a number."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return str(v)


def load_config(package_root: Path) -> NIMAConfig:
    """Load the consolidated master config + wall schedule."""
    package_root = Path(package_root)

    master_path = package_root / "nima_master_build_config.json"
    if not master_path.exists():
        raise FileNotFoundError(f"Master config not found: {master_path}")
    with master_path.open() as f:
        raw = json.load(f)

    high_bay_vertices = [
        HighBayVertex(
            vertex_id=v["Vertex_ID"],
            label=v["Label"],
            x_ft=float(v["Feet_X"]),
            y_ft=float(v["Feet_Y"]),
            grid_x=float(v["Grid_X"]),
            grid_y=float(v["Grid_Y"]),
            notes=v.get("Notes", ""),
        )
        for v in raw["high_bay"]["vertices"]
    ]

    high_bay_walls = [
        HighBayWall(
            wall_id=w["Wall_ID"],
            start_vertex=w["Start_Vertex"],
            end_vertex=w["End_Vertex"],
            wall_type=w["Wall_Type"],
            thickness_ft=float(w["Thickness_ft"]),
            approx_length_ft=float(w["Approx_Length_ft"]),
            related_doors_openings=w.get("Related_Doors_Openings", ""),
            material_finish=w.get("Material / Finish", ""),
            status=w["Status"],
            notes=w.get("Notes", ""),
        )
        for w in raw["high_bay"]["walls"]
    ]

    stair_block = raw["stair_opening"]
    stair_opening_vertices = [
        StairOpeningVertex(
            vertex_id=v["Vertex_ID"],
            description=v["Description"],
            x_ft=float(v["Approx_X_FT"]),
            y_ft=float(v["Approx_Y_FT"]),
        )
        for v in stair_block["vertices"]
    ]
    stair_opening_meta = stair_block["opening"][0] if stair_block.get("opening") else {}

    door_rules = [
        DoorRule(
            rule_id=d["Door_Rule_ID"],
            applies_to=d["Applies_To"],
            width_ft=_to_float_or_none(d.get("Width_ft")),
            height_ft=_height_field(d.get("Height_ft")),
            material_door_type=d.get("Material / Door Type", ""),
            status=d["Status"],
            notes=d.get("Notes", ""),
        )
        for d in raw["door_rules"]
    ]

    facade_windows = [
        FacadeWindow(
            element_id=w["Element_ID"],
            face=w["Face"],
            zone=w["Zone"],
            element_type=w["Element_Type"],
            qty=int(w["Qty"]),
            unit_width_ft=float(w["Unit_Width_ft"]),
            unit_height_ft=float(w["Unit_Height_ft"]),
            sill_ft=float(w["Sill_ft"]),
            head_ft=float(w["Head_ft"]),
            build_as=w.get("Build_As", ""),
            status=w["Status"],
            notes=w.get("Notes", ""),
        )
        for w in raw["facade_windows"]
    ]

    materials = [
        MaterialRule(
            material_id=m["Material_ID"],
            applies_to=m["Applies_To"],
            floor_finish=m["Floor_Finish"],
            wall_finish=m["Wall_Finish"],
            trim_accent=m["Trim / Accent"],
            status=m["Status"],
            notes=m.get("Notes", ""),
        )
        for m in raw["materials"]
    ]

    wall_schedule = _load_wall_schedule(package_root / "wall_schedule.csv")

    return NIMAConfig(
        raw=raw,
        standards=raw["standards"],
        geometry_locks=raw["geometry_locks"],
        high_bay_vertices=high_bay_vertices,
        high_bay_walls=high_bay_walls,
        high_bay_meta={
            "footprint_sf_proxy": raw["high_bay"]["footprint_sf_proxy"],
            "perimeter_lf_proxy": raw["high_bay"]["perimeter_lf_proxy"],
            "roof_top_ft": raw["high_bay"]["roof_top_ft"],
            "program_area_sf_reference": raw["high_bay"]["program_area_sf_reference"],
        },
        stair_opening_meta=stair_opening_meta,
        stair_opening_vertices=stair_opening_vertices,
        door_rules=door_rules,
        facade_windows=facade_windows,
        materials=materials,
        qa_register=raw["qa_register"],
        wall_schedule=wall_schedule,
    )


def _load_wall_schedule(csv_path: Path) -> list[WallScheduleRow]:
    if not csv_path.exists():
        return []
    rows: list[WallScheduleRow] = []
    with csv_path.open(newline="") as f:
        for r in csv.DictReader(f):
            try:
                thickness = float(r["Thickness_ft"])
            except (TypeError, ValueError):
                thickness = 0.0
            rows.append(
                WallScheduleRow(
                    segment_id=r["Segment_ID"],
                    floor=r["Floor"],
                    wall_type=r["Wall_Type"],
                    thickness_ft=thickness,
                    related_rooms_or_zones=r["Related_Rooms_or_Zones"],
                    door_refs=r["Door_Refs"],
                    window_facade_refs=r["Window_Facade_Refs"],
                    material_finish=r["Material / Finish"],
                    build_status=r["Build_Status"],
                    notes=r.get("Notes", ""),
                )
            )
    return rows
