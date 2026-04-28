# NIMA Phase II Spatial Review Learning Lab: Prove-Out Facility Walkthrough

## What this demo is

My implementation is a spatial-review learning lab for NIMA Phase II.
Learners spawn in the entry/lobby zone, then move into the Prove-Out Facility
to study equipment fit, loading access, workflow, scale, and overlook-based
observation. The prototype intentionally blocks unresolved areas rather than
pretending the full building is complete.

It is a **separate class/demo build**. It was created so participants can
actually tour the learning experience instead of staring at a partial QA
package.

## What this demo is NOT

- It is **not** the formal NIMA Phase II RC1 spatial review package.
- It is **not** final BIM, construction documentation, or a coordinated model.
- It is **not** a full-scene merge with the Existing Tyler Center interior.
- It is **not** a replacement for QA-gated geometry review.
- The two operable doors are the only functional doors. Every other opening
  is decorative.

The formal RC1 staging files (`building_envelope.json`,
`scene_partial_current_scope.json`, `scene_partial_expanded_scope_review.json`,
`NIMA_PhaseII_partial_MVP_spatial_review_package_RC1.zip`, and any approved
RC1 source files) were **not modified** by this build.

## Files in this folder

| File | Purpose |
|---|---|
| `NIMA_PhaseII_SpatialReview_LearningLab.glb`  | Pre-generated binary glTF, ready to import. |
| `NIMA_PhaseII_SpatialReview_LearningLab.fbx`  | Generate locally via Blender (see below). |
| `NIMA_PhaseII_SpatialReview_LearningLab.blend`| Generate locally via Blender (see below). |
| `README_UNITY_IMPORT.md` | This file. |
| `TOUR_SCRIPT.md` | Step-by-step class tour script. |
| `unity_scripts/DoorTransition.cs` | Trigger-based active-door behavior. |
| `unity_scripts/TurnBackBoundary.cs` | MVP boundary turn-back / return behavior. |
| `unity_scripts/LearningZoneTrigger.cs` | Pop-up text near each educational board. |
| `unity_scripts/InteractableDoor.cs` | Optional press-E-to-swing door visual. |

## How the model was generated

This environment did not have Blender installed, so the `.glb` was produced
by a self-contained pure-Python writer that emits valid glTF 2.0 binary
(magic `0x46546C67`, version 2). It is fine to use the GLB directly in Unity
with `glTFast` or `UnityGLTF`.

To regenerate the `.blend` and `.fbx` locally (where Blender is installed):

```
blender --background --python tools/build_class_demo_entry_proveout_overlook.py
```

To regenerate just the `.glb` again with no Blender required:

```
python3 tools/build_class_demo_glb.py
```

Both scripts share the same dimensions, layout, and material list, so the
outputs are interchangeable.

## How to import the FBX (or GLB) into Unity

1. Create a new Unity 3D (URP) project, e.g. `NIMA_LearningLab_Unity`.
2. Drag `NIMA_PhaseII_SpatialReview_LearningLab.fbx` (or `.glb`) into
   `Assets/Models/`. If using GLB, install the `glTFast` package via the
   Package Manager first.
3. With the model selected in the Project view, set:
   - **Scale Factor**: 1
   - **Convert Units**: off (the file is already in meters)
   - **Import Cameras / Lights**: optional
   - **Generate Colliders**: on (for floors, walls, stairs)
4. Drag the prefab into the scene. Position at world origin.
5. Copy the four `.cs` files from `unity_scripts/` into `Assets/Scripts/`.

### Player setup

1. Add an `XR Origin` (for VR) or a simple `FirstPersonController` from the
   Starter Assets. Tag the player object **Player**.
2. Position the player at the GLB node `PLAYER_SPAWN`. This sits in the
   lobby at world (X=0, Y=5.5 ft, Z=-28 ft) i.e. (0 m, 1.68 m, -8.53 m)
   facing +Z (toward the prove-out facility).
3. If your model imports with a parent rotation (axis flip), parent the
   spawn marker as a sibling of the model so its world transform is
   inherited correctly.

### Wiring the two working doors

The two operable doors are color-coded green in the model.

| Door | Node name | Suggested setup |
|---|---|---|
| Lobby to Prove-Out Facility (Level 1) | `Door_Lobby_To_ProveOut_Level1` | Add a child empty `Door1_Trigger` with a 6 ft x 8 ft `BoxCollider (Is Trigger)`. Add `DoorTransition.cs`, set `doorName` to the node name. Optionally drop a `Transform` two feet inside the prove-out facility into `exitTarget` to teleport the player past the threshold. |
| Level 2 Landing to Prove-Out Overlook | `Door_Level2_To_ProveOut_Overlook` | Same pattern at `Z = OVERLOOK_Z (14 ft)` in the upper opening. The marker `MARKER_Door2_Trigger` shows the suggested position. |

Set `requireKeyPress = false` for "walk through" behavior, or `true` to
require **E**.

If you want a swing animation on the visible green door panel, also attach
`InteractableDoor.cs` to the panel itself. This is purely visual.

### Wiring the educational boards

