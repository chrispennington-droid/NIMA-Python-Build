"""
NIMA Phase II Spatial Review Learning Lab: Prove-Out Facility Walkthrough
Class demo / presentation build (separate from formal RC1 QA pipeline).

Run with Blender:
    blender --background --python tools/build_class_demo_entry_proveout_overlook.py

Outputs (placed in build_outputs/class_demo_learning_lab/):
    NIMA_PhaseII_SpatialReview_LearningLab.blend
    NIMA_PhaseII_SpatialReview_LearningLab.fbx
    NIMA_PhaseII_SpatialReview_LearningLab.glb

Design units are FEET. Blender file uses meters (1 ft = 0.3048 m).
World convention: +X east, +Y north (depth into prove-out facility), +Z up.

This script DOES NOT modify any RC1 staging or formal source JSON.
"""

import math
import os
import sys

FT = 0.3048  # ft -> m

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "build_outputs", "class_demo_learning_lab",
)
BASE_NAME = "NIMA_PhaseII_SpatialReview_LearningLab"

# ---------------------------------------------------------------------------
# Layout (all values in feet)
# ---------------------------------------------------------------------------
LOBBY = dict(x0=-21.0, x1=21.0, y0=-32.0, y1=0.0,  z0=0.0, z1=24.0)      # 42 x 32 x 24
HIGHBAY = dict(x0=-30.4, x1=30.4, y0=0.0,  y1=176.0, z0=0.0, z1=38.96)   # 60.8 x 176 x 38.96
WALL_T = 0.5  # nominal wall thickness for visible mass

DOOR1 = dict(name="Door_Lobby_To_ProveOut_Level1",
             x0=-3.0, x1=3.0, y=0.0, z0=0.0, z1=8.0)        # 6 x 8
DOOR2 = dict(name="Door_Level2_To_ProveOut_Overlook",
             x0=15.0, x1=21.0, y=0.0, z0=14.0, z1=22.0)     # 6 x 8 at upper

OVERLOOK_Z = 14.0
LANDING = dict(x0=15.0, x1=21.0, y0=-8.0, y1=0.0)           # 6 wide x 8 deep
OVERLOOK = dict(x0=3.0, x1=27.0, y0=0.0, y1=10.0)           # 24 wide x 10 deep

STAIR = dict(x0=15.0, x1=21.0, y_start=-30.0, risers=24,
             riser=14.0/24.0, tread=1.0)  # 24 risers @ 0.583 ft, 1.0 ft tread

OVERHEAD_DOORS = [
    dict(name="OH_Door_W", x0=-25.4, x1=-13.4, y=176.0, z0=0.0, z1=14.0),
    dict(name="OH_Door_C", x0=-6.0,  x1=6.0,   y=176.0, z0=0.0, z1=14.0),
    dict(name="OH_Door_E", x0=13.4,  x1=25.4,  y=176.0, z0=0.0, z1=14.0),
]

EQUIPMENT = [
    dict(name="Large_Test_Rig",   x0=-22.0, x1=-4.0, y0=20.0, y1=30.0, z0=0.0, z1=9.0),
    dict(name="CNC_Machine_Cell", x0=-22.0, x1=-8.0, y0=44.0, y1=52.0, z0=0.0, z1=7.0),
    dict(name="Assembly_Table",   x0=-22.0, x1=-6.0, y0=66.0, y1=71.0, z0=0.0, z1=3.0),
    dict(name="Robot_Work_Cell",  x0=-22.0, x1=-10.0, y0=88.0, y1=100.0, z0=0.0, z1=8.0),
]
FORKLIFT_PATH = dict(name="Forklift_Clearance_Path",
                     x0=10.0, x1=18.0, y0=20.0, y1=160.0, z0=0.0, z1=0.05)  # 8 x 140

