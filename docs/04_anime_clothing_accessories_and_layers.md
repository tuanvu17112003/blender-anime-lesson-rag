---
doc_id: anime-clothing-accessories-and-layers
title: Anime Clothing, Seifuku Pleated Skirts, Accessories & Weight Transfer
topic: modeling-clothing
kind: modeling-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate
tags: anime-clothing, seifuku, skirt, pleats, cloth-sim, solidify, shrinkwrap, data-transfer, mask-modifier, poke-through, skirt-rigging, 2am, kana-fuyuko, codernunk
sources:
  - CoderNunk — Modeling Clothing and Accessories (codernunk.com)
  - 2AM — How to Rig EVERYTHING (Clothes, Skirt, Chains, Straps) (blgGcbZzsWM)
  - Kana Fuyuko — How To Rig Dresses And Skirts Using Blender (cGcBfhYyjC8)
  - Pierrick Picaut — Skirt and dress Rigging & Dynamic Cloth (55bJB5Wmd_U, kCn4sProaek)
  - Blender Clothing Skill & Official Solidify/Data Transfer Manuals
---

# Anime Clothing, Seifuku Pleated Skirts, Accessories & Weight Transfer

Anime outfits (pleated `seifuku` skirts, sailor collars, flowing ribbons, oversized sleeves, layered jackets) frequently break during rigging when AI agents shrinkwrap overlapping meshes haphazardly, forget to remove leg weights from skirts, or leave occluded body skin poking through joints.

## 1. Three Proven Ways to Model Anime Garments

| Garment Type | Recommended Technique | Key Rules |
|---|---|---|
| **Skin-tight** (bodysuit, tights, thigh-high socks, gloves) | **Model/Texture directly on Base Body** (`Hoyoverse` method, `SunnyIsOnline`) | Zero extra draw calls, zero poke-through! Add a tiny seam ridge (`Solidify` ring or edge extrude) only at the sock/glove cuff. |
| **Fitted** (`seifuku` blouse, sweater, pants, vest) | **Duplicate Base Body Region (`Shift+D -> P`)** (`CoderNunk`, `Natsumori Katsu`) | Inflate outward `5–15 mm` (`Alt+S`), bridge across sternum cleavage (`delete tight chest crease`), **align garment elbow/shoulder/knee loops directly over the body's joint loops** so both bend identically! |
| **Loose / Flowing** (pleated skirt, cape, oversized sleeves, coat tails, ribbons) | **Cylinder/Loop Modeling + Creased Pleats OR Cloth-Sim Drape Bake** | Model/simulate in rest pose -> **bake/convert cloth sim to static mesh BEFORE rigging** -> add `Solidify` rim thickness AFTER cloth settle -> rig with bone chains! |

---

## 2. Step-by-Step Garment Recipes

### Fitted Blouse, Jacket & Sleeves
1. Back up `SK_Body` into a hidden backup collection first.
2. In X-Ray Edit Mode, select body faces from collarbone/neck down to waist/sleeves (`leave 1 loop ring extending beyond sleeves/collar`).
3. `Shift+D` -> right-click cancel move -> `P -> Separate Selection`.
4. **Fix Chest/Underarm Tension**: Remove deep cleavage crease between breasts (`dissolve inner sternum edge, bridge smoothly across front`) and use Sculpt `Inflate` + `Grab` (`5–10 mm` ease for shirts, `10–20 mm` for jackets).
5. **Cuffs & Collars Thickness**: Instead of full heavy inner geometry, add thickness only to visible rims—either extrude cuff/collar edge inward `1–2 loops` (`creates solid shadow lip with 90% fewer tris than full Solidify!`) or use `Solidify` (`Thickness = 0.002–0.005 m`, `Offset = 1`, `Rim Fill = True`) and delete unseen interior backfaces afterward!

### Pleated Anime Skirt (`Seifuku`)
- **Method A — Crisp Geometric Pleats (Best for Stylized Anime)**:
  1. Start with a `24–36` vert Circle (or `N`-pleat repeating wedge with `Array` + `Simple Deform Bend 360°`, then `Merge by Distance`).
  2. Select alternating vertical edges around the skirt and scale outward slightly (or offset on normals) to form crisp Z-fold pleats (`12–18` pleats total).
  3. Mark **outer & inner pleat creases sharp** (`Shift+E` crease for Subdiv, or bevel lightly) so cel-shaded light catches crisp anime fold edges!
  4. Keep the **waistband tight (`Shrinkwrap` to torso waist)** and flare the hem outward (`A-line cone`) so thighs have room to step forward without instant clipping.
