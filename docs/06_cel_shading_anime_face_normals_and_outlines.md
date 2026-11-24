---
doc_id: cel-shading-anime-face-normals-and-outlines
title: Anime Cel Shading, Face Normal Editing, SDF Face Shadows, and Outline Engineering
topic: shading-normals-outlines
kind: practitioner-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate-advanced
tags: cel-shading, npr, eevee, shader-to-rgb, view-transform-standard, custom-normals, data-transfer, abnormal, sdf-face-shadow, solidify, inverted-hull, vertex-color, line-art, guilty-gear, genshin-impact, mtoon, light-linking
sources:
  - asw_guilty_gear_toonline_eng.md (79 slides, Junya C Motomura GDC/SIGGRAPH)
  - asw_guilty_gear_xrd_gdc_art_style (yhGjCzxJV3E)
  - guilty_gear_3d_look_2d_study (tWcaQ3gCbUU)
  - 2am_anime_face_explained_custom_shadows (uptuXWNWpk0)
  - 2am_perfect_anime_face_shadows (x-K6bCAl6Qs)
  - animexd_mastering_editing_normals (KB0B9Hz46UM)
  - 3dcinetv_normal_editing_anime_faces_101 (79XKQVAS9dI)
  - fondant_clean_normals_toon_addon (9JiewKzta7Y)
  - blender_secrets_inverted_hull_5_2 (dybTdt9WXts)
  - GTShader_Manual.md (GabrielToonShader) & bjayers_genshin_impact_shader
  - VRM_Addon_for_Blender/docs/en-us/material-mtoon/index.md & MToon 1.0 spec
  - Blender 5.3 Skill: blender-stylized-npr
---

# Anime Cel Shading, Face Normal Editing, SDF Face Shadows, and Outline Engineering

Raw physically based lighting, `AgX`, and unmodified face geometry normals immediately make any anime model look uncanny, plastic, and blotchy. Authentic 2D-looking 3D anime separates **shading color** from **real-world physics** and treats **vertex normals, SDF light maps, and outline geometry** as primary artistic controls.

---

## 1. Non-Negotiable Render & Color Pipeline Setup

1. **Render Engine**: Use **`BLENDER_EEVEE`** (note: in Blender 5.0+, `BLENDER_EEVEE_NEXT` was renamed back to `BLENDER_EEVEE`—Cycles cannot run `Shader to RGB`).
2. **Color Management (`View Transform`)**: Set **Render Properties → Color Management → View Transform = `Standard`** (`Look = None`, `Exposure = 0.0`). Never leave `AgX` or `Filmic` on for anime/NPR unless deliberately grading film plates—`AgX` desaturates bright skin, pastel hair, and crisp whites into muddy grey.
3. **Zero Unwanted World Bounce / GI Wash**:
   - In the World shader, split with `Light Path -> Is Camera Ray`: feed clean sky/backdrop color to **Camera Rays** and pure **`Black (0, 0, 0)`** (`Background` Strength `0`) to **Diffuse/Glossy indirect rays**. Otherwise GI washes out cel shadow contrast across clothes and skin.
4. **Separate Ground Drop Shadows from Self-Shadows (Guilty Gear Rule)**:
   - Unmodified self-shadows cast jagged shadow acne across stylized cheeks and locks of hair.
   - Disable noisy self-shadow casting per object/material (`Cast Shadows = OFF` on anime hair/face meshes or shadow terminator tuned), and if ground contact shadows are required, place a duplicate simplified proxy shadow caster (`Transparent BSDF` mixed off `Is Camera Ray`) or enable only Ground-receiving objects with **Light Linking** (Blender 4.0+/5.x).
5. **Per-Character Dedicated Key Light (`Light Linking`)**:
   - Guilty Gear gives every character an independent light direction tuned per shot/pose (one 3/4 rim-lit sun ruins another character standing at a different angle). Use Blender's **`Light Linking`** collections (or Goo Engine Material Light Groups) so hero key lights only affect their assigned character.

---

## 2. Blender 5.x Cel Shader Core (Shader to RGB + ILM + Hair/Rim)

### Basic 2-Band / 3-Band Toon Shader (EEVEE)
- **`Diffuse BSDF` (Roughness `0`) → `Shader to RGB` → `Map Range` / `ColorRamp` (`Constant` for hard Guilty Gear cut, or `Linear` with narrow `0.48 → 0.52` width to avoid jagged aliasing) → `Mix` (`ShaderNodeMix`, `data_type='RGBA'`)**.
  - *Blender 5.0+ Python API warning*: `ShaderNodeMixRGB` was removed in Blender 5.0. Always instantiate `ShaderNodeMix` (`data_type='RGBA'`), connecting `Factor` to index `0` and color inputs/outputs by name or typed socket indices (`A` = `6`, `B` = `7`, `Result` = `2`).
