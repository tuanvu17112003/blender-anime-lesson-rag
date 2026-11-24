---
doc_id: anime-facial-shapekeys-and-animation
title: Anime Facial Shape Keys, Lip-Sync, Limited Animation, Smear Frames, and Blender 5.x Action Export
topic: facial-shapekeys-and-animation
kind: practitioner-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate-advanced
tags: shape-keys, vrm, arkit, visemes, lipsync, blink, blend-from-shape, limited-animation, stepped-interpolation, nla, smear-frames, lattice, slotted-actions, channelbag, fbx, glb
sources:
  - 2am_blinking_lipsync_export (Qyrz4JoMP28)
  - asw_guilty_gear_xrd_gdc_art_style (yhGjCzxJV3E) & asw_guilty_gear_toonline_eng.md
  - noggi_everything_beautiful_3d_anime (xZWxEoa-Dwk) & guilty_gear_3d_look_2d_study
  - natsumori_katsu_modeling_rigify_unity_vrchat (Sy7RHtco43Y)
  - animationreference_3d_smear_frames.md
  - VRM_Specification/specification/VRMC_vrm-1.0/expressions.md
  - docs.blender.org_manual_en_latest_animation_actions.html.md
  - Blender 5.3 Skills: blender-facial-shapekeys, blender-animation, blender-export-pipelines
---

# Anime Facial Shape Keys, Lip-Sync, Limited Animation, Smear Frames, and Blender 5.x Action Export

Most novice 3D anime fails the moment the character blinks or moves: smooth 24fps Bezier interpolation looks weightless and "doll-like", real Motion Blur smudges cel edges, Shape Keys explode when created *before* applying Mirror/Subsurf, and outdated Blender `action.fcurves` scripts crash immediately in Blender 5.x.

---

## 1. Sacred Shape Key Modeling & Topology Lock Rules

1. **Neutral `Basis` Key Rule**:
   - The `Basis` shape key must be a **calm, neutral, dead-pan expression** with **eyelids wide open** and **lips lightly closed** (`0%` smile, `0%` blink, `0%` mouth open). If `Basis` already smiles, adding `mouthOpen` or `blink` compounds weirdly and shrinks face geometry when combined!
2. **Apply Topology Modifiers BEFORE Authoring Any Shape Key**:
   - Once you add the first Shape Key (`Basis`), Blender **locks vertex count/order** and refuses to apply **`Mirror`**, **`Subdivision Surface`**, or **`Solidify`** (`Modifier cannot be applied to a mesh with shape keys`).
   - Fix if discovered late: use a multi-modifier apply helper (duplicating mesh, mutating one key per duplicate via `SKkeeper` / `join_shapes`, or Blender 5.3 `scripts/apply_with_shapekeys`) **or apply Mirror/Subdiv BEFORE sculpting the very first Shape Key** (`Solidify` for outlines stays live if `Even/Flip` is preserved and exported separately, or baked last on non-shapekey props).
3. **Never Leave Stray Vertices Unmoved or Clipped Through Eyes/Eyelashes**:
   - While shaping `blink` / `eyeBlinkLeft` / `eyeBlinkRight`: verify **from 3/4 side view** that the upper eyelid sweeps forward *in front of* the curved cornea—never dragging straight linearly through the eyeball!
   - Keep **Eyelashes + Upper Eyelid Skin** combined or synced inside the same Shape Key / driver so lashes ride flush with the closing lid instead of floating mid-air (`2AM`).
4. **Preventing Double-Translation (`Muzzle / Cheek` Split Trick)**:
   - Model symmetric expressions once (e.g., `Blink_Both`), then split cleanly into `blinkLeft` and `blinkRight` without re-sculpting:
     1. Create `blinkLeft` from `Basis` (value `1.0`), select vertices only on `+X` (`Mirror` or Lasso), run **Vertex → `Blend From Shape`** targeting `Blink_Both` (Blend `1.0`, `Add = False`), then repeat on `-X` into `blinkRight` with a clean center bridge weight fade (`0.5 -> 0.0` at center seam `X = 0` so neither side double-moves the bridge!).
5. **Re-apply / Preserve Custom Face Normals on Shape Keys (`Animexd`)**:
   - Ensure face custom split normals (or `Data Transfer` target) aren't scrambled when upper eyelids tuck down; avoid `Edit Mode -> Recalculate Normals` after custom normal editing!

---

## 2. Standard Anime / Game Blendshape Lists (VRM 1.0, VRChat, ARKit 52)

