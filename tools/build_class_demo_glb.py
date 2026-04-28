"""
Standalone GLB generator for the NIMA Phase II Spatial Review Learning Lab.

No Blender required. Pure-Python writes a glTF 2.0 binary (.glb) that imports
directly into Unity (via UnityGLTF, glTFast) and any other glTF-aware viewer.

Run:
    python3 tools/build_class_demo_glb.py

Produces:
    build_outputs/class_demo_learning_lab/NIMA_PhaseII_SpatialReview_LearningLab.glb

Layout, materials, and dimensions mirror the Blender script
tools/build_class_demo_entry_proveout_overlook.py so the two stay in sync.
Coordinate convention in the source: +X east, +Y north (depth into prove-out),
+Z up. We export glTF Y-up by remapping (X,Y,Z) -> (X, Z, -Y) at write time.

Design units are FEET; we multiply by FT (= 0.3048) at write time so the GLB
is in meters (Unity-friendly).
"""

import json
import os
import struct

FT = 0.3048

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "build_outputs", "class_demo_learning_lab",
)
BASE_NAME = "NIMA_PhaseII_SpatialReview_LearningLab"

# ---------------------------------------------------------------------------
# Layout (feet) -- KEEP IN SYNC with build_class_demo_entry_proveout_overlook.py
# ---------------------------------------------------------------------------
LOBBY = dict(x0=-21.0, x1=21.0, y0=-32.0, y1=0.0,  z0=0.0, z1=24.0)
HIGHBAY = dict(x0=-30.4, x1=30.4, y0=0.0,  y1=176.0, z0=0.0, z1=38.96)
WALL_T = 0.5

DOOR1 = dict(name="Door_Lobby_To_ProveOut_Level1",
             x0=-3.0, x1=3.0, y=0.0, z0=0.0, z1=8.0)
DOOR2 = dict(name="Door_Level2_To_ProveOut_Overlook",
             x0=15.0, x1=21.0, y=0.0, z0=14.0, z1=22.0)

OVERLOOK_Z = 14.0
LANDING = dict(x0=15.0, x1=21.0, y0=-8.0, y1=0.0)
OVERLOOK = dict(x0=3.0, x1=27.0, y0=0.0, y1=10.0)

STAIR = dict(x0=15.0, x1=21.0, y_start=-30.0, risers=24,
             riser=14.0/24.0, tread=1.0)

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
                     x0=10.0, x1=18.0, y0=20.0, y1=160.0, z0=0.0, z1=0.05)

BARRIERS = [
    dict(name="MVP_Barrier_W", x0=-50.0, x1=-49.0, y0=-40.0, y1=180.0, z0=0.0, z1=8.0),
    dict(name="MVP_Barrier_E", x0=49.0, x1=50.0, y0=-40.0, y1=180.0, z0=0.0, z1=8.0),
    dict(name="MVP_Barrier_S", x0=-50.0, x1=50.0, y0=-41.0, y1=-40.0, z0=0.0, z1=8.0),
    dict(name="MVP_Barrier_N", x0=-50.0, x1=50.0, y0=190.0, y1=191.0, z0=0.0, z1=8.0),
    dict(name="MVP_Barrier_TylerSeal", x0=-30.4, x1=-29.9, y0=140.0, y1=176.0, z0=0.0, z1=10.0),
]

