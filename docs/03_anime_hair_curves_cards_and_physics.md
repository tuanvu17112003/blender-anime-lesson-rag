---
doc_id: anime-hair-curves-cards-and-physics
title: Anime Hair Modeling (Curve Ribbons), UVs, Normals & Physics Chains
topic: modeling-hair
kind: modeling-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate
tags: anime-hair, curves, bevel-object, nurbs, scalp-cap, hair-uv, angel-ring, hair-normals, wiggle-2, spring-bone, 2am, natsumori-katsu, yansculpts
sources:
  - 2AM — Blender: How to Make HAIR, Full Workflow | Modelling, Texturing, Normal Editing (LU0BFThJIco)
  - 2AM — Rig Hair Moving Parts & Remesh Bangs (blgGcbZzsWM)
  - Summer / Natsumori Katsu — Hair Modeling Lecture: Anime-style hair with curves (Ng8FbOHvsLQ, Sy7RHtco43Y)
  - YanSculpts — Easiest Way To Create Hair in Blender (BqWYgrXw7Jk)
  - Astonished — Make anime hair like gachas! (HGKYUWI44lQ)
  - CoderNunk — Modeling The Hair (codernunk.com)
  - Riel — Model Stylized Hair Faster with HairMesh (46F7k4fvsN8)
---

# Anime Hair Modeling (Curve Ribbons), UVs, Normals & Physics Chains

AI agents often try to generate anime hair using realistic `Hair Curves / Principled Hair BSDF` (100k fine strands) or blocky sculpted metaballs. Neither works for anime! Production 3D anime characters use **layered Curve-to-Mesh hair ribbons** anchored over a **Scalp Base Cap**.

## 1. Why Curve Ribbons Are the Industry Standard
- Clean quad edge flow running **root -> tip** (trivial to UV unwrap straight vertically for anime highlights).
- Instant global polycount tuning via `Resolution Preview U` before mesh conversion.
- Non-destructive thickness (`Alt+S`) and twist (`Ctrl+T`) adjustment per lock.
- Easy to skin onto `3–6` bone chains for `Wiggle 2` or `VRM SpringBone` physics.

---

## 2. Step-by-Step Curve-to-Mesh Hair Pipeline

### Step 1: The Scalp Cap ("Hair Net") — Mandatory!
Never stick hair locks directly onto a bald skull! Any camera movement or windy physics will expose bald skin patches between bangs (`2AM`, `Natsumori Katsu`).
1. Enter Edit Mode on `SK_Head`, select all scalp faces above the hairline, temples/sideburns, and nape of neck.
2. Duplicate (`Shift+D`) -> Separate (`P -> Selection`) -> rename `SK_Hair_ScalpCap`.
3. Push outward slightly (`Alt+S` Shrink/Fatten `~2–4 mm`) so it sits cleanly outside the head skin without z-fighting, assign base hair material, and close/clean the hairline edges around the ears and neck.

### Step 2: Build the Custom Bevel Profile & Path Curve
1. **Profile Curve (`Hair_Profile`)**: Add `Curve -> Circle` (or Bezier Circle).
   - Set `Resolution Preview U = 1` or `2` (higher values explode polycount into tens of thousands of wasted tris!).
   - In Edit Mode, shape it into a **crescent/indented ribbon** (or triangle/diamond cross-section with a **flat or slightly concave back side** facing the skull and a crisp/rounded front ridge facing outward). Keep its pivot centered on its origin!
2. **Strand Curve (`Hair_Strand`)**: Add `Curve -> Path` (NURBS Path) or `Bezier Curve`.
   - Set **`Resolution Preview U = 3`** (or `2–4` max — keeps strand clean at `~4–6` vertical loops instead of `12+`).
   - Under `Object Data -> Geometry -> Bevel -> Object`, pick `Hair_Profile` (`2AM`, `YanSculpts`, `CoderNunk`). (Optionally enable `Fill Caps` or merge tips after converting to mesh.)
3. **Essential Curve Shortcuts**:
   - `Alt + S`: Scale point radius (**`0.0`** at the very tip to taper to a razor-sharp anime lock point; wider in mid-strand!). *Note: Regular `S` moves handles/spacing, not bevel radius!*
   - `Ctrl + T`: Twist/tilt strand so the rounded ridge faces outward and the flat side hugs the head.
   - `E` / `Subdivide`: Extend or add control points.
   - **Shonzo's Anti-Flip Hook Tip**: If a curve flips/twists upside down unpredictably when moved forward (`gimbal flip` on curve Z-up), select the curve in Object Data -> **`Twist Method = Minimum`** (or `Z-Up`), or add a gentle root curve hook tucked inside the head so the tangent vector stays smooth!