BOARDS = [
    ("Board_Title",      "NIMA Phase II Spatial Review Learning Lab",
        "A simplified class prototype for learning spatial review, equipment fit, "
        "workflow, and QA-gated model development.",
        -18.0, -31.5, 4.0, 0.0),
    ("Board_Entry",      "Learning Experience",
        "This prototype focuses on the entry sequence, controlled access, "
        "Prove-Out Facility, equipment fit, loading access, and overlook-based observation.",
        -18.0, -25.0, 4.0, 90.0),
    ("Board_NIMA",       "What Does NIMA Do?",
        "NIMA develops technologies, applications, partnerships, facilities, and a "
        "highly-qualified workforce for emerging materials. This learning lab focuses "
        "on how a Prove-Out Facility supports prototyping, testing, and applied research.",
        -18.0, -18.0, 4.0, 90.0),
    ("Board_RDPark",     "Emerging R+D Park Context",
        "The Prove-Out Facility is part of a larger innovation ecosystem with Tyler "
        "Research Center, NIMA, Emerging Technologies, and the KBI/PSU site.",
        -18.0, -11.0, 4.0, 90.0),
    ("Board_PhaseII",    "Phase II Expansion",
        "The expansion adds approximately 24,230 square feet and supports future "
        "research, testing, prototyping, and workforce development.",
        18.0, -18.0, 4.0, -90.0),
    ("Board_ProveOut",   "Purpose of the Prove-Out Facility",
        "The Prove-Out Facility is the large high-bay space where equipment layout, "
        "clearances, workflow, and loading access can be evaluated before final build-out.",
        -28.0, 8.0, 6.0, 90.0),
    ("Board_EquipFit",   "Equipment-Fit Review",
        "Learners inspect whether test rigs, machine cells, assembly tables, robot "
        "work cells, and forklift paths fit safely within the Prove-Out Facility.",
        -28.0, 36.0, 6.0, 90.0),
    ("Board_Overlook",   "Prove-Out Facility Overlook",
        "The overlook lets stakeholders observe the Prove-Out Facility from above and "
        "review workflow, safety, and equipment relationships without entering the "
        "active production floor.",
        15.0, 5.0, 18.0, 180.0),
    ("Board_QA",         "QA Boundary",
        "This prototype intentionally blocks unresolved areas instead of presenting "
        "unverified geometry as complete. The goal is to support spatial learning, "
        "not final construction documentation.",
        28.0, 90.0, 6.0, -90.0),
    ("Board_Reflection", "Main Takeaways",
        "Spatial VR helps learners understand scale, equipment fit, workflow, and "
        "design review. The process also showed why generated geometry needs QA before "
        "being used as an immersive walkthrough.",
        -28.0, 150.0, 6.0, 90.0),
]

# Blocked-boundary barriers around non-tour areas (ring around the building bbox)
BARRIERS = [
    # West perimeter outside of building
    dict(name="MVP_Barrier_W", x0=-50.0, x1=-49.0, y0=-40.0, y1=180.0, z0=0.0, z1=8.0),
    # East perimeter
    dict(name="MVP_Barrier_E", x0=49.0, x1=50.0, y0=-40.0, y1=180.0, z0=0.0, z1=8.0),
    # South perimeter (behind lobby entrance)
    dict(name="MVP_Barrier_S", x0=-50.0, x1=50.0, y0=-41.0, y1=-40.0, z0=0.0, z1=8.0),
    # North perimeter (beyond high-bay loading apron)
    dict(name="MVP_Barrier_N", x0=-50.0, x1=50.0, y0=190.0, y1=191.0, z0=0.0, z1=8.0),
    # Internal sealed boundary stub: "Existing Tyler sealed / no-entry"
    dict(name="MVP_Barrier_TylerSeal", x0=-30.4, x1=-29.9, y0=140.0, y1=176.0, z0=0.0, z1=10.0),
]

# ---------------------------------------------------------------------------
# Materials (PBR base color RGBA, 0..1)
# ---------------------------------------------------------------------------
MAT = {
    "cement_floor":   (0.62, 0.62, 0.60, 1.0),
    "industrial_wall":(0.93, 0.91, 0.86, 1.0),
    "lobby_floor":    (0.78, 0.70, 0.58, 1.0),
    "lobby_wall":     (0.96, 0.93, 0.88, 1.0),
    "glass":          (0.55, 0.72, 0.86, 0.45),
    "stair":          (0.55, 0.55, 0.58, 1.0),
    "guardrail":      (0.20, 0.22, 0.25, 1.0),
    "door_active":    (0.18, 0.62, 0.35, 1.0),  # green = walk through
    "door_overhead":  (0.40, 0.42, 0.48, 1.0),
    "equipment":      (0.55, 0.58, 0.65, 1.0),
    "forklift_path":  (0.95, 0.78, 0.10, 1.0),
    "board_face":     (0.97, 0.97, 0.95, 1.0),
    "board_frame":    (0.18, 0.20, 0.25, 1.0),
    "barrier":        (0.85, 0.18, 0.18, 0.85),
    "overlook_floor": (0.82, 0.74, 0.62, 1.0),
    "accent_warm":    (0.78, 0.55, 0.32, 1.0),
}