- **Method B — Soft Draped Skirt (`CoderNunk`)**:
  1. Pin top waistband edge loop (`Vertex Group = Pin_Waist`).
  2. Add `Cloth` physics (`Silk` preset, `Quality = 8`, `Object Collisions` enabled on body `3 mm` margin).
  3. Play timeline `30–50` frames until natural gravity folds appear -> `Object -> Convert -> Mesh` (bakes drape!) -> cut in half & re-add `Mirror` if symmetrical.

### Belts, Sashes, Ribbons & Armor Plates
- **Belts/Sashes**: Extract waist loops -> `Shrinkwrap` modifier (`Nearest Surface Point`, `Snap Mode = Outside Surface`, `Offset = 0.003–0.008 m`) -> Apply Shrinkwrap -> add `Solidify` (`0.003–0.006 m`).
- **Sailor Collar, Bows & Ties**: Model flat symmetrically at world center, `Solidify` (`Offset = 0` or `1`, `Even Thickness`), tuck knot tightly against collar, and weight **`100%` to `Chest/UpperChest` (knot) + dedicated `Tie`/`Ribbon` bone chains (hanging tails)**.
- **Rigid Badges / Armor / Hairpins / Buckles**: Never blend across spine/arm bones—weight **`100%` (`1.0`) to a single parent bone** so hard props never stretch like jelly!

---

## 3. Hiding Covered Body Geometry (Preventing Poke-Through & Saving Tris)

1. **Single-Outfit Game / Animation Model**:
   - Once garments are finalized, select all body faces completely covered beneath opaque shirts, pants, and boots—**EXCEPT keep `1–2` face rings extending inside collars, sleeve cuffs, skirt hems, and boot tops** so oblique camera angles never expose empty gaps (`CoderNunk`, `blender-clothing`)!
   - Delete the hidden interior skin faces (`saves 30–50% triangle count and permanently eliminates elbow/ribcage poke-through`).
2. **Modular / Swappable Outfits**:
   - Do NOT delete body faces permanently; instead assign covered faces (shrunk by 1 ring from borders) to `Hidden_<Outfit>` Vertex Group and add an inverted **`Mask` modifier** on `SK_Body`. Toggle per outfit!

---

## 4. Garment Skinning & Skirt Weight-Painting Rules (CRITICAL!)

Never rely on raw `Automatic Weights` for layered anime outfits! Follow the exact **2AM (`blgGcbZzsWM`) + Kana Fuyuko (`cGcBfhYyjC8`)** workflow:

1. **Transfer Body Weights to Fitted Clothes**:
   - Parent garment to armature **`With Empty Groups`** (`Ctrl+P`).
   - Add **`Data Transfer`** modifier on the garment **ABOVE the `Armature` modifier**:
     - `Source = SK_Body`
     - Enable `Vertex Data -> Vertex Groups`
     - `Mapping = Nearest Face Interpolated` (or `Projected Face Interpolated`)
     - Click **`Generate Data Layers`** (essential—otherwise empty vertex groups receive nothing!)
     - **Apply** the `Data Transfer` modifier!
2. **Fix Skirt & Dress Weights (The #1 Rigging Trap!)**:
   - If you transferred weights from the body (or ran Automatic Weights near the hips), the **legs/thighs (`DEF-thigh.L/.R`) grab the skirt mesh**—making the front hem stretch like rubber chewing gum between the knees!
   - **Exact Fix (`Kana Fuyuko`)**:
     1. In Weight Paint / Edit Mode on the skirt, **remove 100% of `thigh`/`shin`/`foot` weights** from the skirt! (Or lock skirt chain groups and clear leg influences.)
     2. Build **`6–12` radial `4`-bone chains** around the skirt (`Skirt_F`, `Skirt_FL.L`, `Skirt_L.L`, `Skirt_BL.L`, `Skirt_B`, mirrored via `.L/.R` + `Symmetrize`).
     3. Parent all skirt root bones to **`Pelvis` / `Hips` (`Keep Offset`)**.
     4. Weight paint the skirt ONLY to `Pelvis` (top waistband) + the radial skirt chains (`smooth vertical gradient down each pleat column + smooth horizontal overlap between adjacent chains`).
     5. **2AM's Anti-Upskirt Physics Trick**: When binding skirt chains to `VRM SpringBone` or `Wiggle 2`, start the dynamic spring root at the **2nd or 3rd bone link** down from the waist (keeping the top `1–2` rings rigidly parented to `Pelvis`/`Hips`). This hugs the hips cleanly while letting the lower pleats sway!
3. **Stress-Test Poses**: Pose arms overhead (`140°`), kick leg forward (`90°`), and sit (`90°` hip bend). Check for underarm/thigh poke-through and smooth weights (`Weights -> Smooth` + `Normalize All`).
