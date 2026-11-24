---
doc_id: ai-agent-anime-3d-pitfalls-and-qa-checklist
title: AI Agent Anti-Patterns, Bug Matrix & Pre-Delivery QA Gate for 3D Anime Characters
topic: troubleshooting-qa
kind: pitfall-catalog
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: all
tags: pitfalls, anti-patterns, qa, checklist, troubleshooting, normals, topology, rigging, weight-painting, solidify, shape-keys, blender-5, api-changes, vrm, export
sources:
  - Synthesized across curated guides 00-08
  - Blender 5.3 Skills: blender-asset-qa, blender-core, blender-stylized-npr, blender-character-rigging, blender-animation, blender-export-pipelines
  - Verified practitioner post-mortems: 2AM, Noggi, Arc System Works, Natsumori Katsu, Shonzo, Chaosy3D, Dikko, GabrielToonShader
---

# AI Agent Anti-Patterns, Bug Matrix & Pre-Delivery QA Gate for 3D Anime Characters

AI agents generating or editing 3D anime assets in Blender tend to hallucinate photorealistic anatomy, ignore color management, skip custom normals, break Rigify joints, lock Shape Keys before applying modifiers, or write removed Blender 4.x Python APIs. Every bug below maps a recognizable symptom directly to its root cause and veteran fix.

---

## 1. Proportions, Facial Topology & Modeling Pitfalls

| # | Bug / Symptom | Root Cause | Exact Veteran Fix |
|---|---|---|---|
| 1 | Face looks western, overly realistic, or uncannily stiff ("Uncanny Valley 3D doll") | Modeling eyes at ~50% head height, protruding nasal bridge, deep philtrum, puffy round cheeks, and rounded full-scale head silhouette | Set **eye center at 38%–45% head height** (measured from chin), shorten chin-to-nose distance (`Shonzo`/`2AM`), flatten side cheek shadow profile into 3–4 clean stylized planes, and keep tiny sharp anime nose bridge |
| 2 | Character cannot close eyelids cleanly or blinks pinch jagged triangles ("Zipper eyelid") | Used **`Quadriflow` remesh** on hero head or unmatched upper/lower vertex spans around orbital loops | Never Quadriflow hero faces; retopologize manually with concentric eye rings containing **equal quad counts on upper and lower eyelids** (`6–8` spans top = `6–8` spans bottom) (`Dikko`/`Maoly`) |
| 3 | Nose tip shows ugly center triangle shading crease or sharp mirror seam | Unmerged centerline vertices or `3/5`-edge star pole placed directly on the `X = 0` symmetry spine | Enable `Mirror` **`Clipping = ON`**, keep `X = 0` as a continuous clean edge loop (`No star poles on centerline`), and run `Merge by Distance` (`0.0001 m`) after applying Mirror |
| 4 | Eyeballs pop out of the side of the eye socket in 3/4 view | Built spherical marble eyeballs pushed too far forward inside flat anime face sockets | Flatten cornea sphere along local `Y` into an oval **anime cornea dish/saucer** recessed inside tilted upper/lower eyelid rims, or use flat tracked UV Iris planes inside curved socket (`2AM`) |
| 5 | Body height/limbs look compressed or awkward like an infant | Wrong anime head-count proportion or straight `180°` column legs (`no thigh/calf offset`) | Target **6.5–7.5 heads tall** (classic teenage anime), **5.5–6** chibi-stylized; build gentle S-curve profile (`knee slightly forward`, `calf rearward`, ankle subtly tucked) and keep collar/torso/leg proportions anchored to orthographic `Settei` sheets |
| 6 | Elbows/knees collapse or lose half their volume on bends (`Candy-wrapper` / pinch) | Only 1 edge loop at elbow/knee/knuckle or spiral diagonal edge flow around joints | Model **at least 3 parallel edge loops** at every bending joint (`elbow`, `knee`, `wrist`, `finger knuckles`, `ankle`), spacing outer support loops slightly wider than inner crease loops |

## 2. Hair, Clothing & Geometry Integrity Pitfalls