BOARDS = [
    ("Board_Title", "NIMA Phase II Spatial Review Learning Lab",
     "A simplified class prototype for learning spatial review, equipment fit, "
     "workflow, and QA-gated model development.",
     -18.0, -31.5, 4.0),
    ("Board_Entry", "Learning Experience",
     "This prototype focuses on the entry sequence, controlled access, "
     "Prove-Out Facility, equipment fit, loading access, and overlook-based observation.",
     -19.5, -25.0, 4.0),
    ("Board_NIMA", "What Does NIMA Do?",
     "NIMA develops technologies, applications, partnerships, facilities, and a "
     "highly-qualified workforce for emerging materials. This learning lab focuses on "
     "how a Prove-Out Facility supports prototyping, testing, and applied research.",
     -19.5, -18.0, 4.0),
    ("Board_RDPark", "Emerging R+D Park Context",
     "The Prove-Out Facility is part of a larger innovation ecosystem with Tyler "
     "Research Center, NIMA, Emerging Technologies, and the KBI/PSU site.",
     -19.5, -11.0, 4.0),
    ("Board_PhaseII", "Phase II Expansion",
     "The expansion adds approximately 24,230 square feet and supports future "
     "research, testing, prototyping, and workforce development.",
     19.5, -18.0, 4.0),
    ("Board_ProveOut", "Purpose of the Prove-Out Facility (high-bay volume)",
     "The Prove-Out Facility is the large high-bay space where equipment layout, "
     "clearances, workflow, and loading access can be evaluated before final build-out.",
     -29.0, 8.0, 6.0),
    ("Board_EquipFit", "Equipment-Fit Review",
     "Learners inspect whether test rigs, machine cells, assembly tables, robot work "
     "cells, and forklift paths fit safely within the Prove-Out Facility.",
     -29.0, 36.0, 6.0),
    ("Board_Overlook", "Prove-Out Facility Overlook",
     "The overlook lets stakeholders observe the Prove-Out Facility from above and "
     "review workflow, safety, and equipment relationships without entering the active "
     "production floor.",
     15.0, 5.0, 18.0),
    ("Board_QA", "QA Boundary",
     "This prototype intentionally blocks unresolved areas instead of presenting "
     "unverified geometry as complete. The goal is to support spatial learning, not "
     "final construction documentation.",
     29.0, 90.0, 6.0),
    ("Board_Reflection", "Main Takeaways",
     "Spatial VR helps learners understand scale, equipment fit, workflow, and design "
     "review. The process also showed why generated geometry needs QA before being used "
     "as an immersive walkthrough.",
     -29.0, 150.0, 6.0),
]

# Material name -> RGBA
MAT = {
    "cement_floor":   (0.62, 0.62, 0.60, 1.0),
    "industrial_wall":(0.93, 0.91, 0.86, 1.0),
    "lobby_floor":    (0.78, 0.70, 0.58, 1.0),
    "lobby_wall":     (0.96, 0.93, 0.88, 1.0),
    "glass":          (0.55, 0.72, 0.86, 0.45),
    "stair":          (0.55, 0.55, 0.58, 1.0),
    "guardrail":      (0.20, 0.22, 0.25, 1.0),
    "door_active":    (0.18, 0.62, 0.35, 1.0),
    "door_overhead":  (0.40, 0.42, 0.48, 1.0),
    "equipment":      (0.55, 0.58, 0.65, 1.0),
    "forklift_path":  (0.95, 0.78, 0.10, 1.0),
    "board_face":     (0.97, 0.97, 0.95, 1.0),
    "board_frame":    (0.18, 0.20, 0.25, 1.0),
    "barrier":        (0.85, 0.18, 0.18, 0.85),
    "overlook_floor": (0.82, 0.74, 0.62, 1.0),
    "accent_warm":    (0.78, 0.55, 0.32, 1.0),
}