The 10 boards are independent meshes named `Board_Title`, `Board_Entry`,
`Board_NIMA`, `Board_RDPark`, `Board_PhaseII`, `Board_ProveOut`,
`Board_EquipFit`, `Board_Overlook`, `Board_QA`, `Board_Reflection`. Each has
a frame (`*_frame`) and a face (`*_face`).

For each board:

1. Create a child empty `Trigger` with a roughly 6 ft x 6 ft x 4 ft
   `BoxCollider (Is Trigger)`.
2. Add `LearningZoneTrigger.cs`. Paste the title and body from
   `TOUR_SCRIPT.md` (or read them from the GLB node `extras` if you wrote
   an importer for that).

The board face textures are flat colors in this build because GLB cannot
embed sharp vector text without baked atlases. The triggers + on-screen
popups carry the actual reading content.

### Wiring the blocked / turn-back boundaries

There are five MVP barrier walls in the GLB (red, semi-transparent), named
`MVP_Barrier_W`, `MVP_Barrier_E`, `MVP_Barrier_S`, `MVP_Barrier_N`, and
`MVP_Barrier_TylerSeal`. To make them turn the player around:

1. Convert each barrier's collider to a `BoxCollider (Is Trigger)` (or wrap
   the barrier with a trigger child slightly larger than the wall).
2. Add `TurnBackBoundary.cs`.
3. Set `safeReturnPoint` to a Transform inside the lobby (the
   `PLAYER_SPAWN` marker is a good default).

Three pre-placed `MARKER_Boundary_Notice_*` empties carry the suggested
turn-back signage strings:

- `MVP REVIEW BOUNDARY - Unresolved building areas excluded from this prototype`
- `Existing Tyler sealed - no entry`
- `This area requires future manual vector confirmation`

## What areas are blocked

- Anything outside the Lobby + Prove-Out Facility envelope (perimeter
  barriers north / south / east / west).
- The west wall of the prove-out, where the model would otherwise abut the
  Existing Tyler Center (`MVP_Barrier_TylerSeal`).
- Side rooms, support spaces, mechanical, and the actual east front-of-house
  beyond the spawn area are intentionally not modeled.

## Player spawn

GLB node: `PLAYER_SPAWN`. Coordinates after the Y-up conversion baked into
the GLB:

- World position: **X = 0.000 m, Y = 1.676 m (5.5 ft), Z = 8.534 m (-28 ft)**
- Facing: +Z (toward the Door 1 panel and the Prove-Out Facility)
- Eye height: 5.5 ft, suitable for both desktop FirstPerson and seated VR.

## Known limitations

- Stairs are simplified rectangular blocks with 24 risers at ~7 in / 12 in.
  They are walkable but not architecturally detailed.
- The `.glb` does not embed text; board copy lives in
  `LearningZoneTrigger.cs` and in `TOUR_SCRIPT.md`.
- The three overhead doors are visual panels; they do not animate or open.
- The lobby south wall is rendered as a translucent storefront hint, not a
  full curtain wall system.
- This build uses approximate dimensions per the brief; it is not a
  measured BIM.
- No cars, exterior site, landscape, or interior furniture beyond the
  equipment placeholders.

## Presentation framing

Use this wording verbatim when introducing the experience:

> My implementation is a spatial-review learning lab for NIMA Phase II.
> Learners spawn in the entry/lobby zone, then move into the Prove-Out
> Facility to study equipment fit, loading access, workflow, scale, and
> overlook-based observation. The prototype intentionally blocks unresolved
> areas rather than pretending the full building is complete.

## Layout summary (feet)

| Element | Footprint / Size | Position (X, Y, Z = up) |
|---|---|---|
| Lobby                       | 42 W x 32 D x 24 H        | x[-21,21], y[-32,0], z[0,24] |
| Prove-Out Facility          | 60.8 W x 176 L x 38.96 H  | x[-30.4,30.4], y[0,176], z[0,38.96] |
| Door 1 (Level 1, active)    | 6 W x 8 H                 | shared wall, centered at x=0, z[0,8] |
| Door 2 (Level 2, active)    | 6 W x 8 H                 | shared wall, x[15,21], z[14,22] |
| Stair                       | 6 W, 24 risers            | x[15,21], y[-30,-6], z[0,14] |
| Landing                     | 6 W x 8 D                 | x[15,21], y[-8,0], z=14 |
| Overlook                    | 24 W x 10 D               | x[3,27], y[0,10], z=14 |
| Overlook guardrail          | 4 ft tall                 | N/E/W open edges |
| Overhead door (x3)          | 12 W x 14 H each          | north wall of prove-out, y=176 |
| Forklift / Clearance Path   | 8 W x 140 L (>= 42 req)   | x[10,18], y[20,160] |

## Manual steps before class

1. Run `python3 tools/build_class_demo_glb.py` once on your local machine
   to confirm the GLB regenerates (already done in this commit).
2. (Optional) Run `blender --background --python tools/build_class_demo_entry_proveout_overlook.py`
   to produce `.blend` and `.fbx` if your Unity workflow prefers FBX.
3. Open the file in Unity, drop in the player rig, and wire the two
   triggers (Door 1, Door 2) plus the five MVP barriers.
4. Walk the tour route in `TOUR_SCRIPT.md` once before presenting.
