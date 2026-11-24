---
doc_id: anime-head-face-topology-and-eyes
title: Anime Head, Face Topology, Eyes, Eyelashes & Mouth Bag Playbook
topic: modeling-head-face
kind: modeling-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate
tags: anime-head, face-topology, eyes, iris, eyelashes, eyebrows, mouth-bag, guilty-gear, hoyoverse, wuthering-waves, 2am, shonzo, daniel-kreuter, natsumori-katsu, collection-instance
sources:
  - 2AM — How to Make Anime FACE in Blender Explained! + Custom Shadows (uptuXWNWpk0)
  - 2AM — Hack ANY 3D Art Style w/ Reverse Engineering (9hNmJYqKQys)
  - 2AM — How to Make 3D Anime EYES Like a Pro! (hZMO3OgV-Lw)
  - SunnyIsOnline ft. Dillongoo — How to (Actually) Make Anime in 3D (4LhvcINgNxU)
  - Shonzo — New Anime Style 3D Modeling Guide (HHCGrbeTWww)
  - Summer / Natsumori Katsu — CGWORLD Blender Fes (Sy7RHtco43Y)
  - Chaosy3D — Create an Anime Girl Body in Blender (yg8Snn3OzLc)
  - Daniel Kreuter — Anime Character Modeling Series (AlX-wVx-NNU, RtrOSuAGFgQ, 1oAicxULj20)
---

# Anime Head, Face Topology, Eyes, Eyelashes & Mouth Bag Playbook

The face and eyes carry **80% of an anime character's appeal**. Generic photorealistic head topology fails on anime characters because stylized eyes are huge, noses are tiny triangular planes, cheeks are flattened, and cel-shading exaggerates every irregular vertex bump.

## 1. Core Decision: Which Face Topology Pattern?

| Topology Variant | Best For | Mouth Structure | Shading Method |
|---|---|---|---|
| **Pattern A: Clean Quad + Mouth Diamond** (*Hoyoverse / WuWa / VRM*) | 360° game cameras, VTubers, ARKit/VRM lip sync, clean subdivision | **Diamond boundary loop** enclosing **concentric circular lip loops** (`2AM` `9hNmJYqKQys`) | SDF Face Shadow Map OR Ellipsoid `Data Transfer` normals |
| **Pattern B: Radial Triangle Mouth Fan** (*Guilty Gear / ArcSys*) | Cutscenes, extreme anime mouth expressions (`:D`, shout), 2D-exact look | Dense lip verts fanning outward as **radial triangles** to a rigid outer mouth ring (`2AM` `uptuXWNWpk0`, `SunnyIsOnline`) | **Mandatory** custom split normals (`Copy/Paste Vectors` / `Abnormal`); looks broken under default normals! |

> **Golden Rule**: NEVER sculpt or model an extreme smile into your `Basis` mesh! Always model the mouth in a **calm neutral resting line** (slightly downturned corners or gentle flat line); build smiles, grins, and open vowels exclusively as **Shape Keys** (`Chaosy3D`).

---

## 2. Step-by-Step Anime Head Construction (Low-Bump Poly Method)

Synthesized from `2AM`, `Natsumori Katsu`, `Chaosy3D`, and `Shonzo`:

### Step 1: Silhouette & Kite-Shield Blockout
1. Start from a front-facing `Plane` (or merged single vertex) with **`Mirror` modifier (`Axis X`, `Clipping = True`)**. Do **NOT** leave an active `Subdivision Surface` on permanently if doing tight shadow-loop modeling—dense uncurated subdiv surfaces cause bumpy shading (`Shonzo`). If you use Subdivision to block out (`2AM` WuWa kite-shield method), apply it once at low/mid density and cull/slide edges cleanly afterward!
2. Define the **jawline & side-profile silhouette FIRST**:
   - Trace front jawline from chin -> cheek corner -> ear root.
   - Switch to Right Ortho (`Numpad 3`): pull nose tip forward (`~10–15%` of head depth), keep **lips strictly behind the nose-to-chin line** (`2AM`), and give the forehead a gentle convex curve rather than a sharp spike.
3. **Shonzo's Flat Frontal Face Rule**: Keep the central face region (between mouth, nose base, and front cheeks) nearly flat/planar, with two clean ridge lines radiating from the chin—one toward the cheek/ear, one under the chin toward the neck. Avoid hollowing cheeks inward (caved-in cheeks catch ugly shadows at 3/4 angles!).

