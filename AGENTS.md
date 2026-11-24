# AI Agent Working Rules — 3D Anime Character Pipeline (Blender 4.2 / 5.2+)

When designing, modeling, retopologizing, UV-mapping, shading, rigging, weight-painting, animating, or exporting **3D anime / NPR characters in Blender**, **query the `blender-anime-lessons` MCP server BEFORE guessing values, modifiers, node graphs, bone hierarchies, or `bpy` calls**.

## Mandatory Retrieval Order

1. **`get_anime_pitfalls`**: Check known anti-patterns for the stage you are about to touch (`face proportions`, `Quadriflow`, `Solidify outline`, `ILM`, `Data Transfer`, `Rigify`, `skirt weights`, `Shape Keys`, `Blender 5 action fcurves`, `FBX export`).
2. **`search_anime_lessons`**: Query practitioner techniques (`tier="curated"` first for synthesized rules; `tier="all"` when you want verbatim creator/manual/GitHub sources). Supports both English and Vietnamese queries.
3. **`read_anime_lesson`**: Read the full guide (`00` through `10`) or targeted `section` before emitting complex node setups, bone naming schemes, or Python scripts.
4. **`list_anime_topics_and_courses`**: Inspect indexed guides, free courses, and raw source IDs.

## Hard Non-Negotiable Rules (Never Violate)

- **Color Management**: Set `View Transform = Standard` in `BLENDER_EEVEE` (NOT `AgX` or `Filmic`).
- **Face Normals / Shadows**: Never ship raw polygonal anime face normals to a cel shader—use Proxy Ellipsoid `Data Transfer`, tilted-plane vector copy / `Abnormal`, or the SDF Face Shadow node setup.
- **Mesh Integrity**: `Scale = (1, 1, 1)` (`Ctrl+A`), centered at `(0,0,0)` facing `-Y`, `100% Blue` outside in `Face Orientation`, zero zero-area UVs.
- **Hair & Clothes**: Use `Scalp Cap + Bevel Curve Ribbons` (`U=3-4`), not `150k` particle/hair grooms; keep physical clearance (`2-3 mm`) to prevent z-fighting.
- **Weight & Rigging**: Keep Meta-Rig `spine` at `X = 0`, slight knee/elbow pre-bend, isolate **`DEF` Bone Collection** when painting, force `1.0 Head` weight above jaw & eyes, strip `thigh` weights from skirts, and run `Limit Total (4)` + `Normalize All` before game export.
- **Shape Keys & Export**: Apply Mirror/Subdiv BEFORE creating Shape Keys; uncheck `Apply Modifiers` on FBX export when Shape Keys exist.
- **Blender 5.2+ APIs**: Never use removed APIs (`ShaderNodeMixRGB`, `action.fcurves`, `mesh.use_auto_smooth`, `bone.layers`, `Bone.select`, `BLENDER_EEVEE_NEXT`, `GreasePencilv3`, `FAST` Boolean).