| # | Bug / Symptom | Root Cause | Exact Veteran Fix |
|---|---|---|---|
| 7 | Hair freezes viewport / hits `150k+` tris and kills game engines | Used Blender **Hair Curves / Particle Strand Groom** or left high `Subdivision` levels + `U=12` curve resolution unoptimized | Always build **Base Scalp Cap** (skin/hair dark root shield so scalp gaps never show) + **Beveled Curve Ribbons** converted to mesh at low resolution (`Curve Resolution U = 3–4`, beveled width tapered by Radius `Alt+S`, closed tip, keep body+hair game budget `15k–45k` tris) |
| 8 | Hair strands or collar insides appear invisible in Unity / Unreal / GLB | Single-sided flipped normals (shows **Red** in Viewport `Face Orientation`) triggering Engine Backface Culling | Turn on **Viewport Overlays -> `Face Orientation`** until **100% Blue** outside; run `Shift+N` (`Recalculate Outside`), or add thin capped inner shell thickness (`Solidify` applied cleanly) before export |
| 9 | Unmerged overlapping double faces or skirt hem flickers (`Z-fighting`) | Coplanar duplicated inner lining (`0 mm` offset) or unapplied zero-thickness overlapping `Solidify` shell | Keep lining/cloth shells separated by **`>= 2–3 mm` physical clearance**, weld open skirt/shirt edges (`Merge by Distance`), and delete hidden body skin faces only when outfit is non-swappable |
| 10 | Skirt or pleated collar explodes into spiky folded fans during subdivision | Zero-thickness cloth strips merged non-manifold (`3+` faces sharing 1 edge) before Subsurf | Separate pleated hems cleanly (`Y` split or inset margin), apply `Solidify` cleanly *after* major shape folds, and mark pleat knife edges crisp without creating T-junctions |

## 3. UVs, Textures & Material Pipeline Pitfalls

| # | Bug / Symptom | Root Cause | Exact Veteran Fix |
|---|---|---|---|
| 11 | Blurred pixelated iris, blush, or messy jagged collar trim stripes | Uniform texel density gave head tiny UV area and curved stripes painted diagonally across pixels | Scale **Face & Eyes UV islands `2×–3×`** higher than body; align collars, cuffs, eyebrows, and inner lines horizontally/vertically via **`Follow Active Quads` UV Vectorizing** along crisp pixel boundaries (`Facepalme` / `Guilty Gear`) |
| 12 | Cel shadow threshold bands shift weirdly or specular highlights look dull | `ILM`, `LightMap`, `SDF Face Mask`, or `Normal` map loaded with **`sRGB`** color space instead of **`Non-Color`** | Set Color Space = **`Non-Color`** on every data/mask texture (`ILM`, `SDF`, `Roughness`, `Metallic`, `Normal`, `AO`), leaving **`sRGB`** strictly on Base Color / Shadow Color / SSS / Emission |
| 13 | Game engine export (`Unity` / `Godot` / `VRChat` / `Roblox`) shows blank textures on back hair | Used **UDIM tiles (`1001`, `1002`)** in Blender `Ucupaint` and exported directly without repacking into `[0, 1]` | Repack / bake multi-tile UVs into standard **`[0, 1]` UV atlases** (`<= 4` materials total) before `.fbx`/`.glb`/`.vrm` export, or split Front Hair / Back Hair into separate materials referencing `0–1` space |
| 14 | Black NaN pixels or broken tangent-space lighting streaks appear in game engines | **Zero-area UV faces** (`collapsed single-point UV island`) or un-seamed **`> 60°` hard sharp edges** | Run UV integrity check for `zero_area_faces == 0`; mark UV seams along every sharp split edge (`> 60°`), and keep pack margins proportional (`8 px` for 2K, `16 px` for 4K) |
| 15 | Anime skin tones look desaturated gray and dull white whites | Default **`AgX`** or **`Filmic`** View Transform left active in Color Management | Switch **Render Properties -> Color Management -> `View Transform = Standard`** (`Look = None`) for vibrant 2D cel colors (`Noggi` / `ASW`) |
| 16 | World environment washes out all dark cel shadow contrast | Unclamped World sky lighting illuminates unlit shadow backsides evenly | Split World shader with **`Light Path -> Is Camera Ray`**: show backdrop only to Camera rays and feed pure **Black (`0, 0, 0`)** to indirect GI rays |

## 4. Cel Shading, Custom Face Normals, SDF & Outlines Pitfalls

