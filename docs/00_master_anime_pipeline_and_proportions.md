---
doc_id: master-anime-pipeline-and-proportions
title: Master 3D Anime Character Pipeline, Proportions & Blender 5.x Reference
topic: architecture-proportions
kind: architecture-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: beginner-to-advanced
tags: pipeline, proportions, anime-anatomy, head-ratio, reference-sheet, scale, view-transform, standard, blender-5x, api-changes, guilty-gear, genshin, vrm
sources:
  - Noggi — EVERYTHING About Creating Beautiful 3D Anime (xZWxEoa-Dwk)
  - SunnyIsOnline ft. Dillongoo — How to (Actually) Make Anime in 3D (4LhvcINgNxU)
  - CoderNunk — Complete 3D Game Character Creation Guide (codernunk.com)
  - Summer / Natsumori Katsu — CGWORLD Blender Fes (Sy7RHtco43Y)
  - Crashsune Academy — 4h Low Poly Anime Character Series (EQHdi5rX5fs)
  - VRM 1.0 Specification (vrm-c/vrm-specification)
---

# Master 3D Anime Character Pipeline, Proportions & Blender 5.x Reference

AI agents frequently fail at 3D anime character creation because they apply generic photorealistic PBR defaults (`AgX` color transform, 50% eye vertical placement, raw auto-calculated face normals, smooth 60fps spline curves, unapplied modifiers before Shape Keys, or deprecated Blender 3.x/4.x `bpy` APIs). Follow this battle-tested practitioner pipeline in strict stage order.

## 1. The Correct 10-Stage Production Order (Do Not Scramble)

1. **Style Target & Reference Sheet**: Choose style tier (see Section 2), align orthographic Front (`Numpad 1`) and Side (`Numpad 3`) images to a real-height reference cube (`1 BU = 1 m`, feet at `Z = 0`, facing `-Y`), placed in a dedicated `00_Reference` collection.
2. **Base Head & Body Topology**: Model or sculpt+retopo clean deformation-ready topology in resting neutral expression and `T-Pose` or `A-Pose` (`Apply All Transforms` `Ctrl+A` continuously).
3. **Anime Eyes, Lashes, Brows & Mouth Bag**: Build separate/detachable brow, upper/lower lash strips, light-gray sclera, eye-socket shadow plane, concave/convex iris, and inner mouth box + teeth/tongue.
4. **Hair Base Cap & Curve Strands**: Duplicate scalp hair-net cap -> author layered Bezier/NURBS curves (`Resolution U = 3–4`) -> convert to clean mesh -> merge tip vertices -> verify blue Face Orientation.
5. **Clothing, Accessories & Occluded Body Cleanup**: Extract/model outfits -> drape/solidify -> delete or mask hidden body faces (keep 1 loop inside cuffs/collars/hems).
6. **UV Unwrap & Hand-Painted / Square Textures**: Unwrap with hidden seams (`Face` at ~`2x` body texel density), or use Guilty Gear Square UVs; paint with `Ucupaint` / Krita.
7. **NPR Cel Shader, Custom Face Normals & Outlines**: Switch `View Transform = Standard`, set up EEVEE Toon Shader, fix face shadows (Ellipsoid `Data Transfer` or SDF Face Shadow Map), add Inverted Hull `Solidify` with vertex-weight masking (`0` inside mouth/eyes).
8. **Armature, Secondary Bones & Weight Painting**: Fit `Human Meta-Rig` (delete 100+ realistic face bones unless film), `Generate Rig`, add hair/skirt/ribbon chains on `DEF`, bind, fix head/neck/skirt/rigid-prop weights, normalize & limit to `4` influences.
9. **Facial Shape Keys (Post-Modifier Lock!)**: Apply structural modifiers (`Mirror`, `Subdivision`) FIRST (`SKkeeper` or `modifier_apply_as_shapekey` if needed), keep `Basis` untouched, sculpt VRM/ARKit/viseme & anime expression keys.
10. **2D-Style Animation & Engine Export**: Animate at `24 FPS` with Motion Blur OFF, NLA `Stepped Interpolation` (`Step = 2`) + `1s` smear frames, bake `RIG` -> `GAME_RIG`, export `FBX` / `GLB` / `VRM`.

> **Critical Rule**: Never add Shape Keys before finalizing mesh topology or applying structural modifiers (`Mirror`, `Subdivision`, `Solidify` if baked). Changing vertex counts invalidates every Shape Key delta. Never edit mesh vertices in Edit Mode after hand-editing `Custom Normals` without saving a `Face_Normals` Vertex Group to reapply them.

---

## 2. Choosing Your Anime Style Tier First

As SunnyIsOnline (`4LhvcINgNxU`) and Junya Motomura (`yhGjCzxJV3E`) emphasize, mixing incompatible anime pipelines causes chaos. Pick ONE tier before modeling:

| Tier | Representative Look | Face Shading & Topology | Texturing & Outlines | Animation Style |
|---|---|---|---|---|
| **Tier A: 2D-Exact Cel (ArcSys / Guilty Gear)** | *Guilty Gear Xrd/Strive*, *DBFZ* | Triangle radial mouth fan for huge expressions; handcrafted split vertex normals (`Copy/Paste Vectors` / `Abnormal`) | Square UVs for razor-sharp inner lines; RGBA vertex colors (`R` shadow bias, `B` hull depth, `A` hull width); Inverted Hull + Tangent 2nd normals | Stepped `1s`/`2s` limited animation (`Constant` / NLA step), zero physics sim, per-frame camera-facing mesh/bone distortion & scale |
| **Tier B: Action RPG Anime (Hoyoverse / Kuro)** | *Genshin Impact*, *Honkai Star Rail*, *WuWa*, *ZZZ* | Standard clean quad face loops + diamond mouth loop; **SDF Face Shadow Map** (`7`-step grayscale mask) so 360° camera lights never snap | Hand-painted 2K–4K albedo + **ILM** channel map (`R` spec intensity, `G` AO shadow bias, `B` spec size, `A` inner lines) + 2-tone shadow ramp + Inverted Hull | Smooth game cycles (`24–30 fps` -> engine `60 fps`), `SpringBone` / cloth physics on hair & skirts |
| **Tier C: VTuber / VRM / Indie Stylized** | VRChat, VRM 1.0, Indie RPGs | Clean quad loops + `Data Transfer` Ellipsoid normal smoothing (no raw nose shadows); ARKit 52 / VRM 15 viseme Shape Keys | Clean `Ucupaint` / `MToon` lit+shade color textures (`Standard` view transform); `1–2` materials for mobile/VRChat perf | `T-Pose` (`+Z` or `-Y` forward converted) + `VRM SpringBone` chains + BlendShapeProxy expressions |
| **Tier D: Chibi / Low-Poly Stylized** | *Love-chan*, Nendoroid, mobile | Minimal clean edge loops (`3–8k` tris total), simplified eye sockets or texture-swapped 2D eyes | Crisp color palette squares or simple flat UV hand-paint; simple `Solidify` outline | Snappy `2s` or playful smooth cycles |

---

## 3. Anime Proportions & Anatomy Reference Numbers

Photorealistic human proportions (`8` heads, deep eye sockets, wide jaw, prominent nose bridge, thick wrists) immediately create "uncanny 3D doll" results if applied to anime characters.