- **Hue-Shifted Shadow Palette (Mandatory)**:
  - Never multiply Base Color by pure gray (`0.5, 0.5, 0.5`). Multiply or tint shadow bands toward **warm peach/terracotta (`#E38C7B`) on skin** and **slightly cooler/purple-shifted darker hue on cloth/hair**, or author a dedicated Shadow Albedo texture / procedural HSV shift (`Hue ±0.03`, `Saturation +0.10`, `Value × 0.65`).
- **Guilty Gear / Genshin `ILM` Threshold Control**:
  - Instead of scalar `Threshold = 0.5`, compute `LitFactor = clamp(DiffuseBrightness + (ILM_G - 0.5) * Strength)`.
  - Areas painted **`ILM.G < 0.1`** stay permanently in dark shadow (neck crease, skirt interior, belt undersides); **`ILM.G > 0.5`** stay bright (cheek apex, collar highlight).
  - Add **Crisp Inner Lines** by multiplying final albedo by `ILM.A` (or a dedicated thresholded inner-line mask).
- **View-Dependent Rim Light & Genshin Warm SSS Edge**:
  - Rim mask: `(1 - max(dot(Normal, Incoming), 0)) ^ Power` thresholded via `smoothstep`, multiplied by `LitFactor` (or flipped shadow mask) so rim only sparks along lit or back-lit edges.
  - Warm skin/hair terminator line: sample a very thin band around the `0.48–0.51` shadow transition and add warm saturated orange-red (`SSS Tint`) right on the light-to-shadow terminator (`bjayers` / `GTShader`).
- **Anime Hair Angel-Ring Highlight**:
  - Combine a `Vector` / `Tangent` specular term offset vertically (`UV.y`) along verticalized hair UVs (`Follow Active Quads`), thresholded cleanly and modulated by a wavy crown-tooth noise texture (`Lightmap/Hair Specular Mask`).
- **Blender 5.3+ Native NPR Shader Nodes Note**:
  - Blender 5.3 introduces custom EEVEE lighting evaluation nodes (`Light Info`, `Light Evaluation`, `Shadow Raycast`, `Light Accumulation`) enabling multi-light cel evaluation + customized soft/stylized cast shadows natively without losing light color/passes.

---

## 3. Solving Anime Face Shadows: Three Production Methods

Raw geometry normals on an anime eye socket, nose pyramid, and cheek create ugly jagged shadows as soon as a light rotates (`3dcinetv`, `2AM`). Choose one of three battle-tested fixes depending on target engine and asset complexity:

| Method | Best Target | Pros | Trade-offs |
|---|---|---|---|
| **A. Proxy Sphere / Ellipsoid `Data Transfer`** | Blender/Unity/VRChat VTubers & fast 3D anime | Fastest (~2 min); keeps soft smooth round light wrap | Doesn't paint stylized anime nose wedge / cheek crescents unless paired with painted AO |
| **B. Manual Tilted Plane Vectors / `BNPR Abnormal`** | Guilty Gear style, Stylized film/cutscenes | Crisp, art-directed shadow shapes with exact snapping | Needs clean symmetric face quads; requires care during Shape Key deformation |
| **C. 7-Map **SDF Face Shadow** Node Math (Genshin / Star Rail)** | Modern mobile/PC anime games (`MToon` custom / Unity / UE / Blender EEVEE) | **100% artifact-free** at all 360° yaw angles, immune to facial mesh topology bumps, exports cleanly to any engine | Requires painting 1–2 progressive SDF gradients + light angle driver (`pi` normalized) |

### Method A: Proxy Sphere `Data Transfer` (with Modifier Stack Order Rule)
1. Create a smooth UV Sphere (or stretched Egg/Ellipsoid) positioned centered inside the head cavity, slightly forward of the nose tip; `Shade Smooth`. Hide from render (`Disable in Renders` & Viewport wireframe/bounds).
2. On the Head mesh: ensure `Smooth` shading is enabled and **Object Scale = `(1, 1, 1)`**.
3. Create a Vertex Group (`G_FaceNormals` = `1.0` on face skin, tapering down to `0.0` around ears/neck collar seam, **`0.0` on interior mouth bag & nostrils**).
4. Add **`Data Transfer`** modifier:
   - `Source` = Proxy Ellipsoid, `Vertex Group` = `G_FaceNormals`.
   - Enable **`Face Corner Data` → `Custom Normals`** (`Mapping = Nearest Corner and Best Matching Normal` or `Nearest Face Interpolated`).
   - Optionally place modifier **above** `Armature` ONLY if you immediately **Apply `Data Transfer`** so custom split normals bake into mesh corners BEFORE `Armature`/ShapeKeys deform them (`Animexd` rule: baked custom split normals rotate naturally with `Head` bone matrices, OR use a separate undeformed non-shape-key proxy driven identically). Leaving unapplied world-space `Data Transfer` pointing to a static sphere *after* head rotation causes shadows to swim! Parent the proxy sphere to the `DEF-spine.006` / `Head` bone if kept live.
   - *Fondant / Triangulated Mesh Tip*: If irregular quads/tris still cause stepped shading ripples, pre-smooth face normals with Laplacian smoothing / inverted-area weighting (`Abnormal` or Geometry Nodes blur along normals—avoiding raw vertex-position blur).

