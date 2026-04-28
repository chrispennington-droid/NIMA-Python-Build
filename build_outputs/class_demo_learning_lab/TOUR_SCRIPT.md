# NIMA Phase II Spatial Review Learning Lab - Class Tour Script

## Framing (read aloud)

My implementation is a spatial-review learning lab for NIMA Phase II.
Learners spawn in the entry/lobby zone, then move into the Prove-Out
Facility to study equipment fit, loading access, workflow, scale, and
overlook-based observation. The prototype intentionally blocks unresolved
areas rather than pretending the full building is complete.

This is a **separate class/demo build**, not the formal RC1 partial MVP
package. The formal package remains conservative on purpose; this one is
walkable on purpose.

## Tour route

### 1. Spawn in Entry / Lobby
Player spawns at `PLAYER_SPAWN` (lobby, 5.5 ft eye height, facing the
Prove-Out Facility). The translucent storefront is to your back.

### 2. Read the title and learning objectives
Walk to `Board_Title` and `Board_Entry`. Read:

- **NIMA Phase II Spatial Review Learning Lab.** A simplified class
  prototype for learning spatial review, equipment fit, workflow, and
  QA-gated model development.
- **Learning Experience.** This prototype focuses on the entry sequence,
  controlled access, Prove-Out Facility, equipment fit, loading access,
  and overlook-based observation.

### 3. NIMA + Emerging R+D Park context
Move along the west lobby wall to `Board_NIMA` and `Board_RDPark`:

- **What Does NIMA Do?** NIMA develops technologies, applications,
  partnerships, facilities, and a highly-qualified workforce for emerging
  materials. This learning lab focuses on how a Prove-Out Facility
  supports prototyping, testing, and applied research.
- **Emerging R+D Park Context.** The Prove-Out Facility is part of a
  larger innovation ecosystem with Tyler Research Center, NIMA, Emerging
  Technologies, and the KBI/PSU site.

### 4. Phase II expansion + MVP boundary
Cross to `Board_PhaseII` on the east lobby wall:

- **Phase II Expansion.** The expansion adds approximately 24,230 square
  feet and supports future research, testing, prototyping, and workforce
  development.

Point out the red MVP boundary signage. Explain: blocked areas are
unresolved geometry that is deliberately excluded from this learning
build.

### 5. Enter the Prove-Out Facility through Door 1 (Level 1)
Walk to the green Level 1 door (`Door_Lobby_To_ProveOut_Level1`, 6 ft x
8 ft, centered at x=0). Walk through the trigger (or press **E** if the
door is configured to require key press). Step onto the cement floor of
the Prove-Out Facility.

### 6. Read the Prove-Out Facility purpose board
At `Board_ProveOut` (west wall, 6 ft up):

- **Purpose of the Prove-Out Facility (high-bay volume).** The Prove-Out
  Facility is the large high-bay space where equipment layout, clearances,
  workflow, and loading access can be evaluated before final build-out.

### 7. Walk the equipment-fit review
Move north along the west side of the floor and call out each placeholder:

- `Large_Test_Rig`     ~ 18 ft x 10 ft x 9 ft
- `CNC_Machine_Cell`   ~ 14 ft x 8 ft x 7 ft
- `Assembly_Table`     ~ 16 ft x 5 ft x 3 ft
- `Robot_Work_Cell`    ~ 12 ft x 12 ft x 8 ft

Read `Board_EquipFit`:

- **Equipment-Fit Review.** Learners inspect whether test rigs, machine
  cells, assembly tables, robot work cells, and forklift paths fit safely
  within the Prove-Out Facility.

Step over the yellow `Forklift_Clearance_Path` strip on the east side.
Note: 8 ft wide, runs longitudinally along the facility (>= 42 ft long
clearance per brief).

### 8. Discuss covered loading and overhead doors
Walk to the north wall. Three sectional doors are labeled
`OH_Door_W`, `OH_Door_C`, `OH_Door_E`, each 12 ft wide x 14 ft high.
Explain: this is the **Covered Loading / Service Access** edge. The
overhead doors are visual only in this demo.

### 9. Return south, take the stairs to Level 2
Walk back through Door 1, turn east in the lobby. Climb the stair (24
risers at ~7 in, 12 in tread) to the landing at z=14 ft.

### 10. Enter the Prove-Out Facility Overlook through Door 2
Walk through `Door_Level2_To_ProveOut_Overlook` (6 ft x 8 ft) onto the
overlook deck (24 ft wide x 10 ft deep, refined lobby/connector finish
with a warm accent band).

### 11. Observe equipment layout from above
Stop at the north guardrail (4 ft tall). Read `Board_Overlook`:

- **Prove-Out Facility Overlook.** The overlook lets stakeholders observe
  the Prove-Out Facility from above and review workflow, safety, and
  equipment relationships without entering the active production floor.

Spend a beat here looking down at the equipment fit and the forklift
clearance path. This is the strongest moment of the tour.

### 12. QA boundary callout (optional, from overlook)
Point at `MVP_Barrier_TylerSeal` along the west wall and the perimeter
barriers. Read `Board_QA`:

- **QA Boundary.** This prototype intentionally blocks unresolved areas
  instead of presenting unverified geometry as complete. The goal is to
  support spatial learning, not final construction documentation.

### 13. Final reflection
Return to the lobby (down the stairs, or skip directly if presenting
desktop). Visit `Board_Reflection`:

- **Main Takeaways.** Spatial VR helps learners understand scale,
  equipment fit, workflow, and design review. The process also showed why
  generated geometry needs QA before being used as an immersive
  walkthrough.

End the tour.

## Estimated runtime

- Concise demo: 6 - 8 minutes.
- Class walk-through with discussion: 18 - 25 minutes.

## Backup if a learner wanders outside the MVP

If a learner walks into a red MVP barrier, `TurnBackBoundary.cs` returns
them to the safe return point. The on-screen message is:

> This area is outside the current MVP review boundary.

Use that as a teaching moment for the QA boundary discussion.