| Measurement | Realistic Human | Standard Anime (Teen / Bishoujo) | Tall Shounen / Seinen | Chibi / Super-Deformed |
|---|---|---|---|---|
| **Total Height (in Blender)** | `1.70–1.80 m` | `1.50–1.65 m` (`1.30 m` petite like Natsumori Katsu's demo) | `1.70–1.85 m` | `0.85–1.20 m` |
| **Head-to-Body Ratio** | `7.5–8.0` heads | `5.5–6.5` heads | `6.5–7.5` heads | `2.0–3.0` heads |
| **Eye Vertical Position (Chin = 0%, Crown = 100%)** | `~50%` (midpoint of skull) | `~35–42%` (eyes sit LOWER, forehead/cranium proportionally larger!) | `~42–46%` | `~30–35%` |
| **Eye Spacing** | `1.0` eye width | `1.0–1.25` eye widths (`2AM`: slightly > 1 eye width for cuteness) | `~1.0` eye width | `1.2–1.5` eye widths |
| **Nose & Jaw Profile** | Prominent nasal bone, square jaw | Soft forehead curve, small upturned nose (`<10–15%` head depth), V-chin, **lips never pass nose-to-chin line** (`2AM`) | Sharper bridge, defined jawline, still flatter cheeks | Tiny triangle dot nose, soft round cheek silhouette |
| **Cheek / Frontal Plane** | Rounded zygomatic arch + nasolabial fold | **Nearly flat front plane** from mouth to cheeks (`Shonzo`), two clean curves from chin to side & back | Slight cheekbone plane break | Very round/flat cheek |
| **Leg Length (% Total Height)** | `~48–50%` | `~50–55%` (elongated thighs/calves in stylized heroines) | `~50–52%` | `~30–35%` |
| **Wrists / Ankles / Neck** | Proportional bone thickness | Slender neck (`0.35–0.45x` head width), tapered wrists/ankles (`~50–60%` narrower than realism) | Broad clavicles/shoulders (`~2.0–2.3x` head width), narrow waist | Stubby tapered limbs |

---

## 4. Blender Scene, Scale, Reference & Color Management Setup

1. **Units & World Orientation**:
   - Keep `Unit Scale = 1.0` (Metric, `1 unit = 1 meter`).
   - Character stands with **feet soles at `Z = 0`**, **centered on `X = 0`**, **facing `-Y`** (Front Ortho = `Numpad 1`).
2. **Exact Reference Sheet Alignment (CoderNunk & Chaosy3D)**:
   - Create a temporary measuring Cube (`2 m` default -> move `+1 m` on Z in Edit Mode so origin sits at bottom -> `Dimensions.Z = 1.60 m` or target character height).
   - Switch to `Numpad 1` (Front) and drag in Front model sheet -> set Image Data `Offset Y` so feet touch `Z = 0` -> scale to match cube height -> repeat in `Numpad 3` (Right Side).
   - **Rule**: Draw horizontal guide lines across your Front and Side sheets before importing (crown, brow, eye, nose tip, chin, shoulder, bust, waist, crotch, knee, ankle) so proportions match 1:1. Do NOT draw a foreshortened arm on the side sheet!
   - Put references in `00_Reference` collection, lower `Opacity` to `0.35–0.50`, disable selectable icon in Outliner.
3. **Color Management for Anime (CRITICAL)**:
   - Open `Render Properties -> Color Management` and switch `View Transform` from `AgX` / `Filmic` to **`Standard`** (`Look = None`)!
   - Why: `AgX` and `Filmic` apply S-curve highlight compression and desaturation designed for photorealistic HDR lighting—turning crisp anime pastel skin tones and saturated shadow ramps muddy and washed out.
4. **Collection Architecture**:
   - `00_Reference` (model sheets, normal transfer guide spheres — render disabled)
   - `01_Character_Base` (`SK_Body`, `SK_Head`, `SK_Eyes`, `SK_Hair`, `SK_Outfit_*`)
   - `02_Rig` (`META_Character`, `RIG_Character`, `GAME_RIG_Character`)
   - `03_Lighting_Outlines` (`NPR_KeyLight`, `GP_LineArt`, cameras)

---

## 5. Blender 2.8/3.x/4.x -> Blender 5.2/5.3 Compatibility Matrix

Most popular YouTube anime tutorials (`Daniel Kreuter`, `Lightning Boy`, `2AM`, `Royal Skies`, `Dikko`) were recorded in Blender 2.8–4.2. Translate these UI/Python differences when executing in **Blender 5.2 LTS / 5.3**:

| Legacy Tutorial Instruction (2.8–4.3) | Blender 5.2 / 5.3 Reality & `bpy` Fix |
|---|---|
| `Object Data -> Normals -> Auto Smooth` checkbox (`mesh.use_auto_smooth`) | **Removed in 4.1+ / 5.x.** Custom normals work natively without toggling Auto Smooth! For sharp angle shading, use `bpy.ops.object.shade_smooth_by_angle(angle=...)` or add the **`Smooth by Angle`** Geometry Nodes modifier, or mark edges `Sharp`. |
| Rigify **Bone Layers** (32 dot grid squares) | **Replaced in 4.0+ by Bone Collections** (`arm.collections["DEF"].is_solo = True`, `bcoll.assign(bone)`). |
| `action.fcurves` in Python animation scripts | **Removed in 5.0!** Blender 5.x uses **Slotted Actions + Channelbags**: `cb = bpy_extras.anim_utils.action_ensure_channelbag_for_slot(act, slot)`, then `cb.fcurves.ensure(data_path, index=i)`. (`pb.keyframe_insert(...)` still handles slot/channelbag creation automatically.) |
| `ShaderNodeMixRGB` in shader tutorials | **Deprecated/removed in favor of `ShaderNodeMix`** (`node.data_type = "RGBA"`, inputs `Factor`, `A`, `B` via socket indices or type-safe lookup, output `Result`). |
| `BLENDER_EEVEE_NEXT` in 4.2–4.4 scripts | Renamed back to **`BLENDER_EEVEE`** in Blender 5.0+. |
| `material.use_nodes = True` | Deprecated in 5.x (new materials already initialize with node trees). |
| `Boolean` solver `'FAST'` | Renamed to **`'FLOAT'`** in 5.0 (`'EXACT'` and `'MANIFOLD'` remain). |
| `GreasePencilv3` / `bpy.data.grease_pencils_v3` | Gone in 5.0 — unified back under **`bpy.data.grease_pencils`** (`stroke.points[i].position`, `.radius`). |
| `bone.select` in Edit/Pose Mode scripts | Gone in 5.0 — use **`edit_bone.select`** or **`pose_bone.select`**. |
| `SKkeeper` addon for applying modifiers on Shape-Key meshes | Still useful for batch multi-modifier apply, or use native `bpy.ops.object.modifier_apply_as_shapekey()` for deform modifiers; apply Subdivision/Mirror BEFORE sculpting expressions whenever possible. |
