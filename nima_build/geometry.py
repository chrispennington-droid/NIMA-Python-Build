"""
Phase 2 — Geometry generation.

Builds:
  * High-bay shell (exterior walls + slab + flat roof) from the locked
    rotated-parallelogram vertices and roof-top elevation.
  * F2 stair / open-to-lobby slab opening polygon (cutout only, no stair mesh).
  * Helper utilities for thickening 2D wall segments into 3D extrusions.

All output is in feet. The minimal first-pass intentionally treats the
high-bay shell as one connected ring extrusion to satisfy STD-003 (one
connected building) without fabricating coordinates we do not have.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import shapely
import trimesh
from shapely.geometry import Polygon

from .config import NIMAConfig

# F2 finished-floor elevation is not explicitly locked in the package.
# It is inferred from facade window sill data: F1 windows have head ~14 ft,
# F2 lower windows have sill = 14 ft, F2 project-room windows sill = 14 ft.
# The validation report flags this as an inferred, unlocked value.
INFERRED_F2_FLOOR_FT = 14.0
SLAB_THICKNESS_FT = 0.25
ROOF_THICKNESS_FT = 0.5


@dataclass
class MeshPart:
    name: str
    role: str
    material_id: str
    vertices: np.ndarray
    faces: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_trimesh(self) -> trimesh.Trimesh:
        return trimesh.Trimesh(
            vertices=self.vertices,
            faces=self.faces,
            process=False,
        )


@dataclass
class HighBayShell:
    outer_polygon_xy: list[tuple[float, float]]
    inner_polygon_xy: list[tuple[float, float]]
    perimeter_ft: float
    footprint_sf: float
    roof_top_ft: float
    parts: list[MeshPart] = field(default_factory=list)


@dataclass
class StairOpening:
    polygon_xy: list[tuple[float, float]]
    area_sf: float
    floor_elev_ft: float
    parts: list[MeshPart] = field(default_factory=list)


def _ccw_polygon(points: list[tuple[float, float]]) -> Polygon:
    """Return a CCW shapely polygon, flipping if the input is CW."""
    poly = Polygon(points)
    if not poly.exterior.is_ccw:
        poly = Polygon(list(poly.exterior.coords)[::-1])
    return shapely.make_valid(poly)


def _extrude_to_part(
    poly: Polygon,
    z_lo: float,
    z_hi: float,
    name: str,
    role: str,
    material_id: str,
    metadata: dict[str, Any] | None = None,
) -> MeshPart:
    """Extrude a 2D shapely polygon between two z elevations into a MeshPart."""
    if poly.is_empty:
        raise ValueError(f"{name}: polygon is empty")
    height = z_hi - z_lo
    if height <= 0:
        raise ValueError(f"{name}: extrude height must be positive (got {height})")
    mesh = trimesh.creation.extrude_polygon(poly, height)
    mesh.apply_translation((0.0, 0.0, z_lo))
    return MeshPart(
        name=name,
        role=role,
        material_id=material_id,
        vertices=np.asarray(mesh.vertices, dtype=np.float64),
        faces=np.asarray(mesh.faces, dtype=np.int64),
        metadata=metadata or {},
    )


def build_highbay_shell(cfg: NIMAConfig) -> HighBayShell:
    """
    Build the locked high-bay rotated-parallelogram shell.

    Geometry locks:
      GEO-001 footprint, GEO-002 vertices, GEO-003 roof top.
    Standards:
      STD-006 exterior wall = 1.0 ft, STD-008 cement slab,
      STD-009 warm off-white walls, STD-010 no wood trim.
    """
    verts = [(v.x_ft, v.y_ft) for v in cfg.high_bay_vertices]
    outer = _ccw_polygon(verts)

    # Find the locked exterior thickness from the high-bay wall schedule.
    exterior_walls = [
        w for w in cfg.high_bay_walls if w.wall_type.lower().startswith("exterior")
    ]
    if not exterior_walls:
        raise ValueError("No exterior high-bay walls in schedule")
    thickness = exterior_walls[0].thickness_ft

    inner = outer.buffer(-thickness, join_style=2)  # mitered inward
    if inner.is_empty:
        raise ValueError("High-bay inner polygon collapsed; check thickness vs. footprint")
    wall_ring = outer.difference(inner)

    roof_top = float(cfg.high_bay_meta["roof_top_ft"])

    parts: list[MeshPart] = []

    # Cement slab: from -SLAB_THICKNESS_FT to 0
    parts.append(
        _extrude_to_part(
            outer,
            -SLAB_THICKNESS_FT,
            0.0,
            name="HB-SLAB",
            role="floor",
            material_id="MAT-HIGHBAY",
            metadata={"finish": "cement slab", "std_refs": ["STD-008"]},
        )
    )

    # Wall ring: extrude from 0 to roof_top
    parts.append(
        _extrude_to_part(
            wall_ring,
            0.0,
            roof_top,
            name="HB-WALLS",
            role="exterior_walls",
            material_id="MAT-HIGHBAY",
            metadata={
                "thickness_ft": thickness,
                "wall_ids": [w.wall_id for w in exterior_walls],
                "std_refs": ["STD-006", "STD-009", "STD-010"],
            },
        )
    )

    # Flat roof cap: thin slab at roof_top
    parts.append(
        _extrude_to_part(
            outer,
            roof_top,
            roof_top + ROOF_THICKNESS_FT,
            name="HB-ROOF",
            role="roof",
            material_id="MAT-HIGHBAY",
            metadata={
                "geo_refs": ["GEO-003"],
                "note": "Flat-cap proxy; pitch/parapet detail not in package",
            },
        )
    )

    return HighBayShell(
        outer_polygon_xy=list(outer.exterior.coords),
        inner_polygon_xy=list(inner.exterior.coords),
        perimeter_ft=outer.length,
        footprint_sf=outer.area,
        roof_top_ft=roof_top,
        parts=parts,
    )


def build_stair_opening(cfg: NIMAConfig, f2_floor_ft: float = INFERRED_F2_FLOOR_FT) -> StairOpening:
    """
    Build the F2 stair / open-to-lobby slab opening as a 2D polygon and a
    visual marker plate. STD-015: do not generate stair geometry.
    """
    verts = [(v.x_ft, v.y_ft) for v in cfg.stair_opening_vertices]
    poly = _ccw_polygon(verts)

    # Visual marker plate: very thin slice just below the (proxy) F2 floor.
    # This is a placeholder showing the cutout location; in the full build
    # it would be subtracted from the F2 slab once the F2 envelope is drawn.
    marker_thickness = 0.05
    parts = [
        _extrude_to_part(
            poly,
            f2_floor_ft - marker_thickness,
            f2_floor_ft,
            name="OV-F2-STAIR-OPENING",
            role="opening_marker",
            material_id="MAT-OVERLOOK",
            metadata={
                "geo_refs": ["GEO-004"],
                "note": "Cutout polygon visualization; STD-015 forbids stair geometry",
                "f2_floor_ft_inferred": f2_floor_ft,
            },
        )
    ]

    return StairOpening(
        polygon_xy=list(poly.exterior.coords),
        area_sf=poly.area,
        floor_elev_ft=f2_floor_ft,
        parts=parts,
    )


def thicken_wall_segment(
    p1: tuple[float, float],
    p2: tuple[float, float],
    thickness_ft: float,
    z_lo: float,
    z_hi: float,
    name: str,
    role: str,
    material_id: str,
    metadata: dict[str, Any] | None = None,
) -> MeshPart:
    """Thicken a 2D segment into a 3D wall extrusion."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        raise ValueError(f"{name}: zero-length segment")
    nx = -dy / length
    ny = dx / length
    half = thickness_ft / 2.0
    poly_pts = [
        (p1[0] + nx * half, p1[1] + ny * half),
        (p2[0] + nx * half, p2[1] + ny * half),
        (p2[0] - nx * half, p2[1] - ny * half),
        (p1[0] - nx * half, p1[1] - ny * half),
    ]
    poly = _ccw_polygon(poly_pts)
    return _extrude_to_part(poly, z_lo, z_hi, name, role, material_id, metadata)
