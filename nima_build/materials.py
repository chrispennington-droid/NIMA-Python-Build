"""
Phase 3 — Materials.

Maps the LOCKED material rules from the package onto a PBR palette suitable
for both the JSON scene description and the GLB export. The package material
rules conflate floor/wall/trim under one Material_ID; the palette below
expands those into render-ready entries while keeping the source rule id as
the controlling reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PaletteMaterial:
    name: str
    rgba: tuple[float, float, float, float]
    metallic: float = 0.0
    roughness: float = 0.85
    source_material_id: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rgba": list(self.rgba),
            "metallic": self.metallic,
            "roughness": self.roughness,
            "source_material_id": self.source_material_id,
            "notes": self.notes,
        }


# Color choices: warm neutrals, light wood, cement gray, soft glass tint.
PALETTE: dict[str, PaletteMaterial] = {
    "MAT-HIGHBAY-SLAB": PaletteMaterial(
        name="HighBay Cement Slab",
        rgba=(0.62, 0.61, 0.58, 1.0),
        roughness=0.95,
        source_material_id="MAT-HIGHBAY",
        notes="STD-008 cement slab",
    ),
    "MAT-HIGHBAY-WALL": PaletteMaterial(
        name="HighBay Warm Off-White Industrial",
        rgba=(0.92, 0.89, 0.83, 1.0),
        roughness=0.85,
        source_material_id="MAT-HIGHBAY",
        notes="STD-009 warm off-white; STD-010 no wood trim",
    ),
    "MAT-HIGHBAY-ROOF": PaletteMaterial(
        name="HighBay Roof Cap",
        rgba=(0.58, 0.58, 0.58, 1.0),
        roughness=0.9,
        source_material_id="MAT-HIGHBAY",
        notes="Flat-cap proxy, finish not specified in package",
    ),
    "MAT-NEW-FLOOR": PaletteMaterial(
        name="New Refined Floor",
        rgba=(0.78, 0.74, 0.68, 1.0),
        roughness=0.6,
        source_material_id="MAT-NEW-GENERAL",
        notes="STD-007 uniform refined floor (non-high-bay)",
    ),
    "MAT-NEW-WALL": PaletteMaterial(
        name="New Warm Off-White Wall",
        rgba=(0.95, 0.93, 0.88, 1.0),
        roughness=0.8,
        source_material_id="MAT-NEW-GENERAL",
        notes="Warm off-white painted walls",
    ),
    "MAT-OVERLOOK-WALL": PaletteMaterial(
        name="Overlook Refined Wall",
        rgba=(0.95, 0.93, 0.88, 1.0),
        roughness=0.7,
        source_material_id="MAT-OVERLOOK",
        notes="STD-011 refined feel allowed",
    ),
    "MAT-OVERLOOK-TRIM": PaletteMaterial(
        name="Overlook Light Wood Trim",
        rgba=(0.83, 0.70, 0.50, 1.0),
        roughness=0.55,
        source_material_id="MAT-OVERLOOK",
        notes="Refined warm light wood trim",
    ),
    "MAT-RESTROOM-DOOR-WOOD": PaletteMaterial(
        name="Restroom Solid Warm Light Wood Door",
        rgba=(0.78, 0.62, 0.42, 1.0),
        roughness=0.5,
        source_material_id="MAT-RESTROOM-DOOR",
        notes="STD-012 overrides default glass for RR doors",
    ),
    "MAT-STOREFRONT-GLASS": PaletteMaterial(
        name="Storefront Glass",
        rgba=(0.62, 0.78, 0.85, 0.45),
        metallic=0.0,
        roughness=0.1,
        source_material_id="MAT-STOREFRONT",
        notes="Lobby/connector glazing",
    ),
    "MAT-STOREFRONT-FRAME": PaletteMaterial(
        name="Storefront Aluminum Frame",
        rgba=(0.55, 0.56, 0.58, 1.0),
        metallic=0.85,
        roughness=0.3,
        source_material_id="MAT-STOREFRONT",
        notes="Aluminum / light wood trim companion",
    ),
    "MAT-DOOR-GLASS": PaletteMaterial(
        name="Glass / Aluminum Door",
        rgba=(0.7, 0.82, 0.9, 0.5),
        roughness=0.15,
        source_material_id="MAT-STOREFRONT",
        notes="DR-DEFAULT-GLASS / DR-DOUBLE-GLASS",
    ),
    "MAT-OVERHEAD-DOOR": PaletteMaterial(
        name="Overhead Sectional Door",
        rgba=(0.4, 0.42, 0.45, 1.0),
        roughness=0.7,
        source_material_id="MAT-HIGHBAY",
        notes="DR-HIGHBAY-OVERHEAD 12x14 industrial",
    ),
    "MAT-FACADE-ACCENT": PaletteMaterial(
        name="Facade Dark Accent Strip",
        rgba=(0.18, 0.18, 0.20, 1.0),
        roughness=0.7,
        source_material_id="MAT-HIGHBAY",
        notes="NF-002 / EF-002 coordination reference; not glazing",
    ),
    "MAT-GUARD-GLASS": PaletteMaterial(
        name="Guard / Edge Glazing",
        rgba=(0.65, 0.78, 0.82, 0.4),
        roughness=0.15,
        source_material_id="MAT-OVERLOOK",
        notes="IG-006 open-to-below guard / glass edge",
    ),
    "MAT-EXISTING-TYLER-SEAL": PaletteMaterial(
        name="Existing Tyler Sealed Boundary",
        rgba=(0.78, 0.78, 0.76, 1.0),
        roughness=0.9,
        source_material_id="MAT-NEW-GENERAL",
        notes="STD-004 sealed/no-entry context",
    ),
}


# Render-target -> palette key, for the parts produced in geometry.py.
ROLE_TO_PALETTE: dict[tuple[str, str], str] = {
    ("MAT-HIGHBAY", "floor"): "MAT-HIGHBAY-SLAB",
    ("MAT-HIGHBAY", "exterior_walls"): "MAT-HIGHBAY-WALL",
    ("MAT-HIGHBAY", "roof"): "MAT-HIGHBAY-ROOF",
    ("MAT-OVERLOOK", "opening_marker"): "MAT-OVERLOOK-WALL",
}


def palette_id_for(part_material_id: str, part_role: str, fallback: str | None = None) -> str:
    key = (part_material_id, part_role)
    if key in ROLE_TO_PALETTE:
        return ROLE_TO_PALETTE[key]
    if fallback is not None:
        return fallback
    # Best-effort fallback: pass-through ids that already exist in palette
    if part_material_id in PALETTE:
        return part_material_id
    return "MAT-NEW-WALL"


def palette_to_dict() -> dict[str, dict[str, Any]]:
    return {pid: m.to_dict() for pid, m in PALETTE.items()}