# ===========================================================================
# Blender helpers
# ===========================================================================
try:
    import bpy  # noqa: F401
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def _bpy_clear():
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def _bpy_mat(name, rgba):
    import bpy
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if rgba[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = rgba[3]
            m.blend_method = "BLEND"
    return m


def _bpy_box(name, x0, y0, z0, x1, y1, z1, mat_name):
    import bpy
    cx, cy, cz = (x0 + x1) / 2 * FT, (y0 + y1) / 2 * FT, (z0 + z1) / 2 * FT
    sx, sy, sz = (x1 - x0) * FT, (y1 - y0) * FT, (z1 - z0) * FT
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mat = _bpy_mat(mat_name, MAT[mat_name])
    obj.data.materials.append(mat)
    return obj


def _bpy_wall_with_opening(name, x0, x1, y, z_top, opening,
                            axis="x", thickness=WALL_T, mat="industrial_wall"):
    """Build wall along x or y axis with a rectangular opening cut by panels."""
    # opening = dict with x0,x1,z0,z1 (or y0,y1,z0,z1)
    pieces = []
    if axis == "x":
        oy0 = y - thickness / 2
        oy1 = y + thickness / 2
        ox0, ox1 = opening["x0"], opening["x1"]
        oz0, oz1 = opening["z0"], opening["z1"]
        # left of opening
        if ox0 > x0:
            pieces.append(_bpy_box(f"{name}_L", x0, oy0, 0, ox0, oy1, z_top, mat))
        # right of opening
        if ox1 < x1:
            pieces.append(_bpy_box(f"{name}_R", ox1, oy0, 0, x1, oy1, z_top, mat))
        # below opening
        if oz0 > 0:
            pieces.append(_bpy_box(f"{name}_B", ox0, oy0, 0, ox1, oy1, oz0, mat))
        # above opening
        if oz1 < z_top:
            pieces.append(_bpy_box(f"{name}_A", ox0, oy0, oz1, ox1, oy1, z_top, mat))
    else:
        ox0 = y - thickness / 2  # y becomes x position
        ox1 = y + thickness / 2
        oy0, oy1 = opening["y0"], opening["y1"]
        oz0, oz1 = opening["z0"], opening["z1"]
        if oy0 > x0:
            pieces.append(_bpy_box(f"{name}_L", ox0, x0, 0, ox1, oy0, z_top, mat))
        if oy1 < x1:
            pieces.append(_bpy_box(f"{name}_R", ox0, oy1, 0, ox1, x1, z_top, mat))
        if oz0 > 0:
            pieces.append(_bpy_box(f"{name}_B", ox0, oy0, 0, ox1, oy1, oz0, mat))
        if oz1 < z_top:
            pieces.append(_bpy_box(f"{name}_A", ox0, oy0, oz1, ox1, oy1, z_top, mat))
    return pieces


def _bpy_stair(name, x0, x1, y_start, risers, riser, tread, mat="stair"):
    import bpy
    objs = []
    for n in range(risers):
        y0 = y_start + n * tread
        y1 = y0 + tread
        z0 = 0.0
        z1 = (n + 1) * riser
        objs.append(_bpy_box(f"{name}_step_{n:02d}", x0, y0, z0, x1, y1, z1, mat))
    return objs


def _bpy_text(name, text, x_ft, y_ft, z_ft, rot_deg_z=0.0, size_ft=0.6):
    import bpy
    bpy.ops.object.text_add(location=(x_ft * FT, y_ft * FT, z_ft * FT))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.body = text
    obj.data.size = size_ft * FT
    obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(rot_deg_z))
    return obj


