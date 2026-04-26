"""
Phase 3 — Doors, windows, and facade proxies.

For the minimal first pass, openings are placed as thin proxy plates on the
outer face of their parent wall. This is consistent with STD-001 (lightweight
1:1 spatial-review model, not BIM precision) and avoids forcing exact mullion
spacing or true subtractive openings before the rest of the building envelope
is drawn.

Placement strategy (per STD-018):
  * Where the package gives explicit qty + position rule (e.g. 3 covered-loading
    overhead doors), distribute evenly along the parent wall.
  * Where only a parent wall is known, center the element on that wall.
  * Where no parent wall can be unambiguously identified from the package
    alone, leave the element UNPLACED and surface it in the validation report.

Only high-bay-anchored elements are placed in the first pass, because the
non-high-bay envelope coordinates are not provided in the package.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .config import FacadeWindow, NIMAConfig
from .geometry import MeshPart


# Mapping from package face/zone keywords to a high-bay wall id. Anything not
# in this table is left unplaced.
HIGHBAY_PLACEMENT: dict[str, str] = {
    # Element_ID -> Wall_ID
    "NF-001": "HB-W-001",  # high-bay upper wall, north
    "NF-002": "HB-W-001",  # vertical accent (NOT a glazing element)
    "EF-001": "HB-W-002",  # east face vertical
    "EF-002": "HB-W-002",  # east face ornamental treatment
    "SF-008": "HB-W-003",  # overhead door 1
    "SF-009": "HB-W-003",  # overhead door 2
    "SF-010": "HB-W-003",  # overhead door 3
    "SF-011": "HB-W-003",  # high-bay east panel — ambiguous; treated as south HB upper
}

# Render palette key per element type.
ELEMENT_TYPE_PALETTE: dict[str, str] = {
    "Large translucent/panelled opening": "MAT-STOREFRONT-GLASS",
    "Vertical dark accent strip": "MAT-FACADE-ACCENT",
    "Vertical window / screened opening": "MAT-STOREFRONT-GLASS",
    "Ornamental facade treatment": "MAT-FACADE-ACCENT",
    "Overhead sectional door": "MAT-OVERHEAD-DOOR",
    "High-bay patterned/translucent window": "MAT-STOREFRONT-GLASS",
    "Curtain wall / entry glazing": "MAT-STOREFRONT-GLASS",
    "Large framed window band": "MAT-STOREFRONT-GLASS",
    "Low glazing / guardrail band": "MAT-GUARD-GLASS",
    "Horizontal ribbon window": "MAT-STOREFRONT-GLASS",
    "Tall glazed slot": "MAT-STOREFRONT-GLASS",
    "Grouped upper vertical windows": "MAT-STOREFRONT-GLASS",
    "Grouped lower vertical windows": "MAT-STOREFRONT-GLASS",
    "Two-story vertical glazing": "MAT-STOREFRONT-GLASS",
    "Horizontal window band": "MAT-STOREFRONT-GLASS",
    "Window wall": "MAT-STOREFRONT-GLASS",
    "Guard/glazed edge": "MAT-GUARD-GLASS",
}


@dataclass
class PlacedOpening:
    element_id: str
    parent_wall_id: str
    face: str
    zone: str
    element_type: str
    qty: int
    width_ft: float
    height_ft: float
    sill_ft: float
    head_ft: float
    center_xy: tuple[float, float]
    palette_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    parts: list[MeshPart] = field(default_factory=list)


@dataclass
class OpeningsBuild:
    placed: list[PlacedOpening] = field(default_factory=list)
    unplaced: list[dict[str, Any]] = field(default_factory=list)


def _wall_segment(cfg: NIMAConfig, wall_id: str) -> tuple[tuple[float, float], tuple[float, float], float]:
    """Resolve the (start_xy, end_xy, thickness_ft) for a high-bay wall id."""
    wall = next((w for w in cfg.high_bay_walls if w.wall_id == wall_id), None)
    if wall is None:
        raise KeyError(f"Unknown high-bay wall id: {wall_id}")
    vmap = {v.vertex_id: (v.x_ft, v.y_ft) for v in cfg.high_bay_vertices}
    if wall.start_vertex not in vmap or wall.end_vertex not in vmap:
        raise ValueError(
            f"Wall {wall_id} references non-vertex endpoints: "
            f"{wall.start_vertex} -> {wall.end_vertex}"
        )
    return vmap[wall.start_vertex], vmap[wall.end_vertex], wall.thickness_ft


def _outward_normal(p1, p2, polygon_centroid):
    """Return a unit normal to (p1->p2) that points away from the centroid."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    n1 = (-dy / length, dx / length)
    n2 = (dy / length, -dx / length)
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    cx, cy = polygon_centroid
    d1 = math.hypot(mid[0] + n1[0] - cx, mid[1] + n1[1] - cy)
    d2 = math.hypot(mid[0] + n2[0] - cx, mid[1] + n2[1] - cy)
    return n1 if d1 > d2 else n2