### Method B: `2AM` / `BNPR Abnormal` Tilted Plane Vector Copy
1. Enable Blender **Edit Mode → Mesh → Normals → `Copy Vectors` / `Paste Vectors`** (or open **`BNPR Abnormal`** `3D View N-panel → Abnormal`).
2. Add two helper planes in front of the character face:
   - Plane A tilted slightly **downward (`~15°`)** and outward (`~20°`) on `+X` for cheek/temple shadow wrapping.
   - Flatten face forehead/cheek/upper-lip normals toward Plane A's copied normal vector (`Paste Vectors`), while copying front/up-facing vectors for the nose wedge highlight (`2AM` / `3dcinetv`).
3. Because split custom normals bake into the `.fbx`/`.glb`/`.vrm`, zero runtime shader complexity is needed in Unity/UE/VRM!

### Method C: 2AM / Hoyoverse SDF Face Shadow Map & Exact Math
1. Author an **SDF Face Shadow Threshold Map** (`Non-Color` grayscale texture):
   - Paint sequential shadow contour frames from `0°` front-lit (mostly white `1.0`) to `90°` side-lit (half mask at `0.5`) to `180°` back-lit (dark `0.0` except cheek rim sliver), blended smoothly (`2AM` method: paint 7 key shadow shapes in Krita/GIMP at `1/7` opacity steps or generate Signed Distance Field contour interpolation across frames).
2. Because this map encodes only **left-side (`+X`) shadow progression**, sample it once with `UV.x` (normal) and once with `1 - UV.x` (mirrored horizontal flip `Texture Coordinate -> Separate XYZ -> 1 - X -> Combine XYZ`)!
3. **Normalized Light-Angle Driver Setup (`pi` Formula)**:
   - Connect your Sun / Key Light's world rotation `Z` (`var`) and Character Head's world/pose rotation `Z` (`head_rot_z`) via a scripted expression driver on a shader Value node:
     $$\text{SignedAngle} = \text{atan2}\left(\sin(\theta_{\text{light}} - \theta_{\text{head}}),\; \cos(\theta_{\text{light}} - \theta_{\text{head}})\right) / \pi$$
   - (More general than naive `(-var + head_rot_z) / pi`, because `atan2(sin, cos)/pi` **wraps cleanly `[-1, +1]`** past $\pm 180°$ without snapping when the character turns full circles!)
   - **Selecting Left vs. Right Sample**:
     - If `SignedAngle >= 0` (light on Right side): compare `SDF_Sample >= abs(SignedAngle)`? Flip sign/direction to match your UV `X` handedness (`Greater Than` `MapRange(SignedAngle -> [0, 1])`).
     - Specifically: `FaceLitMask = mix(SDF_Left, SDF_Right, GreaterThan(SignedAngle, 0.0)) > (1.0 - abs(SignedAngle))` (or invert cleanly depending on whether white=`1` means lit earlier or shadowed earlier—always verify in EEVEE viewport with light rotating `360°`!).
   - Feed that sharp `0/1` boolean mask **instead of `Diffuse BSDF`**, bypassing real face normals entirely! Result: **zero nose geometry wobble** at every camera and light angle.

---

## 4. Inverted Hull (`Solidify`) Outlines & Arc System Works Vertex Color Control

### Clean `Solidify` Outline Setup (EEVEE + Cycles Blender 5.2+)
1. Add material slot 2: **`M_Outline`**. Enable **`Backface Culling`** in Material Settings (`Surface` viewport + EEVEE settings).
   - **EEVEE-only simple node**: `Emission` (`Dark Tinted Outline Color`, never pure pitch black—use deep dark maroon/navy/charcoal matched to palette!) → `Material Output`.
   - **Cycles + EEVEE cross-compatible setup (`Blender Secrets 5.2+`)**:
     1. `Emission` + `Transparent BSDF` → `Mix Shader 1` (`Factor = Geometry -> Backfacing`).
     2. `Transparent BSDF` (Top input!) + `Mix Shader 1` (Bottom input!) → `Mix Shader 2` (`Factor = Light Path -> Is Camera Ray`, or **`Light Path -> Ray Length`** so outlines still appear in mirrors/glass reflections!).
     3. Verify **`Transparent Shadows`** is enabled in material/object settings so the outer backface shell doesn't cast a solid black blob shadow inside Cycles.
