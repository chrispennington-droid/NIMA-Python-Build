"""
Phase 4 — GLB / glTF export.

Combines all MeshParts into a single trimesh.Scene, applying a PBR material
per palette entry. The export is binary GLB (one self-contained file).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

from .geometry import MeshPart
from .materials import PALETTE, palette_id_for
from .scene import SceneBuild


def _pbr_material(palette_id: str) -> PBRMaterial:
    pm = PALETTE[palette_id]
    return PBRMaterial(
        name=pm.name,
        baseColorFactor=list(pm.rgba),
        metallicFactor=pm.metallic,
        roughnessFactor=pm.roughness,
        alphaMode="BLEND" if pm.rgba[3] < 1.0 else "OPAQUE",
    )


def _part_to_mesh(part: MeshPart, palette_id: str) -> trimesh.Trimesh:
    mesh = trimesh.Trimesh(
        vertices=np.asarray(part.vertices, dtype=np.float64),
        faces=np.asarray(part.faces, dtype=np.int64),
        process=False,
    )
    pbr = _pbr_material(palette_id)
    # Per-vertex UVs are not necessary for solid colors. trimesh requires UVs
    # to attach a PBRMaterial via TextureVisuals, so synthesize zero UVs.
    uvs = np.zeros((len(mesh.vertices), 2), dtype=np.float64)
    mesh.visual = trimesh.visual.TextureVisuals(uv=uvs, material=pbr)
    return mesh


def _iter_all_parts(scene: SceneBuild) -> Iterable[tuple[str, MeshPart, str]]:
    # (node_name, part, palette_id)
    for p in scene.highbay.parts:
        yield (p.name, p, palette_id_for(p.material_id, p.role))
    for p in scene.stair.parts:
        yield (p.name, p, palette_id_for(p.material_id, p.role))
    for placed in scene.openings.placed:
        for p in placed.parts:
            # opening parts already store the palette id directly in material_id
            palette_id = p.material_id if p.material_id in PALETTE else palette_id_for(
                p.material_id, p.role
            )
            yield (p.name, p, palette_id)


def export_glb(scene: SceneBuild, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tscene = trimesh.Scene()
    for node_name, part, palette_id in _iter_all_parts(scene):
        mesh = _part_to_mesh(part, palette_id)
        tscene.add_geometry(mesh, node_name=node_name, geom_name=node_name)

    glb_bytes = tscene.export(file_type="glb")
    Path(path).write_bytes(glb_bytes)
    return path