# ---------------------------------------------------------------------------
# Minimal glTF 2.0 binary writer
# ---------------------------------------------------------------------------
class GltfBuilder:
    def __init__(self):
        self.buf = bytearray()
        self.buffer_views = []
        self.accessors = []
        self.meshes = []
        self.nodes = []
        self.materials = []
        self.material_index = {}  # name -> index
        self.scene_nodes = []

    # ------- buffer helpers -------
    def _pad4(self, ba):
        while len(ba) % 4 != 0:
            ba.append(0)

    def _add_view(self, data_bytes, target=None):
        self._pad4(self.buf)
        offset = len(self.buf)
        self.buf.extend(data_bytes)
        view = dict(buffer=0, byteOffset=offset, byteLength=len(data_bytes))
        if target is not None:
            view["target"] = target
        self.buffer_views.append(view)
        return len(self.buffer_views) - 1

    def _add_accessor_vec3(self, view_idx, count, mins, maxs):
        self.accessors.append(dict(
            bufferView=view_idx, componentType=5126, count=count,
            type="VEC3", min=mins, max=maxs,
        ))
        return len(self.accessors) - 1

    def _add_accessor_scalar_uint16(self, view_idx, count):
        self.accessors.append(dict(
            bufferView=view_idx, componentType=5123, count=count, type="SCALAR",
        ))
        return len(self.accessors) - 1

    # ------- material -------
    def material(self, name):
        if name in self.material_index:
            return self.material_index[name]
        rgba = MAT[name]
        m = dict(
            name=name,
            pbrMetallicRoughness=dict(
                baseColorFactor=list(rgba),
                metallicFactor=0.05,
                roughnessFactor=0.85,
            ),
            doubleSided=True,
        )
        if rgba[3] < 1.0:
            m["alphaMode"] = "BLEND"
        self.materials.append(m)
        idx = len(self.materials) - 1
        self.material_index[name] = idx
        return idx

    # ------- mesh primitive: axis-aligned box -------
    def add_box(self, name, x0, y0, z0, x1, y1, z1, mat_name, extras=None):
        # Convert ft -> m AND remap (X,Y,Z up) -> glTF Y-up: (X, Z, -Y)
        def m(p):
            x, y, z = p
            return (x * FT, z * FT, -y * FT)

        corners = [
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        ]
        verts = [m(c) for c in corners]
        # 12 triangles, 6 faces, indices into verts
        faces = [
            (0, 1, 2), (0, 2, 3),       # bottom -Y(world Z low)
            (4, 6, 5), (4, 7, 6),       # top
            (0, 4, 5), (0, 5, 1),       # front (y0)
            (2, 6, 7), (2, 7, 3),       # back (y1)
            (1, 5, 6), (1, 6, 2),       # right (x1)
            (0, 3, 7), (0, 7, 4),       # left  (x0)
        ]
        # vertex buffer
        vbytes = bytearray()
        for v in verts:
            vbytes.extend(struct.pack("<fff", *v))
        # bbox
        xs = [v[0] for v in verts]; ys = [v[1] for v in verts]; zs = [v[2] for v in verts]
        v_view = self._add_view(bytes(vbytes), target=34962)
        v_acc = self._add_accessor_vec3(v_view, len(verts),
                                         [min(xs), min(ys), min(zs)],
                                         [max(xs), max(ys), max(zs)])
        # index buffer
        ibytes = bytearray()
        for f in faces:
            for i in f:
                ibytes.extend(struct.pack("<H", i))
        # pad index buffer to 4-byte boundary inside the buffer; component-stride
        # is fine but the GLB BIN chunk itself must be 4-byte padded at the end.
        i_view = self._add_view(bytes(ibytes), target=34963)
        i_acc = self._add_accessor_scalar_uint16(i_view, len(faces) * 3)

        prim = dict(attributes=dict(POSITION=v_acc), indices=i_acc,
                    material=self.material(mat_name), mode=4)
        mesh = dict(name=name, primitives=[prim])
        self.meshes.append(mesh)
        node = dict(name=name, mesh=len(self.meshes) - 1)
        if extras:
            node["extras"] = extras
        self.nodes.append(node)
        node_idx = len(self.nodes) - 1
        self.scene_nodes.append(node_idx)
        return node_idx

    def add_marker(self, name, x, y, z, extras=None):
        # No mesh: just a node with a translation, useful for SPAWN/labels.
        tx, ty, tz = x * FT, z * FT, -y * FT
        node = dict(name=name, translation=[tx, ty, tz])
        if extras:
            node["extras"] = extras
        self.nodes.append(node)
        self.scene_nodes.append(len(self.nodes) - 1)

    # ------- write GLB -------
    def write(self, path):
        gltf = dict(
            asset=dict(version="2.0",
                       generator="NIMA Phase II class demo standalone GLB writer"),
            scene=0,
            scenes=[dict(nodes=list(self.scene_nodes))],
            nodes=self.nodes,
            meshes=self.meshes,
            materials=self.materials,
            accessors=self.accessors,
            bufferViews=self.buffer_views,
            buffers=[dict(byteLength=len(self.buf))],
        )
        json_bytes = bytearray(json.dumps(gltf, separators=(",", ":")).encode("utf-8"))
        while len(json_bytes) % 4 != 0:
            json_bytes.append(0x20)
        bin_bytes = bytearray(self.buf)
        while len(bin_bytes) % 4 != 0:
            bin_bytes.append(0)

        total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
        with open(path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, total_len))
            f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
            f.write(json_bytes)
            f.write(struct.pack("<II", len(bin_bytes), 0x004E4942))
            f.write(bin_bytes)