2. Add **`Solidify` Modifier**:
   - `Thickness` = negative (`-0.002` to `-0.006` m for ~1.6 m characters; `-1` offset moves faces outward cleanly if `Normals -> Flip` is active—verify direction!).
   - **`Offset = -1.0`** (or `+1.0` depending on `Flip` polarity—check **Face Orientation** overlay: hull faces pointing *away* from camera must render **Blue** inside/backside and **Red** outside facing camera when overlay is ON so backface culling hides front-facing hull!).
   - **`Normals → Flip = ON`**, **`Normals → High Quality = ON`**, **`Thickness Mode = Simple`** (keep `Even Thickness` checked or unchecked carefully—`Even Thickness` spikes sharp hairline corners unless **`Clamp`** is set `> 0.0` or corner weights are reduced!).
   - **`Materials → Material Offset = 1`** (assigns slot `+1` `M_Outline`).

### Fixing Split / Broken Outlines & Arc System Works Contour Rules (`79 Slides`)
1. **Why Outlines Gap on Hard Edges (`Sharp` Splits)**:
   - `Solidify` extrudes along vertex normals. Any **split normal** (hard box edge, mirror seam unmerged, UV boundary with split vertices) extrudes two faces in different directions, tearing a visible white hole at the silhouette!
   - **Fix**: Keep the mesh **100% welded (`Merge by Distance` = `0.0001 m`)** with smooth unified normals for the outline pass, OR duplicate/generate a smoothed-normal outline helper shell (`Normal Smoothing`) while keeping crisp custom/split normals on the primary shaded mesh!
2. **Per-Region Thickness Weighting (`Vertex Group` / ArcSys `RGBA` Vertex Colors)**:
   - Uniform thickness makes fingers, eyelashes, nose bridges, and nostrils look bloated and blobby.
   - **Blender Solidify**: Assign **`Vertex Group` (`VG_OutlineWidth`)** (`0.0` inside inner eye sockets, lip line, nostrils, armpit crevices, inner ear; `0.3` fingers/face chin; `1.0` outer coat/hair silhouette). Enable `Fill` / `Factor` carefully.
   - **Guilty Gear / Custom Shader (`RGBA` Vertex Color Spec, Motomura 79 Slides)**:
     - **`R` (Red)**: `Shadow / Ambient Occlusion Bias` (paints always-dark regions directly on verts without texture resolution limits).
     - **`G` (Green)**: **Camera-Distance Thickness Scaling Bias** (`0.0` in tight finger creases/under-chin/wrinkle valleys = **"Close the gap"** -> line pinches cleanly to `0 px` and disappears; `0.5` standard limbs; `1.0` heroic outer shoulder/coat).
     - **`B` (Blue)**: `Base Contour Offset Scale` (modulates initial extrusion thickness).
     - **`A` (Alpha)**: **`Z-Offset / Depth Bias`** (`Push back along camera view vector` on overlapping bangs, noses, eyelids so front bangs outlines don't poke *over* eyes—or push line hull slightly deeper behind foreground geometry!).
   - **Camera-Distance + FOV Compensation (Game Shaders / Geometry Nodes)**:
     - Extrude outline by $w = w_{\text{base}} \cdot \text{clamp}(\text{dist} \cdot \tan(\text{FOV}/2),\; d_{\min},\; d_{\max}) \cdot \text{VG}_{\text{width}}$ so outlines stay `1–2 px` crisp on close-ups AND remain readable in wide full-body shots instead of disappearing into 0px shimmer or swelling into black blobs.

### Grease Pencil `Line Art` (For Blender Renders, Turntables & 2D Compositing)
- **Important Engine Rule**: **Blender `Line Art` (Grease Pencil modifier) renders inside Blender Cycles/EEVEE ONLY**—it does **not** export to `.fbx`, `.glb`, or `.vrm` game engines (use Inverted Hull + Inner Texture Lines for engines).
- In Blender 4.3+/5.x (note: Python type is `GreasePencil`, old `GreasePencilv3` was removed in 5.0):
  - Set `Stroke Thickness` to **`Screen Space`** (consistent pixel width relative to frame resolution), enable `Occlusion` levels cleanly (`0` = visible outer/crease lines), toggle `Silhouette` + `Crease` (`140°` threshold) + `Material Borders` + **`Edge Marks`** (mark exact anime chin/clavicle/collar crease lines in Edit Mode!).
  - Never animate heavy noisy intersections without stabilizing `Light/Camera` chaining (`Chaining -> Geometry Space` / `Image Space` tuning + `Multiframe` cleanup for hero close-ups).