| # | Bug / Symptom | Root Cause | Exact Veteran Fix |
|---|---|---|---|
| 17 | Ugly blotchy triangular shadow patches on anime nose, under-eyes, and upper lip | Raw 3D face geometry normals used directly in toon lighting calculation (`Dot(N, L)`) | Apply **Proxy Sphere/Ellipsoid `Data Transfer` Custom Normals** (`Nearest Face Interpolated`), edit tilted flat face vectors (`2AM`/`Abnormal`), OR bypass geometry normals entirely using a **7-map SDF Face Shadow Node Setup** |
| 18 | Face shadows "swim" or break when head turns in animation after Data Transfer | Unapplied `Data Transfer` modifier referencing a static unparented proxy sphere, OR live modifier placed below `Armature` | **Apply `Data Transfer`** onto resting face BEFORE bone deformation (split custom normals deform rigidly with head weights) OR parent the proxy target directly to `Head` bone (`DEF-spine.006`) |
| 19 | SDF face shadow snaps violently across 180° when character rotates full circles | Naive angle comparison `(-light_z + head_z) / pi` wraps past `[-pi, +pi]` cleanly without `atan2` modulo | Wrap relative yaw cleanly with **`atan2(sin(light_z - head_z), cos(light_z - head_z)) / pi`**, selecting left vs right mirrored `SDF` UV sample smoothly at `0` |
| 20 | White dashed holes / gaps along Inverted Hull `Solidify` outline edges | Unwelded `Sharp`/Mirror vertices or split custom normals extruding adjacent shell faces in opposite directions | Weld mesh vertices (`Merge by Distance`), use unified smoothed normals on an outline shell (never split sharp edges across hull extrusion), or paint ArcSys **`G` (`Close the gap`)** vertex weighting `0.0` at creases/valleys |
| 21 | Character turns completely pitch-black solid silhouette in **Cycles** with `Solidify` outline | `M_Outline` uses raw `Emission` without `Geometry -> Backfacing` + `Light Path -> Is Camera Ray` + **`Transparent Shadows`** | Wire `Emission` + `Transparent BSDF` via **`Geometry -> Backfacing`**, wrap with **`Light Path -> Is Camera Ray`** (`or Ray Length` for mirror reflections!), and enable **`Transparent Shadows`** (`Blender Secrets 5.2+`) |
| 22 | `Solidify` outlines poke black spikes inside nostrils, eyelashes, fingernails, and lips | Uniform thickness (`Vertex Group` unassigned) plus `Even Thickness` magnifying sharp narrow corners | Paint `VG_OutlineWidth = 0.0` around eyelids, nostrils, lips, and tight finger webs; tune `Clamp` on `Solidify`, and use ArcSys Alpha depth-push bias on bangs if outlines cut eyes |
| 23 | Artist expects Blender `Grease Pencil Line Art` outlines to show up in Unity / VRChat / VRM | Blender `Line Art` modifier is a Blender-only screen-space Grease Pencil generator and does **not** export to `.fbx`/`.glb`/`.vrm` | Use **Inverted Hull (`Solidify`) + Inner Albedo/ILM Lines** for real-time engine exports; keep Grease Pencil `Line Art` (`Screen Space`) strictly for Blender renders/video compositing |

## 5. Rigging, Weight Painting & Physics Pitfalls

| # | Bug / Symptom | Root Cause | Exact Veteran Fix |
|---|---|---|---|
| 24 | `Bone Heat Weighting: failed to find solution for one or more bones` | Multi-layer intersecting anime clothing, loose hair locks, zero-area verts, or unapplied Scale (`!= 1.0`) | Apply `Ctrl+A -> All Transforms` first (`Scale = 1,1,1`), run `Merge by Distance`, OR skin a watertight **`Voxel Remesh` Proxy** with Automatic Weights and transfer via **`Data Transfer -> Vertex Groups`** |
| 25 | `RIGIFY ERROR: Disconnected chain` or reversed IK knee/elbow bend flip | Detached head/tail endpoints when fitting Meta-Rig, off-center `spine` (`X != 0`), or `180°` collinear knee/elbow | Never detach connected parented Meta-Rig joints (`Natsumori Katsu`); lock center spine `X = 0`; bend knees slightly forward (`-Y`) and elbows slightly backward (`+Y`) before `Generate Rig` |
| 26 | Eyes, cheeks, jaw, or forehead squish rubbery when neck/spine bends | Automatic Weights bled `DEF-spine.004/005` (`neck`) or `shoulder` weights onto cranium, eyeballs, eyelashes, or face verts | Paint **`1.0` pure solid weight on `DEF-spine.006` (`Head`)** above the jaw hinge + eyeball/cornea/teeth/hair root meshes, and erase (`0.0`) all neck/chest weights from the face |
| 27 | Skirt splits vertically down the crotch or flies awkwardly forward when leg lifts | Transferred/auto weights left **`thigh.L` / `thigh.R`** weights attached to skirt hem vertices | Strip ALL `thigh` and `calf` vertex groups from skirt meshes; weight waist rigidly to `pelvis` (`DEF-spine`), use radial skirt bone chains, and start **`Wiggle` / `SpringBone` physics at Link 2–3** (`2AM` rule), not waist Link 1 |
| 28 | Blender crashes or paints weights onto control shapes (`CTRL-arm`) instead of rig bones | Attempted weight painting with `CTRL`/`MCH` Rigify collections visible instead of isolating `DEF` | In **Armature Data Properties -> Bone Collections**, solo ONLY **`DEF`** during weight painting; set **`Only Deform Bones`** on export |
| 29 | Skirt/twintails clip straight inside torso, thighs, or cheeks in Unity / Blender | Missing physics colliders on `Wiggle 2` / `VRM SpringBone` chains or missing tip tail leaf bone | Parent **Sphere/Capsule Colliders** to `Head`, `Neck`, `Chest`, `Upper Arm`, and `Thighs` matching visual radii; include final tip dummy tail bone on every spring chain |
| 30 | Game engine drops vertex bone weights or spikes random geometry corners | Blender left `> 4` bone weights per vertex (`5–8` influences) or un-normalized floating sums | Always run **`Limit Total (4)` -> `Clean (0.01)` -> `Normalize All`** on every skinned mesh before `.fbx`/`.glb`/`.vrm` export |