# ---------------------------------------------------------------------------
# Scene assembly
# ---------------------------------------------------------------------------
def build_scene():
    g = GltfBuilder()

    # ---- Lobby ----
    g.add_box("Lobby_Floor", LOBBY["x0"], LOBBY["y0"], -0.05,
              LOBBY["x1"], LOBBY["y1"], 0.0, "lobby_floor")
    g.add_box("Lobby_Ceiling", LOBBY["x0"], LOBBY["y0"], LOBBY["z1"],
              LOBBY["x1"], LOBBY["y1"], LOBBY["z1"] + 0.4, "lobby_wall")
    g.add_box("Lobby_Wall_S", LOBBY["x0"] - WALL_T, LOBBY["y0"] - WALL_T, 0,
              LOBBY["x1"] + WALL_T, LOBBY["y0"], LOBBY["z1"], "glass")
    g.add_box("Lobby_Wall_W", LOBBY["x0"] - WALL_T, LOBBY["y0"], 0,
              LOBBY["x0"], LOBBY["y1"], LOBBY["z1"], "lobby_wall")
    g.add_box("Lobby_Wall_E", LOBBY["x1"], LOBBY["y0"], 0,
              LOBBY["x1"] + WALL_T, LOBBY["y1"], LOBBY["z1"], "lobby_wall")

    # ---- Prove-Out Facility shell ----
    g.add_box("ProveOut_Floor", HIGHBAY["x0"], HIGHBAY["y0"], -0.05,
              HIGHBAY["x1"], HIGHBAY["y1"], 0.0, "cement_floor")
    g.add_box("ProveOut_Roof", HIGHBAY["x0"], HIGHBAY["y0"], HIGHBAY["z1"],
              HIGHBAY["x1"], HIGHBAY["y1"], HIGHBAY["z1"] + 0.5, "industrial_wall")
    g.add_box("ProveOut_Wall_W", HIGHBAY["x0"] - WALL_T, HIGHBAY["y0"], 0,
              HIGHBAY["x0"], HIGHBAY["y1"], HIGHBAY["z1"], "industrial_wall")
    g.add_box("ProveOut_Wall_E", HIGHBAY["x1"], HIGHBAY["y0"], 0,
              HIGHBAY["x1"] + WALL_T, HIGHBAY["y1"], HIGHBAY["z1"], "industrial_wall")

    # ---- Shared wall (lobby/prove-out) at y=0 with two openings ----
    # Lower band (lobby height) with Door 1 cut
    def wall_strip_with_opening(name, x0, x1, y, z_top, ox0, ox1, oz0, oz1, mat):
        t = WALL_T
        if ox0 > x0:
            g.add_box(f"{name}_L", x0, y - t/2, 0, ox0, y + t/2, z_top, mat)
        if ox1 < x1:
            g.add_box(f"{name}_R", ox1, y - t/2, 0, x1, y + t/2, z_top, mat)
        if oz0 > 0:
            g.add_box(f"{name}_B", ox0, y - t/2, 0, ox1, y + t/2, oz0, mat)
        if oz1 < z_top:
            g.add_box(f"{name}_A", ox0, y - t/2, oz1, ox1, y + t/2, z_top, mat)

    wall_strip_with_opening("Shared_Wall_Lower",
                            LOBBY["x0"], LOBBY["x1"], 0.0, LOBBY["z1"],
                            DOOR1["x0"], DOOR1["x1"], DOOR1["z0"], DOOR1["z1"],
                            "industrial_wall")
    # Upper band (above lobby ceiling) with Door 2 cut, full prove-out width
    wall_strip_with_opening("Shared_Wall_Upper",
                            HIGHBAY["x0"], HIGHBAY["x1"], 0.0, HIGHBAY["z1"],
                            DOOR2["x0"], DOOR2["x1"], DOOR2["z0"], DOOR2["z1"],
                            "industrial_wall")
    # Wing strips (lobby side) outside lobby width and below upper section
    if HIGHBAY["x0"] < LOBBY["x0"]:
        g.add_box("Shared_Wall_WingW", HIGHBAY["x0"], -WALL_T/2, 0,
                  LOBBY["x0"], WALL_T/2, LOBBY["z1"], "industrial_wall")
    if HIGHBAY["x1"] > LOBBY["x1"]:
        g.add_box("Shared_Wall_WingE", LOBBY["x1"], -WALL_T/2, 0,
                  HIGHBAY["x1"], WALL_T/2, LOBBY["z1"], "industrial_wall")

    # ---- Active door panels (visual cue, color-coded green) ----
    g.add_box(DOOR1["name"], DOOR1["x0"], -0.06, 0.0,
              DOOR1["x1"], 0.06, DOOR1["z1"], "door_active",
              extras=dict(role="active_door",
                          target="ProveOut_Facility_Level1",
                          width_ft=6.0, height_ft=8.0))
    g.add_box(DOOR2["name"], DOOR2["x0"], -0.06, DOOR2["z0"],
              DOOR2["x1"], 0.06, DOOR2["z1"], "door_active",
              extras=dict(role="active_door",
                          target="ProveOut_Facility_Overlook",
                          width_ft=6.0, height_ft=8.0))

    # ---- North wall of prove-out with three overhead doors ----
    seg_xs = [HIGHBAY["x0"]]
    for d in OVERHEAD_DOORS:
        seg_xs += [d["x0"], d["x1"]]
    seg_xs.append(HIGHBAY["x1"])
    for i in range(0, len(seg_xs), 2):
        sx0, sx1 = seg_xs[i], seg_xs[i + 1]
        if sx1 - sx0 > 0.01:
            g.add_box(f"ProveOut_Wall_N_seg_{i//2}", sx0, HIGHBAY["y1"], 0,
                      sx1, HIGHBAY["y1"] + WALL_T, HIGHBAY["z1"], "industrial_wall")
    for d in OVERHEAD_DOORS:
        g.add_box(d["name"], d["x0"], HIGHBAY["y1"], d["z0"],
                  d["x1"], HIGHBAY["y1"] + WALL_T/2, d["z1"], "door_overhead",
                  extras=dict(role="overhead_door", label="12x14 Overhead Door",
                              width_ft=12.0, height_ft=14.0,
                              note="Visual only - not interactive"))
        g.add_box(d["name"] + "_header", d["x0"], HIGHBAY["y1"], d["z1"],
                  d["x1"], HIGHBAY["y1"] + WALL_T, HIGHBAY["z1"], "industrial_wall")

    # ---- Stairs ----
    for n in range(STAIR["risers"]):
        y0 = STAIR["y_start"] + n * STAIR["tread"]
        y1 = y0 + STAIR["tread"]
        z1 = (n + 1) * STAIR["riser"]
        g.add_box(f"Stair_step_{n:02d}", STAIR["x0"], y0, 0.0,
                  STAIR["x1"], y1, z1, "stair")
    # Landing
    g.add_box("Stair_Landing", LANDING["x0"], LANDING["y0"], OVERLOOK_Z - 0.1,
              LANDING["x1"], LANDING["y1"], OVERLOOK_Z, "overlook_floor")
    # Stair guardrails
    g.add_box("Stair_Rail_W", STAIR["x0"], STAIR["y_start"], 0,
              STAIR["x0"] + 0.15, LANDING["y1"], OVERLOOK_Z + 4.0, "guardrail")
    g.add_box("Stair_Rail_E", STAIR["x1"] - 0.15, STAIR["y_start"], 0,
              STAIR["x1"], LANDING["y1"], OVERLOOK_Z + 4.0, "guardrail")

    # ---- Overlook deck (in prove-out, projecting from south wall) ----
    g.add_box("Overlook_Deck", OVERLOOK["x0"], OVERLOOK["y0"], OVERLOOK_Z - 0.5,
              OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z, "overlook_floor")
    g.add_box("Overlook_AccentBand",
              OVERLOOK["x0"], OVERLOOK["y1"] - 0.4, OVERLOOK_Z - 0.6,
              OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z, "accent_warm")
    g.add_box("Overlook_Guard_N", OVERLOOK["x0"], OVERLOOK["y1"] - 0.15, OVERLOOK_Z,
              OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z + 4.0, "guardrail")
    g.add_box("Overlook_Guard_E", OVERLOOK["x1"] - 0.15, OVERLOOK["y0"], OVERLOOK_Z,
              OVERLOOK["x1"], OVERLOOK["y1"], OVERLOOK_Z + 4.0, "guardrail")
    g.add_box("Overlook_Guard_W", OVERLOOK["x0"], OVERLOOK["y0"], OVERLOOK_Z,
              OVERLOOK["x0"] + 0.15, OVERLOOK["y1"], OVERLOOK_Z + 4.0, "guardrail")

    # ---- Equipment ----
    for eq in EQUIPMENT:
        g.add_box(eq["name"], eq["x0"], eq["y0"], eq["z0"],
                  eq["x1"], eq["y1"], eq["z1"], "equipment",
                  extras=dict(role="equipment", label=eq["name"].replace("_", " ")))
    g.add_box(FORKLIFT_PATH["name"],
              FORKLIFT_PATH["x0"], FORKLIFT_PATH["y0"], 0.01,
              FORKLIFT_PATH["x1"], FORKLIFT_PATH["y1"], 0.06, "forklift_path",
              extras=dict(role="forklift_path",
                          label="Forklift / Clearance Path 42 ft x 8 ft"))

    # ---- Boards ----
    for (bname, title, body, x, y, z) in BOARDS:
        g.add_box(bname + "_frame", x - 4.0, y - 0.1, z - 0.1,
                  x + 4.0, y + 0.1, z + 5.5, "board_frame")
        g.add_box(bname + "_face",  x - 3.8, y - 0.05, z,
                  x + 3.8, y + 0.05, z + 5.3, "board_face",
                  extras=dict(role="board", title=title, body=body))

    # ---- Barriers (red translucent) ----
    for b in BARRIERS:
        g.add_box(b["name"], b["x0"], b["y0"], b["z0"],
                  b["x1"], b["y1"], b["z1"], "barrier",
                  extras=dict(role="mvp_boundary",
                              label="MVP REVIEW BOUNDARY"))

    # ---- Markers (no geometry) ----
    g.add_marker("PLAYER_SPAWN", 0.0, -28.0, 5.5,
                 extras=dict(role="player_spawn",
                             facing_deg=0.0,
                             eye_height_ft=5.5))
    g.add_marker("MARKER_Door1_Trigger", 0.0, -1.0, 4.0,
                 extras=dict(role="trigger_volume",
                             door="Door_Lobby_To_ProveOut_Level1"))
    g.add_marker("MARKER_Door2_Trigger", 18.0, -1.0, OVERLOOK_Z + 4.0,
                 extras=dict(role="trigger_volume",
                             door="Door_Level2_To_ProveOut_Overlook"))
    g.add_marker("MARKER_Boundary_Notice_S", 0.0, -39.0, 4.0,
                 extras=dict(role="boundary_sign",
                             text="MVP REVIEW BOUNDARY - "
                                  "Unresolved building areas excluded from this prototype"))
    g.add_marker("MARKER_Boundary_Notice_TylerSeal", -29.0, 158.0, 6.0,
                 extras=dict(role="boundary_sign",
                             text="Existing Tyler sealed - no entry"))
    g.add_marker("MARKER_Boundary_Notice_Manual", 48.0, 60.0, 5.0,
                 extras=dict(role="boundary_sign",
                             text="This area requires future manual vector confirmation"))

    return g


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    g = build_scene()
    glb_path = os.path.join(OUT_DIR, BASE_NAME + ".glb")
    g.write(glb_path)
    size_kb = os.path.getsize(glb_path) / 1024.0
    print(f"Wrote {glb_path} ({size_kb:.1f} KB)")
    print(f"Meshes: {len(g.meshes)}, Materials: {len(g.materials)}, "
          f"Nodes: {len(g.nodes)}")


if __name__ == "__main__":
    main()
