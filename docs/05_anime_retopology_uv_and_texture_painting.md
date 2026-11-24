---
doc_id: anime-retopology-uv-and-texture-painting
title: Anime Retopology, Stylized UV Layout, and Hand-Painted / Game Texture Packing
topic: retopology-uv-texturing
kind: practitioner-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate
tags: retopology, shrinkwrap, f2, looptools, quadriflow, uv-unwrap, follow-active-quads, mio3uv, ucupaint, ilm-map, vertex-color, texture-painting, texel-density, vectorizing
sources:
  - dikko_modeling_for_animation_06_face_retopo (SwM19PgSdCM)
  - vertex_arcade_retopologize_stylized (0aPr51sDkxE)
  - maoly_face_retopology_no_addon (rvDf6ZuEynM)
  - facepalme_texture_anime_head (ATClZK6W5a8)
  - astonished_gacha_anime_hair_ucupaint (HGKYUWI44lQ)
  - pyrodev_handpainting_anime_texture (gOvm7XuI9Qo)
  - bjayers_genshin_impact_shader / GTShader_Manual.md
  - 80lv_complete_head_retopology_workflow
  - Blender 5.3 Skill: blender-retopology-uv & blender-texturing
---

# Anime Retopology, Stylized UV Layout, and Hand-Painted / Game Texture Packing

Photorealistic auto-retopology and uniform Ptex/UDIM UV packing break anime characters. Anime hero heads depend on clean facial rings for shape-key blinking and lip-sync, while cel-shaded textures need **2× texel density on the face and eyes** and straightened **rectangular/square UV strips** for vector-sharp stripes, trims, and Guilty Gear-style inner linework.

---

## 1. When to Use Manual vs. Auto Retopology

| Method | Best Use Case | Veteran Rule |
|---|---|---|
| **Manual Snap Retopo** | Hero anime face, eyes, mouth, knees, elbows, fingers, bending joints | Mandatory for any region driven by **Shape Keys** or extreme IK limb bends |
| **`Quadriflow` Remesh** | Static stylized props, sculpt blockout smoothing, stiff armor plates | Always Voxel-Remesh manifold first; destroys UVs; **never use on anime hero heads** because edge loops spiral around eyes/mouth and break blink shape keys |
| **`Decimate` (Collapse/Planar)** | Hair LODs, distant background NPCs, flat hard-surface trims (`Planar`) | Keeps existing UVs/shapes; clean up pole triangles on bending seams afterward |

### Why Quadriflow Fails on Anime Heads
- `Quadriflow` creates diagonal diamond flow across eyelids and mouth corners, producing jagged "zipper" pinching when `eyeBlinkLeft`/`eyeBlinkRight` or `aa`/`oh` Shape Keys pull verts shut.
- Anime heads require **exact matching upper/lower eyelid and lip vertex counts** across the 4 facial quadrants (upper/lower, left/right).

---

## 2. Manual Retopology Setup in Blender 4.2 / 5.2+

### Viewport & Modifier Stack (No Paid Add-ons Needed)
1. **High-poly / Sculpt target**: Disable editing/selection in Outliner (`Selectable` off), optionally set a distinct Viewport Display Color.
2. **Low-poly retopo object**:
   - Origin at world `(0, 0, 0)`.
   - Add **Mirror Modifier** (`X` axis, **`Clipping = ON`**). Work strictly on half the head/body until neck merge.
   - Add **Shrinkwrap Modifier** (`Wrap Method = Project` or `Nearest Surface Point`, `Snap Mode = On Surface` / `Above Surface` during editing, target = sculpt).
   - Turn on **Object Properties → Viewport Display → `In Front`** so faces do not bury beneath the sculpt.
3. **Snapping & Built-in Helpers**:
   - Enable Snap (`Magnet`), Snap Target = **`Face Project`**, check **`Align Rotation to Target` = OFF** for organic quads, toggle **`Project Individual Elements`**.
   - Enable built-in **`Mesh: F2`** (1-vertex quad extrusion) and **`LoopTools`** (built in cleanly in 5.2+/5.3 for `Relax` and `Space`).
   - Use **`Poly Build`** tool for rapid quad dragging, or **`Annotate`** tool (Vertex Arcade / Maoly workflow) to draw target loop lines onto the sculpt skin first.
   - Use Sculpt Mode **`Slide Relax`** brush (`Shift` to relax) with Wireframe overlay ON to equalize quad spacing without pulling vertices off the sculpt surface.

### Facial Loop & Star-Pole Blueprint (Dikko + Maoly + 80.lv Rules)
- **5 Essential Loops** (block these first before filling cheeks/forehead):
  1. **Eye Orbitals**: Start with **6–8 spans upper eyelid = 6–8 spans lower eyelid** (equal quad count top and bottom!). Extrude 2–3 concentric rings outward.
  2. **Raccoon Mask Loop**: Connects the two eye rings cleanly across the nose bridge with **zero 3/5-edge star poles on the centerline** (`X = 0` must remain an uninterrupted edge loop!).
  3. **Nose-to-Chin (Nasolabial) Loop**: Flows from nose bridge/wing down past the mouth corner around the chin.
  4. **Mouth / Lip Orbitals**: Equal spans upper lip = lower lip, nested inside the nasolabial loop. Extrude inward 3–4 loops to form a closed **mouth bag** behind the teeth/tongue slot.
  5. **Jawline-to-Forehead Frame**: Anchors the silhouette edge of the anime cheek and separates cheek shading plane from jaw underside.