### Step 2: Eye Socket Loops & 3/4 Profile Rotation Trick
1. Create a **`12–16` vertex** loop around the eye opening (`8` vertices for ultra-low-poly).
2. Extrude **one outer ring** around the eye (defines the eyelid crease & brow ridge boundary).
3. **Crucial 3/4 & Side-Profile Fix (`SunnyIsOnline` / `ArcSys` PPT)**:
   - Do NOT leave the eye socket flat facing `+Y/-Y`, and do NOT rotate the entire eye loop blindly.
   - Instead, in Top View (`Numpad 7`), rotate the eye loop slightly outward (`~10–15°`), then enable **Proportional Editing** and pull **only the outer corner (`lateral canthus`) backward** along the head curve.
   - Why: Keeps the inner eye flat enough to read clearly from the front while allowing the iris to sit naturally tucked behind the cheek/brow contour in side view—preventing the dreaded "bug-eyed white sclera sticking out in profile"!

### Step 3: Nose Bridge & Custom Shadow Loop
1. Keep the nose bridge slim (`2–3` vertical face columns from upper lip -> philtrum -> nose tip -> brow bridge), flaring smoothly into the forehead.
2. **If using Pattern B (Edited Normals)**: Carve **two concentric teardrop loops** around the nose tip/wing and optionally **two concentric triangle loops** on one cheek for the anime Rembrandt shadow (`2AM` `uptuXWNWpk0`).
   - Inner loop receives the angled shadow vector; outer ring interpolates cleanly to the flat front face normal!
3. **Nostril / Nose Line**: Either paint a crisp tiny diagonal nose-line on texture (`Hoyoverse`) or extrude/inset a thin dark micro-strip on the side of the nose tip (`SunnyIsOnline`).

### Step 4: Mouth, Diamond Loop & Inner Mouth Bag
1. **Diamond + Circular Lip Loops** (`2AM` `9hNmJYqKQys`): Surround the mouth area (`bottom ~40% of face`) with a diamond perimeter connecting nose base -> cheeks -> chin, then fill concentric circular loops inside it so `Alt`-clicking selects clean lip rings for Shape Keys. Keep lip width **slightly narrower than the inter-eye gap**!
2. Split the resting lip line (`V` to rip edge) and extrude inward `2–3` times to build a closed **Mouth Bag** (`MouthBox` vertex group so you can hide it with `H` while editing!).
3. Add a tight creased edge loop (`Shift+E`) just inside the lip seam so open-mouth Shape Keys hold crisp anime lip corners.
4. Assign **`UpperLip`** and **`LowerLip`** to separate Vertex Groups immediately—resting lips overlap so tightly that manual re-selection later is painful!
5. Model **Upper/Lower Teeth** (curved U-arch strips, NOT individually modeled realistic teeth—individual tooth gaps look horrifying in anime!) and a simple **Tongue** tucked inside the mouth box (`Shonzo` / `Natsumori Katsu`).

### Step 5: Back of Skull, Neck Connection & Ears
1. **Neck Match**: Match the base neck vertex count to your torso's neck opening (`12–20` vertices full loop, flattened cleanly with `S Z 0` and tilted ~`10°` forward).
2. **Density Reduction Under Hair**: Collapse dense forehead/cheek edge flows into `2–3` clean quads/triangles along the **crown and behind the ears** where opaque hair covers the skull (`2AM` / `Natsumori Katsu`).
3. **Ears**: Delete `1` quad at the jaw-neck junction, inset/extrude outward `2–3` rings, angle slightly backward in Top View, crease root (`Shift+E = 1.0`). Triangles inside the inner ear concha are completely acceptable (`Chaosy3D`).

---

## 3. Anime Eyes, Lashes & Eyebrows (Step-by-Step)

Synthesized from `2AM` (`hZMO3OgV-Lw`), `Noggi`, and `Crashsune`:

### 1. Sclera (Eye Socket Backing)
- Extrude the inner eye-socket loop inward along `+Y` (back into head), scale slightly larger vertically/horizontally (`preventing iris edge clipping`), then extrude again and `M -> Merge at Center` (or `Grid Fill`).
- Material: **Very light gray (`#EBEBEB`–`#F2F2F2`, `sRGB`)**, NEVER pure white `#FFFFFF` (pure white clips/blooms harshly against highlights!).

### 2. Eye Socket Cast Shadow Strip (Secret Polish!)
- Duplicate the **top inner edge** of the eye socket, extrude downward as a thin curved ribbon sitting `~1 mm` in front of the sclera/iris.
- Assign a semi-transparent material (`Alpha Blend`: `50% Transparent BSDF + Dark Shadow/Skin Tint`) — creates authentic anime top-eyelid shadow across the white sclera and top of iris without needing dynamic shadow maps!

