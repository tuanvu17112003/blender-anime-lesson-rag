# Blender Anime Character RAG + MCP Knowledge Base

Offline Hybrid RAG (**SQLite FTS5 BM25 + ChromaDB `ONNXMiniLM_L6_V2` dense vectors + Reciprocal Rank Fusion**) and stdio JSON-RPC 2.0 MCP documentation server synthesizing **3D anime character modeling, retopology, UVs, cel shading, custom face normals, SDF face shadows, Rigify/weight painting, physics, facial Shape Keys, limited animation, and Blender 4.2 / 5.2+ API best practices**.

## Why This Exists

AI agents coding Blender scripts or guiding 3D anime workflows often guess photorealistic proportions, ship broken raw face normals, mix removed Blender `4.x` APIs (`ShaderNodeMixRGB`, `action.fcurves`, `use_auto_smooth`), or tangle Rigify/skirt weights. This repository turns veteran 3D anime practitioner guides into a fast, offline, bilingual (**English + Vietnamese**) RAG MCP server.

## Repository Layout

- `docs/` — **11 curated practitioner guides** (`00_` through `10_`, including a **40-item Pitfall & Pre-Delivery QA Catalog** in `09_` and **Free Courses Compendium** in `10_`). Works standalone right after cloning.
- `AGENTS.md` — System instruction rules directing AI coding agents to query `blender-anime-lessons` before editing Blender assets/scripts.
- `fetch_sources.py` — Optional reproducible downloader to pull third-party YouTube transcripts/chapters, playlists, and companion GitHub documentation locally into `raw_sources/` (gitignored).
- `ingest.py` — Builds `data/lessons.sqlite3` (FTS5 + structured `pitfalls` table) and `data/chroma/` (`blender_anime_lessons`) from `docs/` (and `raw_sources/` if fetched locally).
- `anime_rag.py` — Standalone CLI + bilingual (Vietnamese/English) Hybrid RAG + stdio JSON-RPC 2.0 MCP server (`4` read-only tools).
- `smoke_test.py` — End-to-end verification suite (CLI search, pitfalls, section reads, and strict stdio MCP handshake/tool validation).

## Quick Setup

```bash
# 1. Install dependencies (Python >= 3.10)
pip install -e .

# 2. (Optional) Fetch full upstream YouTube transcripts & companion GitHub manuals locally
python fetch_sources.py

# 3. Build local SQLite FTS5 + Chroma vector index (works out-of-the-box with `docs/`)
python ingest.py

# 4. Query via CLI (English or Vietnamese)
python anime_rag.py search "cach xu ly bong khuon mat va vien outline trong blender"
python anime_rag.py pitfalls "Bone Heat Weighting"
python anime_rag.py read anime-facial-shapekeys-and-animation --section "Shape Key"
python anime_rag.py stats

# 5. Verify RAG + MCP protocol health
python smoke_test.py
```

## Register as an MCP Server

Add this server block to your MCP client config (e.g. `mcp_config.json`):

```json
{
  "mcpServers": {
    "blender-anime-lessons": {
      "type": "stdio",
      "command": "python",
      "args": ["-B", "/path/to/BlenderLessonDocs/anime_rag.py", "mcp"],
      "env": {
        "PYTHONUTF8": "1",
        "ANONYMIZED_TELEMETRY": "False"
      },
      "timeoutMs": 120000
    }
  }
}
```

### Exposed MCP Tools

- `search_anime_lessons(query, topic=None, tier="all", limit=6)`
- `read_anime_lesson(doc_id, section=None, offset=0, limit=16000)`
- `get_anime_pitfalls(symptom_or_topic, limit=8)`
- `list_anime_topics_and_courses(tier="curated")`

## Security & Third-Party Attribution

- Runs **100% offline** at query time with read-only SQLite access and telemetry disabled (see [SECURITY.md](SECURITY.md)).
- Third-party transcripts, web articles, and external repositories (`Noggi`, `Arc System Works / GDC`, `2AM`, `Natsumori Katsu`, `Daniel Kreuter`, `Crashsune Academy`, `Dikko`, `CGDive`, `Royal Skies`, `Lightning Boy Studio`, `Pierrick Picaut`, `VRM Consortium`, `GabrielToonShader`, `Blender Wiggle 2`, `BNPR Abnormal`, `Blender Foundation`) are **not redistributed** inside this Git repository—see `docs/10_courses_and_lessons_compendium.md` and `fetch_sources.py` for direct source links.