- **Keep 5-Edge Star Poles (`E-poles`) Off Deforming Creases**:
  - Place the 5 facial direction-change poles on stiff landmarks: nose-bridge corner, outer orbital corner, cheekbone crest, nose-wing/cheek junction, and mid-cheek transition.
- **Neck & Crown Edge Reduction**:
  - Place any **3→1 quad reductions** on the top of the scalp (under hair) and **back of the neck**, never across the front throat or cheeks.
- **Ear Retopology Trick (Maoly)**:
  - Duplicate (`Shift+D -> P`) the perimeter loop around the ear hole into a separate helper object, build the stylized ear cleanly in isolation (since Shrinkwrap fights recessed ear folds), then `Ctrl+J` join and `Merge by Distance` back into the head.
- **Subdivision Creases (`Shift+E`)**:
  - Set `Mean Crease = 1.0` selectively only if keeping live Subsurf on stylized eyelid/lip/nostril cuts, and **apply Subsurf cleanly** before authoring facial Shape Keys or UV packing.

---

## 3. Two Proven UV Strategies for 3D Anime Characters

Unlike PBR realism where texel density is locked globally (`512 px/m`), anime art styles intentionally **bias UV real estate** toward the camera focal zones and square off islands for razor-sharp line art.

### Strategy A: Standard Non-Uniform Anime Atlas (Genshin / Vtuber / VRM Style)
Best for modern cel-shaded game characters and VTubers (`Mio3UV` or Blender native UV tools):
1. **Priority Scale Hierarchy**:
   - **Eyes & Face (`2×` to `3×` density)**: Occupy the largest islands so iris highlights, lashes, blush gradients, and lip corners never pixelate on close-ups.
   - **Hair Front & Silhouette Clothes (`1×`–`1.5×`)**: Rectangularized strand strips (`Follow Active Quads`) so painted hair shine/anisotropic rings run straight horizontally across all strands at once.
   - **Body Skin under clothes, Socks, Back-side Undersides (`0.25×`–`0.5×`)**: Smallest islands, or dark solid swatch corners for interior/shadow-only shells (like `astonished_gacha` separating underside hair tips into a tiny dark shadow UV zone).
2. **Material Slot Consolidation (`1` to `4` Materials Max)**:
   - Keep draw calls low for Unity/Unreal/VRChat/Roblox: `M_Face`, `M_Eye` (optional emissive/refraction), `M_Hair`, `M_Body_Clothes`.
   - When mirroring symmetrical left/right parts (arms, boots, socks) to save UV space: move duplicate right-side UV islands **exactly `+1.0` in U** before baking AO/Curvature/Normal maps so bake rays do not double-burn dark seams, then shift back or keep at `+1.0` (engines tile `0–1`).
   - **Face Mirroring Workflow (Facepalme)**: Unwrap half the face with **`Project From View`** on `Numpad 1` (Front), run **`Minimize Stretch`**, align the center spine vertices to `X = 0.5` (`Align Vertical` -> set `X = 0.5`), set `2D Cursor` to `(0.5, 0.5)` and Pivot = `2D Cursor`, then after applying Mirror modifier select the opposite half (`UV Sync Selection = OFF`) and scale **`S X -1`** over the UV spine—or keep face unmirrored if using asymmetric freckles/scars/hair shadow!

### Strategy B: Square UV + Inner Line "Vectorizing" (Guilty Gear / Cel-Sharp Workflow)
- **Follow Active Quads (`U -> Follow Active Quads`)**: Align one quad's edges horizontally/vertically (`Align X/Align Y` or `S X 0`/`S Y 0`), make it the **active face**, select the island (`L`), and run `Follow Active Quads`.
- **UV Vectorizing (Facepalme / Guilty Gear)**:
  - On straight anime eyebrows, collars, trim stripes, or Guilty Gear inner pencil lines, align straight UV borders flush against solid color boundaries or black/white edges in the texture.
  - Even on a compact `1024px` map, aligned UV edges sample cleanly along straight pixel axes, producing **razor-sharp, anti-aliased linework** with zero brush wobble!
  - If a diagonal quad edge bends a stripe awkwardly, swap its triangulation direction (cut the opposing diagonal with Knife `K` and dissolve the old diagonal, or rotate edge CW/CCW).
- **UV2 (`Decal_UV`) for Chest Emblems / Logos**:
  - Add a second UV map (`UVMap_Decal`) strictly for sharp logos, numbers, or high-res crests blended over a low-res tiled fabric Base Color, avoiding inflating the main body texture to 4K.