def _highbay_centroid(cfg: NIMAConfig) -> tuple[float, float]:
    xs = [v.x_ft for v in cfg.high_bay_vertices]
    ys = [v.y_ft for v in cfg.high_bay_vertices]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _build_panel_mesh(
    p1: tuple[float, float],
    p2: tuple[float, float],
    outward_normal: tuple[float, float],
    distance_along: float,
    width_ft: float,
    sill_ft: float,
    head_ft: float,
    standoff_ft: float = 0.55,  # just outside 1.0 ft thick wall + small gap
    name: str = "OPENING",
    role: str = "opening",
    palette_id: str = "MAT-STOREFRONT-GLASS",
    metadata: dict[str, Any] | None = None,
) -> MeshPart:
    """
    Build a thin (0.05 ft) rectangular panel mesh on the outside face of a wall.

    distance_along: position of the panel center measured from p1 along p1->p2.
    """
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length  # along-wall unit
    nx, ny = outward_normal  # outward unit

    cx = p1[0] + ux * distance_along + nx * standoff_ft
    cy = p1[1] + uy * distance_along + ny * standoff_ft

    half_w = width_ft / 2.0
    panel_thickness = 0.05

    # 8 vertices for an axis-aligned-on-wall thin panel.
    base_corners_xy = [
        (cx - ux * half_w, cy - uy * half_w),  # left
        (cx + ux * half_w, cy + uy * half_w),  # right
    ]
    front_offset = (nx * panel_thickness, ny * panel_thickness)

    verts = []
    # Bottom-left, bottom-right, top-right, top-left at back face (against wall)
    bl = (base_corners_xy[0][0], base_corners_xy[0][1], sill_ft)
    br = (base_corners_xy[1][0], base_corners_xy[1][1], sill_ft)
    tr = (base_corners_xy[1][0], base_corners_xy[1][1], head_ft)
    tl = (base_corners_xy[0][0], base_corners_xy[0][1], head_ft)
    # Front face = back face + outward offset
    bl_f = (bl[0] + front_offset[0], bl[1] + front_offset[1], bl[2])
    br_f = (br[0] + front_offset[0], br[1] + front_offset[1], br[2])
    tr_f = (tr[0] + front_offset[0], tr[1] + front_offset[1], tr[2])
    tl_f = (tl[0] + front_offset[0], tl[1] + front_offset[1], tl[2])

    verts = np.array([bl, br, tr, tl, bl_f, br_f, tr_f, tl_f], dtype=np.float64)
    # Faces of a box (12 triangles).
    faces = np.array([
        [0, 1, 2], [0, 2, 3],   # back
        [4, 6, 5], [4, 7, 6],   # front
        [0, 4, 5], [0, 5, 1],   # bottom
        [3, 2, 6], [3, 6, 7],   # top
        [0, 3, 7], [0, 7, 4],   # left
        [1, 5, 6], [1, 6, 2],   # right
    ], dtype=np.int64)

    return MeshPart(
        name=name,
        role=role,
        material_id=palette_id,
        vertices=verts,
        faces=faces,
        metadata=metadata or {},
    )


