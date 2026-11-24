---
doc_id: anime-character-rigging-and-weights
title: Anime Character Rigging, Rigify Setup, Weight Painting, and Hair/Skirt/Bust Physics
topic: rigging-and-weights
kind: practitioner-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate-advanced
tags: rigging, rigify, metarig, bone-collections, weight-painting, voxel-proxy, data-transfer, skirt-weights, wiggle-2, springbone, corrective-drivers, vrm, unity-humanoid, game-skeleton
sources:
  - natsumori_katsu_modeling_rigify_unity_vrchat (Sy7RHtco43Y)
  - 2am_rig_everything_hair_chest_clothes (blgGcbZzsWM)
  - codernunk_complete_3d_character_guide.md
  - Blender_Wiggle_2/README.md
  - VRM_Addon_for_Blender/docs/en-us/create-humanoid-vrm-from-scratch/index.md & VRMC_springBone-1.0
  - Blender 5.3 Skill: blender-character-rigging
---

# Anime Character Rigging, Rigify Setup, Weight Painting, and Hair/Skirt/Bust Physics

Automatic rigging and "Generate Rig" defaults frequently explode on anime characters: feet invert backwards, knees bend sideways on IK, neck weights deform stiff eyeballs, skirts pull violently with running legs, and Rigify generates 100+ unused face bones that blow past Unity/VRChat/Roblox mobile bone limits.

---

## 1. Pre-Rigging Checklist (Before Adding or Generating an Armature)

Verify every item before parenting meshes:
1. **World Scale & Facing**:
   - Character stands centered at `(0, 0, 0)`, facing **`-Y`**, `+Z` up, feet soles resting at `Z = 0.0`.
   - Real-world humanoid height: `~1.50 m – 1.75 m`.
2. **Apply All Transforms (`Ctrl+A → All Transforms`)**:
   - Every character mesh AND the Meta-Rig must have `Location = (0,0,0)`, `Rotation = (0,0,0)`, **`Scale = (1,1,1)`**. Unapplied scale causes Automatic Weights to fail silently (`Bone Heat Weighting: failed to find solution`), breaks Rigify IK snapping, and scrambles exporter root scales.
3. **Neutral Symmetrical Pose & Geometry Prep**:
   - Arms in **A-pose** (`~30°–45°` down—less shoulder armpit pinching than a rigid 90° T-pose while still clean for Unity/VRM/Rigify) or clean T-pose if VRM 1.0 auto-retarging requires horizontal T-pose alignment (Note: VRM 1.0 requires a clean T-pose rest pose for engine humanoid mapping!).
   - **`Merge by Distance`** (`0.0001 m`) applied; **`Mirror`**, **`Solidify` (if geometry-baked)**, and **`Subdivision Surface`** modifiers resolved so **Mirror never runs *below* Armature**. Keep `Armature` near the top of the modifier stack (only `Smooth`/Shape Keys affect rest shape before skinning, and `Data Transfer` custom normals either baked before rigging or parented to `Head` bone).
   - Recalculate outside normals (`Shift+N`); check **Face Orientation** so character shell is completely Blue.

---

## 2. Rigify Human Meta-Rig Tuning for Anime & Game Engines

### Natsumori Katsu's Three Golden Meta-Rig Rules
1. **Center Spine (`X = 0`) Strictly Zeroed**:
   - Keep `spine`, `pelvis`, `neck`, `head` heads/tails on exact `X = 0.0` (enable `X-Axis Mirror` in Edit Mode before moving any `.L`/`.R` limb bone!).
2. **Never Disconnect Parented Joints**:
   - When moving knees, elbows, wrists, ankles, or chest bones to match an anime body, move the **joint sphere**, not detached heads/tails that pull `connected` Rigify chain joints apart. Breaking chain connections causes **`RIGIFY ERROR: Spine/Arm/Leg chain disconnected`** on Generate Rig!