### Game Margin & Export Rules
- Set island pack margins in **pixels relative to texture size**: `4 px` at 1024, `8 px` at 2048, `16 px` at 4096 (eliminates mipmap bleeding at distance).
- Every **hard edge (`sharp_edge > 60°`)** used in baking **must** be split on a **UV seam**.
- **UV Overlap & Engine Checks**:
  - **VRM / Unity / Unreal / Roblox**: UV coordinates must fit inside `[0, 1]` (or intentional tiled offsets without unwanted cross-material bleed). **No zero-area UV faces** (`area == 0` causes corrupt tangents in MikkTSpace and NaN shader black spots!).
  - **UDIM Tiles (`1001`, `1002`)**: Excellent while painting multi-part hero hair cleanly inside Blender **Ucupaint** (`astonished_gacha` workflow), **but bake/repack back onto standard 0–1 UV atlases before exporting to Unity, Godot, VRChat, or Roblox**, because real-time mobile/web/VR engines rarely read Blender UDIM naming natively without custom Virtual Texturing.
- **Blender 5.0+ Python Gotcha**:
  - `BMLoopUV.select` was removed in Blender 5.0; UV selection in `bpy`/`bmesh` is shared across UV maps via mesh `.uv_select_*` attributes (`mesh.uv_layers[name].uv` + `mesh.uv_select_vert` / `uv_select_loop`).

---

## 4. Texture Painting & Anime Game Map Packing

### Non-Destructive Layer Painting inside Blender (`Ucupaint` / Native) vs External Tools
Whether using free open-source **`Ucupaint`** (recommended Blender layer painter), **Krita**, **GIMP**, **Clip Studio Paint**, or **Substance 3D Painter**:
1. **Lock a Disciplined Palette First (`Shift+X` Eyedropper)**:
   - Sample exact **Base Color**, **1st Shadow Color** (hue-shifted slightly cooler/warmer, slightly higher saturation, lower value—**never pure gray/black**!), **Rim/SSS Tint**, and **Dark Line/Crease Color** (warm dark brown `#3B2420` for skin, tinted dark variant of clothing hue for fabric).
2. **Layer Order for Anime Base Color (Albedo)**:
   - **Base Fill** -> **3D Position / Vertical Gradient** (subtle darker lower hem/socks, brighter upper chest/face focus; inverse subtly darkens lower scalp/neck underside) -> **Baked Soft AO / Occlusion Shadow** (collar shadow onto clavicle, skirt shadow onto thighs, bangs shadow hint onto forehead) -> **Hard Cast Crease Shadows** (drape valleys, armpit, inner ear) -> **Inner Crease Line Art** (0.04–0.15 relative brush width; thicker on major silhouette separations like belt-over-tunic) -> **Face Blush & Eye Specular Sparkles**.
3. **UV / Face-Mask Isolation**:
   - In `Edit Mode`, select underside/interior shells (inner hair locks, inside of skirt, under chin), switch to `Texture Paint` and toggle **Paint Mask (`Face Selection Masking`)**, then flood-fill the shadow tone cleanly without bleeding onto visible front locks.
4. **Keep Albedo Brightness Game-Safe**:
   - Avoid pure `1.0, 1.0, 1.0` white (`> 0.85` clips under directional + rim lights) and avoid pure `0.0, 0.0, 0.0` black (`< 0.04` kills cel shade bands and detail).

### Genshin / Guilty Gear `ILM` & Channel-Packed Mask Standard
Modern anime shaders (`GTShader`, Hoyoverse-style, Guilty Gear Xrd/Strive) avoid blurry photoreal PBR maps and instead pack four strict stylization masks into one **Non-Color** RGBA texture (`*_ILM.png`):

| Channel | Encoding / Meaning | How Authors Paint It |
|---|---|---|
| **`R` (Red)** | **Specular Intensity / Mask** | `0.0` matte cloth/skin, `0.3` hair sheen, `0.8–1.0` leather/metal armor |
| **`G` (Green)** | **Painted Shadow / AO Bias** | `< 0.1` always-in-shadow crevices; `< 0.25` darkened fold pockets; `0.5` neutral default lit response; `> 0.5` biased to stay lit (nose tip, forehead, cheeks) |
| **`B` (Blue)** | **Specular Gloss / Rim Width / Material ID Ramp** | Controls tight shiny highlight vs wide cloth sheen, or quantized ramp row index |
| **`A` (Alpha)** | **Crisp Inner Lines** | Black `0.0` etched pencil lines along folds, mechanical seams, button borders; white `1.0` everywhere else (no blurry anti-alias halo if vectorized along Straight UVs!) |

### Mandatory Color Space Checklist
- `Base Color` / `SSS Ramp` / `Shadow Color` / `Emission`: **`sRGB`**
- `ILM` / `LightMap` / `SDF Face Shadow` / `Outline Vertex Mask` / `Normal` / `Roughness` / `Metallic`: **`Non-Color`** (setting `sRGB` on an ILM or SDF map applies a `2.2` gamma curve and shifts every cel shadow threshold!).
- Save clean baked textures relative (`//textures/...png`) and avoid shipping unbaked procedural-only Ucupaint stacks to `.fbx`/`.glb`/`.vrm`.