def build_with_blender():
    import bpy
    _bpy_clear()
    bpy.context.scene.unit_settings.system = "IMPERIAL"
    bpy.context.scene.unit_settings.length_unit = "FEET"

    # ---- Lobby shell ----
    _bpy_box("Lobby_Floor", LOBBY["x0"], LOBBY["y0"], -0.05,
             LOBBY["x1"], LOBBY["y1"], 0.0, "lobby_floor")
    _bpy_box("Lobby_Ceiling", LOBBY["x0"], LOBBY["y0"], LOBBY["z1"],
             LOBBY["x1"], LOBBY["y1"], LOBBY["z1"] + 0.4, "lobby_wall")
    # Walls (S, E, W). N wall is the shared wall with prove-out and is built below.
    _bpy_box("Lobby_Wall_S", LOBBY["x0"] - WALL_T, LOBBY["y0"] - WALL_T, 0,
             LOBBY["x1"] + WALL_T, LOBBY["y0"], LOBBY["z1"], "glass")  # storefront hint
    _bpy_box("Lobby_Wall_W", LOBBY["x0"] - WALL_T, LOBBY["y0"], 0,
             LOBBY["x0"], LOBBY["y1"], LOBBY["z1"], "lobby_wall")
    _bpy_box("Lobby_Wall_E", LOBBY["x1"], LOBBY["y0"], 0,
             LOBBY["x1"] + WALL_T, LOBBY["y1"], LOBBY["z1"], "lobby_wall")

    # ---- Prove-Out Facility shell ----
    _bpy_box("ProveOut_Floor", HIGHBAY["x0"], HIGHBAY["y0"], -0.05,
             HIGHBAY["x1"], HIGHBAY["y1"], 0.0, "cement_floor")
    _bpy_box("ProveOut_Roof", HIGHBAY["x0"], HIGHBAY["y0"], HIGHBAY["z1"],
             HIGHBAY["x1"], HIGHBAY["y1"], HIGHBAY["z1"] + 0.5, "industrial_wall")
    _bpy_box("ProveOut_Wall_W", HIGHBAY["x0"] - WALL_T, HIGHBAY["y0"], 0,
             HIGHBAY["x0"], HIGHBAY["y1"], HIGHBAY["z1"], "industrial_wall")
    _bpy_box("ProveOut_Wall_E", HIGHBAY["x1"], HIGHBAY["y0"], 0,
             HIGHBAY["x1"] + WALL_T, HIGHBAY["y1"], HIGHBAY["z1"], "industrial_wall")

    # ---- Shared Lobby/Prove-Out wall at y=0 with two openings ----
    # First lower opening (Door 1) cut, then for the upper opening (Door 2) we
    # split into a strip above the lobby ceiling line.
    _bpy_wall_with_opening(
        "Shared_Wall_Lower", LOBBY["x0"], LOBBY["x1"], 0.0, LOBBY["z1"],
        opening=dict(x0=DOOR1["x0"], x1=DOOR1["x1"], z0=0.0, z1=DOOR1["z1"]),
        axis="x", mat="industrial_wall",
    )
    # Strip above lobby ceiling, full prove-out width, with Door 2 opening
    _bpy_wall_with_opening(
        "Shared_Wall_Upper", HIGHBAY["x0"], HIGHBAY["x1"], 0.0, HIGHBAY["z1"],
        opening=dict(x0=DOOR2["x0"], x1=DOOR2["x1"], z0=DOOR2["z0"], z1=DOOR2["z1"]),
        axis="x", mat="industrial_wall",
    )
    # Wing strips on shared wall outside lobby width but below upper section
    if HIGHBAY["x0"] < LOBBY["x0"]:
        _bpy_box("Shared_Wall_WingW", HIGHBAY["x0"], -WALL_T/2, 0,
                 LOBBY["x0"], WALL_T/2, LOBBY["z1"], "industrial_wall")
    if HIGHBAY["x1"] > LOBBY["x1"]:
        _bpy_box("Shared_Wall_WingE", LOBBY["x1"], -WALL_T/2, 0,
                 HIGHBAY["x1"], WALL_T/2, LOBBY["z1"], "industrial_wall")

    # ---- North wall of prove-out with three overhead doors ----
    # Build as 4 wall segments separated by 3 overhead-door openings
    seg_xs = [HIGHBAY["x0"]]
    for d in OVERHEAD_DOORS:
        seg_xs += [d["x0"], d["x1"]]
    seg_xs.append(HIGHBAY["x1"])
    for i in range(0, len(seg_xs), 2):
        sx0, sx1 = seg_xs[i], seg_xs[i + 1]
        if sx1 - sx0 > 0.01:
            _bpy_box(f"ProveOut_Wall_N_seg_{i//2}", sx0, HIGHBAY["y1"], 0,
                     sx1, HIGHBAY["y1"] + WALL_T, HIGHBAY["z1"], "industrial_wall")
    # Headers above each overhead door
    for d in OVERHEAD_DOORS:
        _bpy_box(d["name"] + "_panel", d["x0"], HIGHBAY["y1"], d["z0"],
                 d["x1"], HIGHBAY["y1"] + WALL_T/2, d["z1"], "door_overhead")
        _bpy_box(d["name"] + "_header", d["x0"], HIGHBAY["y1"], d["z1"],
                 d["x1"], HIGHBAY["y1"] + WALL_T, HIGHBAY["z1"], "industrial_wall")
        _bpy_text(d["name"] + "_label", "12x14 Overhead Door",
                  (d["x0"] + d["x1"]) / 2 - 3.0, HIGHBAY["y1"] - 0.6, d["z1"] + 1.2,
                  rot_deg_z=180.0, size_ft=0.7)

    # ---- Door panels (visual, color-coded green for active) ----
    _bpy_box(DOOR1["name"] + "_panel", DOOR1["x0"], -0.06, 0,
             DOOR1["x1"], 0.06, DOOR1["z1"], "door_active")
    _bpy_text(DOOR1["name"] + "_label", "ACTIVE DOOR  Lobby > Prove-Out (Level 1)",
              -8.0, -0.7, 8.5, rot_deg_z=0.0, size_ft=0.6)
    _bpy_box(DOOR2["name"] + "_panel", DOOR2["x0"], -0.06, DOOR2["z0"],
             DOOR2["x1"], 0.06, DOOR2["z1"], "door_active")
    _bpy_text(DOOR2["name"] + "_label", "ACTIVE DOOR  Level 2 > Overlook",
              10.0, -0.7, 22.5, rot_deg_z=0.0, size_ft=0.5)

    # ---- Stairs + landing ----
    _bpy_stair("Stair_L1_to_L2", STAIR["x0"], STAIR["x1"],
               STAIR["y_start"], STAIR["risers"], STAIR["riser"], STAIR["tread"])
    _bpy_box("Stair_Landing", LANDING["x0"], LANDING["y0"], OVERLOOK_Z - 0.1,
             LANDING["x1"], LANDING["y1"], OVERLOOK_Z, "overlook_floor")
    # Stair guardrails (both sides)
    _bpy_box("Stair_Rail_W", STAIR["x0"], STAIR["y_start"], 0,
             STAIR["x0"] + 0.15, LANDING["y1"], OVERLOOK_Z + 4.0, "guardrail")
    _bpy_box("Stair_Rail_E", STAIR["x1"] - 0.15, STAIR["y_start"], 0,
             STAIR["x1"], LANDING["y1"], OVERLOOK_Z + 4.0, "guardrail")

    # ---- Overlook deck (in prove-out, projecting from south wall) ----
    _bpy_box("Overlook_Deck", OVERLOOK["x0"], OVERLOOK["y0"], OVERLOOK_Z - 0.5,
             OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z, "overlook_floor")
    _bpy_box("Overlook_AccentBand", OVERLOOK["x0"], OVERLOOK["y1"] - 0.4, OVERLOOK_Z - 0.6,
             OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z, "accent_warm")
    # Guardrails on N, E, W (open edges)
    _bpy_box("Overlook_Guard_N", OVERLOOK["x0"], OVERLOOK["y1"] - 0.15, OVERLOOK_Z,
             OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z + 4.0, "guardrail")
    _bpy_box("Overlook_Guard_E", OVERLOOK["x1"] - 0.15, OVERLOOK["y0"], OVERLOOK_Z,
             OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z + 4.0, "guardrail")
    _bpy_box("Overlook_Guard_W", OVERLOOK["x0"], OVERLOOK["y0"], OVERLOOK_Z,
             OVERLOOK["x0"] + 0.15, OVERLOOK["y1"], OVERLOOK_Z + 4.0, "guardrail")

    # ---- Equipment placeholders ----
    for eq in EQUIPMENT:
        _bpy_box(eq["name"], eq["x0"], eq["y0"], eq["z0"],
                 eq["x1"], eq["y1"], eq["z1"], "equipment")
        _bpy_text(eq["name"] + "_label", eq["name"].replace("_", " "),
                  eq["x0"], eq["y1"] + 0.5, eq["z1"] + 0.5, rot_deg_z=0.0, size_ft=0.7)
    # Forklift path (yellow translucent floor strip)
    _bpy_box(FORKLIFT_PATH["name"],
             FORKLIFT_PATH["x0"], FORKLIFT_PATH["y0"], 0.01,
             FORKLIFT_PATH["x1"], FORKLIFT_PATH["y1"], 0.06, "forklift_path")
    _bpy_text("Forklift_Path_label", "Forklift / Clearance Path  42 ft x 8 ft",
              FORKLIFT_PATH["x0"], FORKLIFT_PATH["y0"] + 4.0, 0.2,
              rot_deg_z=0.0, size_ft=0.6)

    # ---- Educational boards ----
    for (bname, title, body, x, y, z, rot) in BOARDS:
        # Frame + face
        _bpy_box(bname + "_frame", x - 4.0, y - 0.1, z - 0.1,
                 x + 4.0, y + 0.1, z + 5.5, "board_frame")
        _bpy_box(bname + "_face",  x - 3.8, y - 0.05, z,
                 x + 3.8, y + 0.05, z + 5.3, "board_face")
        _bpy_text(bname + "_title", title, x - 3.6, y - 0.12, z + 4.5,
                  rot_deg_z=rot, size_ft=0.6)
        # Wrap body to ~46 chars
        words = body.split()
        line, lines = "", []
        for w in words:
            if len(line) + len(w) + 1 > 46:
                lines.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        if line:
            lines.append(line)
        for i, ln in enumerate(lines[:8]):
            _bpy_text(f"{bname}_body_{i}", ln, x - 3.6, y - 0.12, z + 3.7 - i * 0.5,
                      rot_deg_z=rot, size_ft=0.32)

    # ---- Blocked-boundary barriers ----
    for b in BARRIERS:
        _bpy_box(b["name"], b["x0"], b["y0"], b["z0"],
                 b["x1"], b["y1"], b["z1"], "barrier")
    # Barrier signage (a few strategic spots)
    _bpy_text("Sign_MVP_S",  "MVP REVIEW BOUNDARY",  -8.0, -39.5, 4.0, 0.0, 0.8)
    _bpy_text("Sign_MVP_N",  "MVP REVIEW BOUNDARY",  -8.0, 189.5, 4.0, 180.0, 0.8)
    _bpy_text("Sign_Tyler",  "Existing Tyler sealed - no entry",
              -29.5, 158.0, 6.0, 90.0, 0.6)
    _bpy_text("Sign_QA",     "Unresolved building areas excluded from this prototype",
              48.0, 80.0, 5.0, -90.0, 0.5)
    _bpy_text("Sign_Manual", "This area requires future manual vector confirmation",
              48.0, 60.0, 5.0, -90.0, 0.5)

    # ---- Player spawn marker ----
    bpy.ops.object.empty_add(type="ARROWS",
                              location=(0.0 * FT, -28.0 * FT, 5.5 * FT))
    bpy.context.active_object.name = "PLAYER_SPAWN"

    # ---- Sun + camera ----
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 60 * FT))
    bpy.context.active_object.data.energy = 4.0
    bpy.ops.object.camera_add(location=(0 * FT, -40 * FT, 6 * FT),
                               rotation=(math.radians(80), 0, 0))

    os.makedirs(OUT_DIR, exist_ok=True)
    blend_path = os.path.join(OUT_DIR, BASE_NAME + ".blend")
    fbx_path   = os.path.join(OUT_DIR, BASE_NAME + ".fbx")
    glb_path   = os.path.join(OUT_DIR, BASE_NAME + ".glb")

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    bpy.ops.export_scene.fbx(filepath=fbx_path, apply_unit_scale=True,
                              global_scale=1.0, axis_forward="-Z", axis_up="Y")
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format="GLB")
    print(f"Wrote: {blend_path}\nWrote: {fbx_path}\nWrote: {glb_path}")


if __name__ == "__main__":
    if HAS_BPY:
        build_with_blender()
    else:
        print("Blender (bpy) not available. Run with:")
        print("  blender --background --python tools/build_class_demo_entry_proveout_overlook.py")
        print("To produce a .glb without Blender, run:")
        print("  python3 tools/build_class_demo_glb.py")
        sys.exit(0)