3. **Slight Natural Pre-Bend on Elbows & Knees (Never 180° Straight!)**:
   - Place knees slightly forward (`-Y`) and elbows slightly backward (`+Y`). A perfectly collinear `180°` arm/leg chain gives Rigify's IK solver an ambiguous bend plane, causing knees or elbows to snap sideways or flip backward mid-animation!

### Anime Facial Bones vs. Shape Keys (Game/VRChat Optimization)
- Full **Rigify Human Meta-Rig** includes ~100+ realistic facial bones for Pixar-style lip/eyelid deformation.
- **For anime characters (unless specifically doing film bone-face rigs)**: Delete all small Rigify facial jaw/nose/lip/brow meta-bones and keep ONLY `spine.006` (`Head`), plus optional simple **Eye Aim bones (`Eye.L`, `Eye.R`)** and **`jaw` (optional)**. Drive blinks, eyebrows, cheek blush/wince, and `aa/ih/uu/ee/oh` mouth lip-sync using **Shape Keys** instead—cheaper for VRM/VRChat/Unity (`Quest` strict bone caps) and produces much cleaner 2D anime curves without mushy multi-bone weighting!
- **Bone Roll (`Ctrl+N` → Active Bone / Global `+Y` / `+Z`)**:
  - Fingers bend along local `+X` (thumb bends inward along its palm axis); knee/elbow hinges bend cleanly along uniform primary axes so FK curl sliders never twist sideways.

### Adding Anime Hair, Ribbon, Skirt, Tail, and Bust Bones cleanly inside Rigify
Instead of hand-building an unconnected second armature (which splits animations and breaks single-rig engine exports):
1. In **Meta-Rig Edit Mode**, add bone chains parented to the appropriate Rigify parent:
   - Hair bangs/twintails/ponytail -> parent to `spine.006` (Head bone).
   - Skirt front/back/side chains (typically `6–10` radial chains × `3–4` links each) -> parent to `spine` (Pelvis/Hip root) with **`Deform` = ON** (important: see Section 4 below for exact Skirt Spring placement!).
   - Collar ribbons / Chest / Breast (`Breast.L/.R` if enabled) / Coat tails -> parent to `spine.003` (Chest/Upper Torso) or `spine.002`.
2. In **Pose Mode → Bone Properties → Rigify Type**:
   - **If exporting physics bones to Unity/Godot/VRChat (`VRM SpringBone` / Dynamic Bones / Magica Cloth)**: Assign Rigify type **`basic.super_copy`** with **`Control = False` (`Make Control` unchecked) and `Deform = True`**. This prevents Rigify from littering the viewport with 60 unnecessary hair/skirt control shapes while automatically transferring all **`DEF-*`** hair/skirt bones cleanly into the generated rig hierarchy!
   - **If animating hair/cloth manually in Blender shots**: Assign **`limbs.simple_tentacle`** (`FK + Tweak` controls) so animators get clean FK overlap arcs + Stretch/Tweak handles, OR use `basic.super_copy` with `Control = True` + **Wiggle 2**.
3. **Symmetry Naming**: Strictly suffix symmetric chains `.L` and `.R` (e.g., `HairSide.L`, `HairSide.R`) -> Armature → **`Symmetrize`** generates the mirror cleanly.

### Blender 4.0+ / 5.x Bone Collections (`arm.collections`, Replacing Legacy Layers)
- Blender 4.0 removed 32 numbered bone layers, and Blender 5.x removes old layer references completely.
- In generated Rigify rigs (and custom rigs):
  - **`DEF` collection**: Holds ONLY deformation bones (`DEF-hips`, `DEF-spine...`, `DEF-Hair...`). **Isolate / Solo ONLY `DEF` when weight painting** so you never accidentally paint onto `MCH-*`, `ORG-*`, or `CTRL-*` mechanism bones!
  - Enable **`Export Only Deform Bones` (`use_deform_only=True`)** during `.fbx`/`.glb` export so control widgets and mechanism bones never bloat the game skeleton.