## 6. Shape Keys, Animation & Export Pitfalls (Including Blender 5.2+ API)

| # | Bug / Symptom | Root Cause | Exact Veteran Fix |
|---|---|---|---|
| 31 | `Modifier cannot be applied to a mesh with shape keys` | Created `blink` / `aa` Shape Keys *before* applying `Mirror`, `Subdivision`, or `Bevel` modifiers | Always **apply all topology-changing modifiers BEFORE adding the first Shape Key**, or run a duplicate-and-rejoin shape-key preservation script (`apply_with_shapekeys`) |
| 32 | Mouth or blink doubles up horribly (`Face explodes twice as wide`) | `Basis` key already had smile/parted mouth baked in, OR left/right blink shared un-tapered center bridge vertices | Keep **`Basis` 100% neutral relaxed face** (`0%` blink, `0%` smile); blend mirror center seam (`X = 0`) cleanly `0.5 -> 0.0` when splitting shapes with **`Blend From Shape`** |
| 33 | Animation looks floaty, sluggish, and unmistakably "cheap 3D CG" | Smooth auto-Bezier curves at 60fps + EEVEE Motion Blur ON + moving all characters uniformly every frame | Set **`24 fps` + Motion Blur OFF**; animate pose-to-pose using **NLA / F-Curve `Stepped Interpolation` (`2s` / `3s`)**; skip fast mid-swing transitions (`Guilty Gear`); animate background elements slower or `hold` completely (`Noggi`) |
| 34 | Motion smears make character stay stretched for `5+` frames looking rubbery | Left **Lattice / Smear Shape Key** on slow Linear splines instead of 1-frame `Constant` steps | Keyframe **`Smear Shape Key` / `Lattice Strength` / `smear_geo` visibility** strictly with **`Constant` interpolation** on **1 frame (`24fps` = `42ms`)** (`2–3` frames at `60fps`), turning cleanly back to `0.0` the very next frame |
| 35 | Blender `.fbx` export finishes with **ZERO blendshapes / Shape Keys** in Unity/Unreal | Checked FBX Exporter **`Apply Modifiers`** option on a character mesh that contains Shape Keys! | Keep topology modifiers already applied cleanly before Shape Keys, keep ONLY `Armature` live, and **UNCHECK `Apply Modifiers`** during `.fbx` export! |
| 36 | `ShaderNodeMixRGB` script fails in Blender 5.x (`Unknown node type`) | Blender 5.0 removed legacy `ShaderNodeMixRGB` node | Always use **`ShaderNodeMix`** with `node.data_type = 'RGBA'` (access Factor `[0]`, A `[6]`, B `[7]`, Result `[2]`) |
| 37 | `AttributeError: 'Action' object has no attribute 'fcurves'` in Blender 5.x scripts | Blender 5.0+ removed legacy `action.fcurves` in favor of **Slotted Actions & Channelbags** | Use `from bpy_extras import anim_utils; cb = anim_utils.action_ensure_channelbag_for_slot(act, slot); fc = cb.fcurves.ensure(...)` |
| 38 | Script fails in Blender 5.x with `mesh.use_auto_smooth` or `bone.select` or `bone.layers` | Blender 4.1–5.0 removed `use_auto_smooth`, armature `.layers`, `Bone.select`, `FAST` Boolean, and `GreasePencilv3` | Use **`Smooth by Angle` modifier** (not `use_auto_smooth`), **`arm.collections`** (not `.layers`), **`edit_bone.select` / `pose_bone.select`**, **`FLOAT` Boolean**, and **`GreasePencil`** type |
| 39 | VRM 1.0 character expressions do not blink or lip-sync in VTuber apps (`VSeeFace` / `Warudo`) | Named blendshapes with VRM 0.x UpperCase (`Blink`, `Joy`, `A`) or exported raw `.glb` without VRM 1.0 mapping | Map exact **VRM 1.0 camelCase preset names** (`aa`, `ih`, `uu`, `ee`, `oh`, `happy`, `angry`, `sad`, `relaxed`, `surprised`, `blink`, `blinkLeft`, `blinkRight`) inside VRM Add-on Expressions before `.vrm` export |
| 40 | Custom anime pose looks strong in 3/4 Viewport but awkward and stiff in final render | Violated **Camera View Is King** rule by only sculpting/posing in free orbit perspective | Lock split viewport to active **Render Camera (`Numpad 0`)**, adjust silhouette gaps between all 4 limbs, push camera-plane squash/stretch & rim lights specifically for the final camera lens (`focal 50–85mm` portraits, avoid wide lens face distortion!) |

