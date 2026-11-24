---
doc_id: anime-body-topology-and-proportions
title: Anime Body Topology, Joints, Hands, Feet & Pose Standards
topic: modeling-body-topology
kind: modeling-guide
blender_version: 4.2 LTS / 5.2 LTS / 5.3
difficulty: intermediate
tags: body-topology, t-pose, a-pose, elbow, knee, shoulder, hand, fingers, feet, torso, dikko, chaosy3d, natsumori-katsu, codernunk
sources:
  - Chaosy3D — CREATE an ANIME GIRL BODY in Blender (yg8Snn3OzLc)
  - Dikko — Modeling For Animation Series (01WQlMD7dsk, QboreU0cRjY, GxMz4HylQfU, 8R0e0qh5wiU)
  - Summer / Natsumori Katsu — CGWORLD Blender Fes (Sy7RHtco43Y)
  - CoderNunk — Complete 3D Game Character Creation Guide (codernunk.com)
  - Noggi — EVERYTHING About Creating Beautiful 3D Anime (xZWxEoa-Dwk)
  - VRM 1.0 Specification — Humanoid Pose Rules (vrm.dev)
---

# Anime Body Topology, Joints, Hands, Feet & Pose Standards

A 3D anime body looks effortless in still renders until you bend an arm or leg—at which point poor joint topology collapses like a crushed soda can, shoulders cave in, and fingers look like bent sausages.

## 1. T-Pose vs A-Pose: Which Should You Model In?

| Bind Pose | Advantages | Drawbacks | Best Used For |
|---|---|---|---|
| **T-Pose** (arms horizontal `0°`, palms facing down `-Z`) | World-axis aligned hands/arms; fast mirroring; **required/preferred by VRM 0.x/1.0 & Mixamo**, easiest Unity Humanoid bone auto-mapping | Deltoid/armpit stretches more when arms hang down at rest (`~75°` drop from bind pose!) | **VRM / VRChat avatars**, Mixamo prototypes, quick low-poly game rigs (`Natsumori Katsu`, `VRM spec`) |
| **A-Pose** (`30–45°` arm slope down, slight natural elbow bend back & knee bend forward) | Midpoint between arm-down idle and arm-up combat -> **vastly cleaner shoulder/armpit deformation**, better garment/sleeve draping | Slightly trickier finger alignment (model hand flat in separate/world axes, then rotate & join to wrist!) | **Action RPGs, fighting games, animation shorts, Unreal/Godot/Blender hero rigs** (`Chaosy3D`, `Dikko`, `blender-character-rigging`) |

> **Pro Tip (`Chaosy3D`)**: Even if building an A-Pose body, model the hand **flat aligned to world XYZ** first, then rotate and bridge it onto the angled wrist—never try to extrude crooked diagonal fingers directly in world space!

---

## 2. Torso, Neck & Shoulder Deformation Loops

1. **Neck -> Clavicle -> Chest**:
   - Start neck at `12–20` vertices (even count divisible by 4, e.g., `16` or `20`, matching head base).
   - Tilt the ribcage slightly backward (`~10°`) and pelvis slightly forward (`~10°`) in side profile—human torsos are NOT vertical cylinders (`Natsumori Katsu`).
   - Place a dedicated **collarbone / trapezius loop** wrapping over the shoulder top to the sternum pit.
2. **Shoulder / Armpit (High-Stress Zone!)**:
   - Create an **`16–18` vertex** armhole loop (`Chaosy3D`).
   - Ensure concentric **deltoid/shoulder-cap loops** wrap *over* the shoulder rather than dead-ending vertically into the torso.
   - Keep **extra edge loops on the top/outer deltoid** and slightly fewer tucked neatly under the armpit so raising the arm overhead doesn't pinch or pull the chest inward.
3. **Breasts & Stylized Chest**:
   - Extract/inset a circular `12–20` vert loop on the pectoral area, extrude `2–3` rings outward to bust apex, merge tip cleanly at center (or clean quad cap), and add a soft lower crease (`Shift+E` gentle or shaped edge) curving toward the armpit (`CoderNunk`, `Chaosy3D`).
   - **Trap to avoid**: Anime stylized busts look much larger in 3D perspective than on 2D orthographic sheets—check frequently in Perspective view! Also, if the character wears a loose shirt/sweater, remove/smooth the deep sternum cleavage crease on the clothing mesh so the fabric bridges naturally across the chest.
4. **Hips & Pelvis**:
   - Run a clean **diagonal hip/pelvis loop** from the crotch crease upward over the iliac crest (hip bone) toward the glutes—never a flat horizontal belt loop straight across the upper thighs (`Chaosy3D`, `Dikko`)!
   - Why: When a character sits or kicks forward, a horizontal thigh loop folds awkwardly into the groin; a diagonal underwear-line hip loop bends cleanly!
   - Add `1–2` extra supporting loops around the glute curve (`back`) while keeping the front groin crease crisp.