---

## 3. Weight Painting & Skinning Pipeline (Zero-Popping Rules)

### Step 1: Parenting & Solving Automatic Weight Failures
- Select Mesh(es) → Shift-Select Armature (in `Object Mode`) → `Ctrl+P` → **`With Automatic Weights`**.
- **If `Bone Heat Weighting: failed to find solution` occurs** (super common on multi-layer anime outfits with intersecting collars, pleats, layered hair spikes, or tiny accessory shells!):
  1. Check for overlapping duplicate verts (`Merge by Distance`), open non-manifold edges, negative object scale, or zero-area faces.
  2. **Voxel Proxy Skinning Workaround (`blender-character-rigging` pro fix)**:
     - Duplicate the multi-part character, `Voxel Remesh` it into one unified watertight manifold proxy (`0.008–0.015 m` voxel size), parent the proxy to the Armature with **`With Automatic Weights`** (heat solver succeeds immediately on closed manifold shells!), then transfer weights to each true anime garment/body mesh using a **`Data Transfer`** modifier (`Vertex Data → Vertex Groups`, `Mapping = Nearest Vertex` or `Projected Face Interpolated`), Click **`Generate Data Layers`** and **`Apply`**!
  3. **Alternative for Separated Rigid Parts**: Parent with **`With Empty Groups`**, then assign `1.0` weight to exact target bones in Edit Mode (`Vertex Group → Assign`).

### Step 2: Critical Weight Rules by Anime Body Part (`2AM` + `Natsumori Katsu`)

| Region / Part | Veteran Weight Rule | Why Random Auto Weights Fail |
|---|---|---|
| **Head above Jaw (`Crania, Nose, Cheeks, Ears, Eyes, Eyelashes, Teeth, Hair Roots`)** | Paint **`1.0` pure Red (`Mix`, weight `1.0`) to `DEF-spine.006` (Head)** and **remove (`Clean`/erase `0.0`) ALL weights from Neck/Chest/Shoulder bones**! | Auto weights bleed Neck (`spine.004/005`) and Clavicle weights into the cheeks, jaw underside, eyes, and lower bangs—causing eyeballs to pop sideways or jawlines to warp when the neck turns! |
| **Eyeballs / Cornea / Highlight Planes / Upper Teeth** | **`1.0` strictly to `EyeAim.L/.R` (if bone-aimed) or `1.0` strictly to `Head`** (no neck/spine influence ever) | Bleeding weights turn eyes into ovals whenever the neck bends |
| **Shoulders / Clavicle (`Arm Raise Test`)** | Smooth gradient over deltoid cap + upper pectoral; include partial `Shoulder` rotation weight so arm lift pulls clavicle cleanly instead of pinching armpit holes | Unweighted clavicles crush the shoulder socket flat at `90°+` arm raises |
| **Elbows & Knees (`90°–130°` Extreme Bend Test)** | Check **Weight Paint → Brush → Options → `Auto Normalize = ON`**; ensure `DEF-forearm`/`DEF-upper_arm` (`shin`/`thigh`) cross smoothly across the 3-loop joint band; enable **`Preserve Volume` (Dual Quaternion)** in Armature modifier ONLY for Blender renders (note: real-time game engines use **Linear Blend Skinning**, so test with `Preserve Volume = OFF` for game exports!). | Candy-wrapper twist or sharp knee collapse |
| **Rigid Pins, Buttons, Buckles, Ribbons, Jewelry** | **Rigid `1.0` weight to ONE bone (`Normalize`)**, or use **Transfer from Chest proxy**. Never leave multi-bone soft bleed across a metal brooch/belt buckle! | Stretches metal buttons like rubber chewing gum |
| **Fingers (`Grab/Fist Curl Test`)** | Keep knuckles sharply isolated to their respective phalanx (`f_index.01..03`) so curling one finger doesn't tug adjacent fingers | Auto weights bleed between closely modeled parallel fingers |