def build_openings(cfg: NIMAConfig) -> OpeningsBuild:
    """
    Place high-bay-anchored facade elements; surface unplaced ones.
    """
    out = OpeningsBuild()
    centroid = _highbay_centroid(cfg)

    # Group elements by parent wall id for even distribution.
    by_wall: dict[str, list[FacadeWindow]] = {}
    for w in cfg.facade_windows:
        wall_id = HIGHBAY_PLACEMENT.get(w.element_id)
        if wall_id is None:
            out.unplaced.append(_unplaced_record(w, "no high-bay parent wall identified"))
            continue
        by_wall.setdefault(wall_id, []).append(w)

    for wall_id, elements in by_wall.items():
        try:
            p1, p2, _thickness = _wall_segment(cfg, wall_id)
        except (KeyError, ValueError) as exc:
            for w in elements:
                out.unplaced.append(_unplaced_record(w, f"wall lookup failed: {exc}"))
            continue
        normal = _outward_normal(p1, p2, centroid)
        wall_length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])

        # Sort elements with deterministic order (overhead doors share Element_Type
        # so use Element_ID alphabetical).
        elements_sorted = sorted(elements, key=lambda e: e.element_id)

        # Special handling: HB-W-003 with three overhead doors -> evenly-spaced.
        overhead_doors = [e for e in elements_sorted if e.element_type == "Overhead sectional door"]
        other_elements = [e for e in elements_sorted if e.element_type != "Overhead sectional door"]

        if overhead_doors and wall_id == "HB-W-003":
            # Distribute 3 doors evenly: 4 equal gaps.
            n = len(overhead_doors)
            for i, w in enumerate(overhead_doors):
                d_along = wall_length * (i + 1) / (n + 1)
                _place(out, w, wall_id, p1, p2, normal, d_along)

        for w in other_elements:
            d_along = wall_length / 2.0  # center on wall (STD-018 fallback)
            _place(out, w, wall_id, p1, p2, normal, d_along)

    return out


def _place(
    out: OpeningsBuild,
    w: FacadeWindow,
    wall_id: str,
    p1: tuple[float, float],
    p2: tuple[float, float],
    normal: tuple[float, float],
    distance_along: float,
) -> None:
    palette_id = ELEMENT_TYPE_PALETTE.get(w.element_type, "MAT-STOREFRONT-GLASS")
    role = "door" if "door" in w.element_type.lower() else (
        "facade_accent" if w.status == "COORDINATION_REFERENCE" else "window"
    )

    # Skip mesh emission if element is COORDINATION_REFERENCE (per package note),
    # but still record placement metadata so the JSON scene has it.
    parts: list[MeshPart] = []
    if w.status != "COORDINATION_REFERENCE":
        mesh = _build_panel_mesh(
            p1=p1,
            p2=p2,
            outward_normal=normal,
            distance_along=distance_along,
            width_ft=w.unit_width_ft,
            sill_ft=w.sill_ft,
            head_ft=w.head_ft,
            name=w.element_id,
            role=role,
            palette_id=palette_id,
            metadata={
                "face": w.face,
                "zone": w.zone,
                "build_as": w.build_as,
                "status": w.status,
                "qty": w.qty,
                "parent_wall": wall_id,
                "notes": w.notes,
            },
        )
        parts.append(mesh)

    cx = p1[0] + (p2[0] - p1[0]) / math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * distance_along
    cy = p1[1] + (p2[1] - p1[1]) / math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * distance_along

    out.placed.append(
        PlacedOpening(
            element_id=w.element_id,
            parent_wall_id=wall_id,
            face=w.face,
            zone=w.zone,
            element_type=w.element_type,
            qty=w.qty,
            width_ft=w.unit_width_ft,
            height_ft=w.unit_height_ft,
            sill_ft=w.sill_ft,
            head_ft=w.head_ft,
            center_xy=(cx, cy),
            palette_id=palette_id,
            metadata={
                "status": w.status,
                "build_as": w.build_as,
                "notes": w.notes,
                "render_emitted": bool(parts),
            },
            parts=parts,
        )
    )


def _unplaced_record(w: FacadeWindow, reason: str) -> dict[str, Any]:
    return {
        "element_id": w.element_id,
        "face": w.face,
        "zone": w.zone,
        "element_type": w.element_type,
        "qty": w.qty,
        "unit_width_ft": w.unit_width_ft,
        "unit_height_ft": w.unit_height_ft,
        "sill_ft": w.sill_ft,
        "head_ft": w.head_ft,
        "status": w.status,
        "build_as": w.build_as,
        "notes": w.notes,
        "reason_unplaced": reason,
    }