---

## 3. Elbows & Knees: The 3-Loop Fan / Diamond Rule

Never place a single edge loop at an elbow or knee joint! When bent `120–150°`, a single loop loses 40% of its volume and turns into a pinched garden hose.

**Standard Anime Joint Pattern (`Chaosy3D`, `Natsumori Katsu`, `Dikko`)**:
1. Add **3 evenly spaced loops** spanning the joint (`Center joint loop` + `1 proximal` + `1 distal` supporting loop via `Ctrl+R` + `Ctrl+B` Bevel).
2. **Outer vs Inner Asymmetry**:
   - **Outer bending surface** (front of knee / back of elbow): keep `4–5` clean spans (more vertices = smooth curved knee cap / elbow tip under tension!).
   - **Inner crease surface** (back of knee / front inside elbow): inset & collapse/merge `1–2` spans into a clean diamond/triangle wedge (fewer vertices = zero ugly overlapping mesh fold when bent tightly!).
3. **Limb Segment Counts (`Chaosy3D`)**:
   - `10–14` verts around mid-arm/wrist; `14–18` verts around mid-thigh/calf.
   - Add **`4–6` evenly spaced twist loops** along the forearm and upper arm so wrist supination (`pronation/supination`) doesn't candy-wrap!
4. **Natural Pre-Bend (CRITICAL for Rigify/IK)**:
   - Model the elbow with a slight (`~5–10°`) backward bend and the knee with a slight (`~5–10°`) forward bend in Side View. Completely straight `180°` limbs cause IK solvers to bend backward or snap unpredictably!

---

## 4. Hands, Fingers & Feet

### Hands & Fingers (`Chaosy3D`, `Natsumori Katsu`, `Dikko`, `Noggi`)
1. **Finger Cylinders**: Use **`6–8` vertices** per finger (`8` for hero characters, `6` for game/mobile). Extrude in world space with palm flat (`-Z` down).
2. **Knuckle Loops**: Put **3 loops** at each knuckle joint (`Ctrl+R` + `Ctrl+B` small bevel).
   - **Noggi's "Anti-Sausage-Finger" Trick (`xZWxEoa-Dwk`)**: Add extra edge density on the **top/back of each knuckle** while keeping the **underside/inner crease** as a long clean span (or slight wedge collapse). When fingers curl around a sword hilt, the outer knuckles read crisply instead of looking like bent rubber tubes!
3. **Palm Thickness & Thumb**:
   - Give the palm real volume (`thicker at the heel/base, tapering slightly toward knuckles`; never a flat pancake!).
   - Keep a slight natural arch across the knuckles (`middle finger highest, pinky lowest`).
   - Connect fingers to palm (`bridge/fill` with `F2`), gradually reducing vertex count from `~24–28` across the palm down to **`16–20` vertices at the wrist** to match the forearm.
   - **Thumb**: Extrude from a **`10`-vert** side-palm loop rotated **`~35–45°` downward and forward** (`opposable` angle—never sticking straight out sideways at `90°`!).
4. **Fingernails**: Only model stylized nail ridges on hero close-up models; otherwise paint nail color onto the UV texture.

### Feet & Footwear (`Chaosy3D`, `Natsumori Katsu`, `CoderNunk`)
- **Flat Sole on `Z = 0`**: Align bottom sole faces strictly to `Z = 0` (`S Z 0`) so shoes/feet rest solidly on the ground without floating or clipping.
- **Anime Shoe Toe Spring**: Slightly curve the very front toe tip upward (`~2–5 mm`, `Natsumori Katsu`) for natural visual balance and walk-cycle roll.
- **Hidden Toes**: If the character always wears boots/shoes/socks, **DO NOT model 5 separate toes** (`waste of 400+ tris`)—model a clean stylized shoe/sock silhouette (`8–12` loops). Only model individual `8`-vert toes (`Chaosy3D`) for barefoot anime characters!

---

## 5. Body Topology QA Checklist

- [ ] Character stands at `Z = 0`, centered `X = 0`, facing `-Y`, real metric scale (`1.5–1.75 m`), `Ctrl+A -> All Transforms` applied.
- [ ] Arm/leg segments have **3 loops per bending joint** + slight natural IK pre-bend (elbow back, knee forward).
- [ ] Neck (`12–20` verts), wrists (`16–20` verts), and ankles have clean loop counts with even quad spacing (`Slide Relax` / `LoopTools -> Relax`).
- [ ] No n-gons (`>4` sides) anywhere on deforming joints; poles (`5`-edge verts) placed away from elbow/knee/groin creases (tucked on flat chest, back of skull, or shoulder blade).
- [ ] All normals point outward (`Face Orientation` = solid blue).