### Step 3: Skirt & Multi-Layer Dress Rigging (`2AM` / Skirts Without Hip Clipping!)
Automatic weights on a skirt attach the skirt hem directly to `thigh.L` / `thigh.R`, causing ugly V-tears down the front crotch or dragging the entire hem horizontally when lifting one leg. Do this instead:
1. Weight the **waistband / top skirt ring** rigidly to `spine` / `pelvis` (`DEF-spine`), **stripping `DEF-thigh.L`, `DEF-thigh.R`, `DEF-pelvis` stray distortions cleanly**—or start with **`Data Transfer`** weights from the underlying clean torso/pelvis mesh and manually **`Remove` leg bone weights** from the flare!
2. Add **Skirt Chain Bones (`6–10` chains radially)** around the hip circumference, pointing downward along skirt drape direction.
3. **2AM Skirt Root Placement Secret**: Do **NOT** put dynamic wiggle/spring physics on the very top waist bone (`Link 1`). Keep `Link 1` pinned stiff (`Pelvis` control) or start physics softness from **`Link 2` onward**, paired with subtle manual `thigh -> skirt` **Track/Limit Rotation (`Copy Rotation` partial positive only when leg kicks forward)**! This stops the skirt from snapping backward or clipping straight into the upper thighs when sprinting.
4. **Weight Normalization & Engine Limits**:
   - Before exporting: Mesh Data → Vertex Groups dropdown → **`Limit Total` (`4` influences max—strictly required by Unity, Unreal, Roblox, glTF/VRM GPUs!)**, then **`Clean` (`Keep Single`, threshold `0.01`)**, then **`Normalize All`** (so weights on every vertex sum strictly to `1.0`).

---

## 4. Hair, Bust & Cloth Physics (`Wiggle 2` vs. `VRM SpringBone` vs. Blender Renders)

| Pipeline | Recommended Tool | Key Production Rules |
|---|---|---|
| **Blender Shot Animation (Cycles/EEVEE)** | **`Blender Wiggle 2`** (`wiggle_bone` addon) | Enable per-tail/hair/skirt chain cleanly (`Rotation` + optional gentle `Stretch` on hair ends); set **Armature Colliders** (head/shoulder capsules) to prevent hair poking through clavicles; **Bake Wiggle to Keyframes** *before* final step-frame passes or render farms! |
| **VRM / VTuber / Unity / VRChat (`PhysBones`)** | **`VRM SpringBone`** / Unity **`PhysBones`** | Parent root bone cleanly to `Head` / `Chest` / `Hips`; add **Tail Leaf Bone** (`dummy` end joint) at tip so engine calculates last segment orientation; place **Sphere/Capsule Colliders** inside Head, Neck, Upper Chest, Upper Arms, and Thighs so twintails and skirts slide cleanly over geometry without zero-cost cloth simulation! |
| **Tight Jackets / Tunics / Thigh-Highs** | **Skin-Weight Transfer** | No cloth sim or spring bones needed—use **Data Transfer (`Nearest Face Interpolated`)** from body skin onto clothes, then lightly smooth jagged edges with Weight Paint `Blur` (`Auto Normalize = ON`). |

### Shoulder / Hip Volume Loss Fix (Corrective Drivers & Blendshapes)
For game exports that use Linear Blend Skinning (`Preserve Volume = OFF`):
- Author a corrective Shape Key (e.g., `corr_shoulder_up.L`) sculpted ONLY while **`DEF-upper_arm.L` is rotated `+90°`**, then drive its value (`0.0 → 1.0`) directly from `DEF-upper_arm.L`'s **`ROT_Z` / `ROT_X` `LOCAL_SPACE`** bone channel (`Transform Channel` driver). Keep driver range clamped `0.0–1.0` cleanly so resting T/A poses remain `0.0`.