---

## 7. Mandatory Pre-Delivery QA Gate Checklist

Run through all **10 checks** (manually or via `blender-asset-qa`) before calling any anime character model, rig, or animation **done**:

1. **Color & Render Sanity (`EEVEE`)**: Render Engine = `BLENDER_EEVEE`, View Transform = **`Standard`**, Motion Blur = **`OFF`** (`24 fps` for anime film), no washed-out gray GI bounce.
2. **Scale & Transforms**: Origin `(0,0,0)`, resting soles at `Z = 0.0`, Facing `-Y` (or matching engine pipeline), **`Scale = (1.0, 1.0, 1.0)`** on all meshes & armatures (`Ctrl+A`).
3. **Geometry & Face Orientation**: Zero loose double vertices (`Merge by Distance`), **100% Blue** outside in `Face Orientation` (zero accidental flipped red outside shells on hair/clothes), zero z-fighting decals (`>= 2 mm` offset), no non-manifold hair ribbon errors.
4. **UV & Texture Verification**: Zero `0`-area UV faces, `Non-Color` set cleanly on every `ILM` / `SDF` / `Normal` / `Roughness` / `Metallic` texture, `[0, 1]` UV layout if targeting engines (`Unity`/`VRM`/`Roblox`), packed/relative image paths (`//textures/`).
5. **Toon Face & Normal Verification**: Orbit key light full `360°` yaw around head—verify **zero nose blotches**, smooth forehead wrap (`Data Transfer` / `Abnormal` / `SDF`), and verify `Outline` shell (`Solidify`) has no cracked edge gaps, nose spikes, or Cycles pitch-black box (`Backfacing` + `Is Camera Ray` + `Transparent Shadows`).
6. **Rigging & Weight Stress Test**: Test extreme `Pose Mode` poses (`90°–120°` knee bend, `+100°` overhead arm raise, `+45°` neck yaw/tilt, high sprint leg kick with skirt):
   - Zero eye/jaw drag on neck rotation (`1.0 Head weight`).
   - Zero skirt hip-clipping or opposite-leg tearing (`thigh` weights stripped; `Link 2+` spring root).
   - Game exports: `Limit Total 4`, `Normalize All`, `Only Deform Bones`, `QUATERNION` rotations, `Preserve Volume = OFF` tested!
7. **Shape Key Integrity**: `Basis` strictly relaxed/neutral; test **`blinkLeft`, `blinkRight`, `aa`, `oh`, `happy`** individually and simultaneously (`no cornea poke-through`, `eyelashes follow lid`, `teeth stay inside mouth`).
8. **Physics / Colliders Check**: `Wiggle 2` / `VRM SpringBone` hair & skirt tips include dummy tail bones and matching `Head/Chest/Thigh` sphere colliders without intersecting cheek skin.
9. **Blender 5.x Script Check**: Zero calls to removed APIs (`ShaderNodeMixRGB`, `action.fcurves`, `use_auto_smooth`, `bone.layers`, `bone.select`, `BLENDER_EEVEE_NEXT`, `GreasePencilv3`, `FAST` Boolean).
10. **Visual Multi-Angle Contact Sheet**: Inspect rendered Front, 3/4 Left/Right, Side, Back, Close-up Face, Light `0°/90°/-90°` test renders, and Pose Stress sheet at target camera view (`Numpad 0`) before final handoff.