Choose the minimum clean set needed by your target runtime (don't ship 52 sculpts if VRM 15 is enough—and vice-versa for Live Link iPhone mocap!):

### VRM 1.0 Core Preset Names (`VRMC_vrm-1.0` Spec — *Mandatory Exact Case!*)
Notice **VRM 1.0 renamed VRM 0.x keys** (`Joy`/`Sorrow`/`Fun`/`A`/`I`/`U`/`E`/`O`) to **camelCase** standard presets:
- **Visemes (Lip-Sync 5)**: `aa`, `ih`, `uu`, `ee`, `oh` (note: animate mouth corner pull + lower jaw teeth/tongue drop together!).
- **Blink & Gaze**: `blink`, `blinkLeft`, `blinkRight` (optionally `lookUp`, `lookDown`, `lookLeft`, `lookRight` if shader UV offset / texture-scrolling eyes).
- **Emotions (6)**: `happy`, `angry`, `sad`, `relaxed`, `surprised`, `neutral`.
- *VRChat Avatar (`Oculus 15 Visemes`)*: Adds `vrc.v_sil`, `vrc.v_pp`, `vrc.v_ff`, `vrc.v_th`, `vrc.v_dd`, `vrc.v_kk`, `vrc.v_ch`, `vrc.v_ss`, `vrc.v_nn`, `vrc.v_rr`, `vrc.v_aa`, `vrc.v_e`, `vrc.v_ih`, `vrc.v_oh`, `vrc.v_ou` (you can mix clean bases + subtle `pp/ff/ss` lip pursing).
- *iPhone / Live2D-tier Mocap (`ARKit 52`)*: Required for full VTuber face tracking (`eyeBlinkLeft`, `eyeSquintLeft`, `jawOpen`, `mouthSmileLeft`, `cheekPuff`, `tongueOut`, etc.). Keep mutually interfering keys zeroed in rest and verify Left/Right symmetry before export.

### Quick Eyebrow & 2D Expressive Anime Cheats (`2AM` / `Katsu` / Stylized VFX)
- Beyond realistic anatomy, add dedicated **2D anime expression keys** (or toggleable bone/scale cards):
  - `Face_Blush` (slides internal textured blush card forward `2mm` in front of cheek skin + alpha `1`, or drives shader param via bone/UV!).
  - `Eye_Star / Heart / Spiral` (swappable UV iris offset or hidden eye-card toggle).
  - `Sweatdrop / VeinPop / GloomLines` (parented to `Head`, scaled from `0.001 -> 1.0` over **1 frame** on stepped keyframes).
  - Keep **eyebrows floating 1–2 mm in front** (or shrinkwrapped just ahead) of bangs when stylized **manga/anime eyebrow visibility through hair** is desired (`Override Material / Stencil / Physical Front Offset`).

---

## 3. Authentic 2D Anime Motion: Limited Animation (`On 2s / 3s`), Not Floaty CG

Why raw 3D keyframe interpolation fails `Noggi`'s / `Guilty Gear`'s "2D Look Test":
1. **Strict Project Timing Settings (`Noggi`)**:
   - Timeline Frame Rate: **`24 fps`** (never 30 or 60 for anime film style).
   - **Motion Blur = `OFF`** in EEVEE/Render Properties (anime uses crisp holds and hand-crafted smear silhouettes instead of camera shutter blur).
2. **Animate Pose-to-Pose in **`Stepped`** (`Constant` / NLA `Stepped Interpolation`), Not Smooth Auto-Splines**:
   - First pose strong storytelling keyframes (`Contact`, `Breakdown`, `Anticipation`, `Extreme`, `Settle`).
   - **Guilty Gear / ASW Rule**: **Delete/skip intermediate frames cleanly across fast attacks & swings** (`frame N` crouch -> **instant snap** `frame N+2` full slash apex -> `hold` `frame N+3, N+4`!). Smooth computer tweens through mid-swing steal impact weight!
   - **Variable Frame Rates Inside a Single Shot (`Noggi`)**: Hero character dialogue lip-sync runs on `2s` (or `1s` for fast lip pops), camera pans/background clouds stay smooth (`1s`) or deliberately held on `3s/4s`, while uninvolved background characters stay **completely still** (`hold`).
   - **Non-Destructive `Stepped Interpolation` Modifier (Blender 5.x F-Curve Modifier / NLA)**:
     - Do *not* permanently bake-destroy your clean spline keyframes mid-WIP if you still need to tweak arcs! Apply a **`Stepped Interpolation`** F-curve modifier (`Step Size = 2` for 2s, `3` for 3s) or NLA **`Stepped`** override *while sculpting timing*, **AND** manually refine awkward breakdown frames on `1s` where `2s` skips an ugly tangency!
3. **4-Limb Readability & "Camera View Is King" Cheats**:
   - Keep **arms and legs visibly separated** in the camera silhouette (never overlap elbow silhouette cleanly onto ribcage torso silhouette when a slight outward elbow push reads crisp in 2D).
   - Actively **scale/squash head cheeks toward camera**, shift eyes slightly closer together on `3/4` heroic glares (`Katsu`/`Guilty Gear` camera-plane foreshortening), and cheat limb scale during kicks/punches (`Oversized foreground fist` on apex impact hold!).

---

## 4. 3D Anime Smear Frames & VFX Timing (`1s` / `2–3` Frames at 60fps)

From *Guilty Gear* & *Animation Reference* (`animationreference_3d_smear_frames.md`):
- **Duration**: A smear lasts only **1 frame at 24fps (`~41.7 ms`)**—or **2–3 frames at 60fps** in fighting games (`Guilty Gear Xrd`/`Strive`). You should **barely notice it cleanly paused**, yet feel snappy whip momentum at playback speed!
- **Never Bake Smears Into Permanent Rig Geometry**! Use three non-destructive methods:
  1. **Armature Stretch + `Lattice` Modifier (`VG` / Animated `Strength`)**:
     - Bind a temporary `Lattice` cage (`Influence = 0.0` outside the single smear frame, `1.0` only on frame `F` via **`Constant` keyframe**). Pull lattice control points backward along the motion arc to streak trailing sleeves, hair tips, and trailing limbs into sharp tapered motion lines.
  2. **Dedicated Multi-Limb / Dry-Brush `smear_geo` Mesh Swap (`1-frame` Visibility Pop)**:
     - Hide regular sword/arm on smear frame `F` (`scale = 0.001` or `Render Visibility = False` stepped) and pop on a custom arc-ribbon **`smear_geo`** blade slash / stretched 3-finger fan mesh with **Emission alpha streak gradient** (transparent back tail → sharp painted white/color tip)! Keep hidden scale (`0.001`) rather than Blender-only `hide_render` if exporting to game engines (Unreal/Unity).
  3. **Custom `Smear` Shape Keys on Hair/Limbs**:
     - Sculpt a crisp tapered smear fan on a Shape Key (`smear_slash_arc`), keyframe `0 -> 1 -> 0` with `Constant` interpolation across frame `F-1 -> F -> F+1`.

---

## 5. Blender 5.2+ Animation API (`Slotted Actions` & `Channelbags`), IK/FK & Engine Export

### Critical Blender 5.x Action / F-Curve API Update (`blender-animation` + 5.3 Manual)
Blender 4.4 introduced **Slotted Actions**, and **Blender 5.0+ removed legacy `action.fcurves` completely!** Any AI script doing `action.fcurves.new(...)` or `for fc in action.fcurves:` **crashes with `AttributeError` in Blender 5.2 LTS**.
Use the official Blender 5.x `Channelbag` pattern:
```python
from bpy_extras import anim_utils

# Ensure action + slot on armature or object
if not obj.animation_data:
    obj.animation_data_create()
act = obj.animation_data.action or bpy.data.actions.new("Run")
obj.animation_data.action = act
slot = obj.animation_data.action_slot or act.slots.new(obj.id_type, obj.name)
obj.animation_data.action_slot = slot

# Access F-curves via the Channelbag (replaces old action.fcurves!)
cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
fcurve = cb.fcurves.ensure("rotation_quaternion", index=0)
# Never pass keyframe_points.add()/insert inside loop -> always call .update() or keyframe_insert()
```
- **Multi-Target Scene Sync**: One Slotted Action (`anim_SceneCut01`) can now store coordinated slots for `HeroRig`, `ShapeKeys` (`Mesh.key`), and `KeyLight` cleanly in a single Action!
- **Quaternions on Game Skeletons**: Set Limb/Spine rotation modes cleanly (`QUATERNION`) before final export baking so Unreal/Unity/glTF never trigger gimbal-lock flip artifacts between keyframes. Verify seamless loops cleanly (`frame_start == frame_end` pose values identical; run `Set Extrapolation = Make Cyclic` only temporarily or clean matching boundary keys before baking!).

### Clean Control Rig (`RIG`) → Game Export (`FBX` / `GLB` / `VRM`) Pipeline
1. Never export `CTRL-*`, `MCH-*`, or `ORG-*` Rigify helper bones into a game engine!
2. Before final engine export:
   - **Pose Mode (`Bake Action`)** with **`Only Selected Bones`** (`DEF` collection soloed), **`Visual Keying = ON`**, **`Clear Constraints = OFF`** on source scene (or bake onto duplicate clean export armature with **`Clear Constraints = ON`** so custom IK curves turn into exact pure FK bone transforms!).
   - **`Apply Modifiers` Warning**: Do **not** check Blender FBX's generic `Apply Modifiers` if your character has **Shape Keys**, because applying modifiers while Shape Keys exist causes Blender FBX exporter to **silently skip ALL Shape Keys**! Keep modifiers above Shape Keys already applied beforehand, leave **only `Armature`** live, and uncheck `Apply Modifiers` during FBX export!
   - Check **`Only Deform Bones`** (`use_deform_only=True`) and disable **Add Leaf Bones** (`add_leaf_bones=False`) in FBX unless targeting a specialized SpringBone tip requirement.
   - Verify exact coordinate orientation & scale:
     - **Unity `.fbx`**: `Apply Scalings = FBX All` (or `Apply Unit` + `-Z Forward / +Y Up` matching Unity), re-test humanoid bone green-mapping + `A`/`Blink` blendshapes inside Unity inspector.
     - **Godot / Web / VRM `.glb` / `.vrm`**: `+Y Up`, `+Z Front` in glTF spec (Blender glTF exporter converts Blender `-Y Front / +Z Up` automatically when `+Y Up` is checked); use **VRM Add-on for Blender (`2.20+` / Blender 4.2–5.x compatible)** to bind `MToon` materials, `VRM 1.0 Humanoid`, `Expressions`, and `SpringBone` colliders cleanly.