### Step 3: Layer Strands in 4 Distinct Zones (Avoid Uniform Spikes!)
Follow `Natsumori Katsu` (`Sy7RHtco43Y`) and `2AM` (`LU0BFThJIco`):
1. **Back Hair Volume**: Broad thick locks fanning from the crown/top whorl (`set object origin at hair root` so duplicating + rotating around the head is effortless!). Make inner/under layers dark/filled cleanly so looking upward from low camera angles never sees hollow back-faces!
2. **Side Locks (Cheek Framing)**: Frames the jawline/ears (`crucial for character cuteness!`). Keep them slightly curved around the cheeks with branched/split tips (`V` or layered thin sub-strands) so they look soft, not stiff metal spikes.
3. **Front Bangs**: Place a central lock overlapping symmetrical side bangs, then **break strict symmetry** (`2AM` / `Natsumori Katsu`): vary strand widths, lengths, and curl directions so the hairstyle doesn't look stamped/mirrored!
4. **Ahoge / Flyaways / Ponytails / Braids**:
   - **Ahoge / stray wisps**: Separate thin curves inserted into the crown so they can bounce independently.
   - **Braids (`CoderNunk`)**: Build a repeating 2-lobe twisted braid segment (`Origin` at center) -> `Array` (`Fit Curve`) + `Curve` modifier along a NURBS path -> convert & sculpt smooth.
   - **Depth Layering Rule**: Never tuck all strands at the exact same radius from the skull (`causes z-fighting and tangled clipping`); layer explicitly into **Under-layer -> Mid-layer -> Hero outer layer**.

### Step 4: Conversion, Tip Cleanup & Optional Remesh
1. **ALWAYS duplicate your raw Curve objects into a hidden `99_Backup_Curves` collection** before converting! (Once converted to mesh, you lose curve editing.)
2. Remove unapplied `Mirror`/`Subdivision` modifiers if they behave oddly during conversion, select curves -> `Object -> Convert -> Mesh`, then re-apply `Mirror` (`Clipping = True`) if symmetrical.
3. **Merge Tip Vertices**: Zero-radius curve tips still create overlapping duplicate vertices at the exact same point! Select all (`A`) -> **`M -> Merge by Distance`** (`threshold = 0.0001`).
4. **Check Normals**: Enable `Overlays -> Face Orientation`. Curve conversions frequently produce inside-out red strands! Select all -> `Mesh -> Normals -> Recalculate Outside` (`Shift+N`), or `Flip` red islands.
5. **Optional Bang Fusion (`2AM` `blgGcbZzsWM`)**: If overlapping bangs cause `Automatic Weights` or `Solidify` outlines to artifact, separate the moving bang cluster -> cap open ends (`F`) -> `Sculpt Mode -> Voxel Remesh` -> `Decimate` modifier down to game budget -> `Tris to Quads` (for clean silhouette without interior hidden intersections!).

---

## 3. Anime Hair UVs, "Angel Ring" Highlights & Custom Normals

1. **Straightened Root-to-Tip UVs (`2AM`, `Astonished`)**:
   - Mark 1 lengthwise UV seam down the **back/hidden underside** of each hair lock (`Shift+Alt+Click` edge loop -> `Mark Seam`).
   - Unwrap (`Angle Based`), then **rectangulate every strand island** (`S X 0`, `S Y 0`, `Follow Active Quads` or `Mio3UV` Grid/Straighten) with **all roots aligned at `V = 1.0` (top)** and **all tips at `V = 0.0` (bottom)**!
   - Stack similar secondary hair locks neatly over the same hair-strand column on your texture atlas to maximize pixel resolution (`2AM` `LU0BFThJIco`).
   - Why this matters: A horizontal bright painted/shader band across `V ≈ 0.65–0.75` automatically wraps cleanly across every hair lock as the classic anime **"Angel Ring"** highlight!
2. **Simplifying Hair Shading with Spherical Normals (`2AM` `LU0BFThJIco`, `ASW`)**:
   - Raw per-strand hair normals scatter cel-shaded shadows into messy jagged zebra stripes.
   - **Fix**: Wrap a high-subdiv (`level 4–6`) UV Sphere / deformed ellipsoid closely around the hair volume -> add `Data Transfer` modifier to the hair (`Face Corner Data -> Custom Normals`, `Nearest Corner and Best Matching Face Normal`) -> Apply! Now the entire hairstyle shades as one cohesive anime silhouette!
   - **Crucial Warning (`ASW` Slide 58)**: Once you spherize hair normals, `Solidify` inverted hulls expand along those spherical normals instead of the strand geometry—causing gaps at hair tips! **Always keep a clean smooth-normal set for outlines or paint outline weights to `0.0` at hair tips!**

---

## 4. Hair Rigging & Physics Setup

- **Static Crown / Scalp**: Weight **`100%` (`1.0`) to `DEF-spine.006` / `Head`**. Never allow neck or shoulder bones to influence any hair lock unless it's a long lower ponytail draping over shoulders!
- **Dynamic Locks (Bangs, Side Locks, Ponytails, Twintails)**:
  - Add `3–6` connected bone chains starting from the root inside the head -> parent the top root bone of each chain to `Head` (`Keep Offset`).
  - Use `.L` / `.R` suffixes + `Armature -> Symmetrize`.
  - Paint smooth linear gradient weights from `Bone 1` (root, partly shared with `Head` so the root doesn't detach from scalp!) down to `Bone N` (tip).
  - **Physics**:
    - **Inside Blender (`Wiggle 2`)**: Enable `Head` on the chain's root bone (pinned) and `Tail` on child bones; configure stiffness/damping/gravity; add Head/Shoulder mesh as **Wiggle Collision**; bake with `Loop Physics` + `Preroll`.
    - **For VRM / Unity**: Add a `VRM SpringBone` group referencing ONLY the root bone of each moving chain + assign **Head & Torso Sphere/Capsule Colliders** (`VRMC_springBone`) so bangs don't clip into the eyeballs or forehead!