### 3. Eyelashes & Eyelid Crease (Hybrid Attached + Floating)
- **Upper Eyelash Base**: Extrude outward directly from the upper eye-socket loop (`connected to the face mesh!`). Why: When you sculpt the `eyeBlink` Shape Key, closing the eye socket automatically drags the lash base down cleanly!
- **Double Eyelid Crease**: Duplicate the upper eyelid arc edge above the socket, separate, subdivide/relax (`LoopTools -> Relax`), extrude thin dark strip, and snap (`Face Project`) flush onto the eyelid.
- **Outer/Individual Lashes & Lower Lash**: Extrude pointed triangular tips at inner/outer eye corners (`scale tip edge to 0`, add `2–3` loop cuts to curve, `Merge by Distance` tip). Keep decorative upper wing lashes separate so they rotate/flip cleanly during blink/wink.
- **Shading Detail**: Assign a **darker material** to the underside faces of the upper lash base so lashes separate cleanly from the bright sclera (`2AM` `hZMO3OgV-Lw`).
- **Placeholder Materials Early**: Assign temporary `Emission` solid colors (skin, dark brown lashes, light gray sclera, inner lid pink shadow) while modeling so you immediately read proportions—never model everything in default gray clay!

### 4. Eyebrows
- Duplicate faces along the brow ridge, separate (`P -> Selection`), extrude thickness, `LoopTools -> Relax`, snap (`Face Project`), then nudge `+1–2 mm` forward off the forehead so they never z-fight.
- **Anime "Brows Through Hair" Trick**: Keep eyebrows on a separate material/object layer (`NPR` compositor Render Layer / Goo Engine / Unity stencil buffer) so expressive eyebrows remain subtly visible through bangs!

### 5. Anime Iris & Noggi's Parallax Depth Trick
1. **Geometry**: Add a `24`-vert `Circle`, rotate `90°` on `X`, extrude inward twice, `Merge at Center`.
   - **Concave dish** (`push center backward`): creates authentic anime "follow-you" depth illusion from 3/4 views (`SunnyIsOnline`, `2AM`).
   - **Slight convex bulge** (`pull center forward` with `Sphere` proportional editing): stays more visible from extreme side profile (`CoderNunk`, `Noggi`). Test both against your character's side angle!
2. **2AM's Collection Instance Painting Trick**:
   - Unwrap the circular iris dead flat while centered on world axes (`0,0,0`).
   - Put it in an `Iris_Master` collection -> place a **Collection Instance** rotated into the eye socket (`~10°` outward, `~5°` downward).
   - Now paint the flat master iris dead-straight in Texture Paint / `Ucupaint` while simultaneously judging its final perspective in the socket! When finished, run `Object -> Apply -> Make Instances Real`, mirror across `X`, and flip UVs on the mirrored copy (`hZMO3OgV-Lw`).
3. **Layered Anime Iris Painting (Ucupaint)**:
   - Layer 1: Solid base iris hue -> Layer 2: Dark outer rim ring -> Layer 3: Dark upper half (with scalloped "jelly-bean" cutout shapes along bottom edge) -> Layer 4: Oval dark pupil + contrasting bright inner diamond/accent -> Layer 5: Soft crescent glow on lower half (`Add` blend, low opacity) -> Layer 6: Crisp white + pastel secondary **eye highlights** (optionally on a separate floating mesh `0.5–1 mm` forward so highlights can animate/jiggle independently!).
4. **Noggi's Parallax Iris Depth (`noggi.substack.com`)**:
   - Separate iris into `3` shader texture layers (`Base_Color`, `Ridges`, `Highlights`) driven by a UV **Parallax Offset** (`Incoming` vector in Tangent/Object space scaled by depth) — upper highlight floats in front while pupil recesses optically behind!

---

## 4. Quick Anti-Error Checklist for Anime Heads

- [ ] Are there bumpy triangles or uneven quad sizes across the cheek/forehead? (`Smooth Vertices` / `Slide Relax` in Sculpt mode).
- [ ] Does the outer eye corner wrap backward slightly along `Y` (`3/4` check)?
- [ ] Does the side profile show sclera poking past the eyelid rim? (Tuck sclera behind outer lid ridge).
- [ ] Are `UpperLip`, `LowerLip`, `MouthBox`, and `Face_Normals` stored as Vertex Groups?
- [ ] Did you check `Overlays -> Face Orientation` (all exterior faces blue, zero red inside-out lashes/strands)?
