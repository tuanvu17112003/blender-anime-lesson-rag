#!/usr/bin/env python3
"""Offline Hybrid RAG CLI & stdio JSON-RPC 2.0 MCP server for 3D Anime Blender knowledge."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from typing import Any

# Silence noisy third-party telemetry and stdout progress bars in stdio MCP mode.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY_IMPL", "none")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SQLITE_PATH = DATA_DIR / "lessons.sqlite3"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "blender_anime_lessons"

SERVER_NAME = "blender-anime-lessons"
SERVER_VERSION = "0.1.0"
SUPPORTED_PROTOCOLS = {"2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"}
MAX_MCP_MESSAGE_BYTES = 4 * 1024 * 1024

TIER_BOOST = {
    "curated": 1.45,
    "web_guide": 1.05,
    "github_source": 1.00,
    "youtube_episode": 0.90,
}

# Bilingual Vietnamese/English expansion map covering common 3D anime & Blender terminology.
VI_EN_SYNONYMS: dict[str, str] = {
    "khuon mat": "anime face head proportions eyes mouth topology",
    "guong mat": "anime face head proportions eyes mouth topology",
    "bong khuon mat": "face shadow custom normals data transfer sdf abnormal cel shading",
    "bong mat": "face shadow custom normals data transfer sdf abnormal",
    "do bong": "cel shading toon shader diffuse shader to rgb shadow band",
    "to bong": "cel shading toon shader diffuse shader to rgb ilm",
    "vien": "outline solidify inverted hull backface culling vertex color",
    "net vien": "outline solidify inverted hull line art grease pencil",
    "toc": "anime hair curve ribbons scalp cap solidify wiggle springbone",
    "mai toc": "front hair bangs ribbon curve solidify",
    "vay": "skirt weights thigh strip springbone link 2 wiggle",
    "quan ao": "clothing layers solidify clearance data transfer",
    "trang phuc": "clothing layers outfit armor accessories",
    "xuong": "armature rigify metarig bone collections def",
    "khop": "knee elbow shoulder loops pre-bend pole flip",
    "trong so": "weight paint skinning auto weights voxel proxy normalize limit total",
    "son trong so": "weight paint bone heat deform",
    "bieu cam": "shape keys blendshapes expressions vrm arkit",
    "nhay mat": "blink eyeBlinkLeft blinkRight blend from shape eyelash",
    "khau hinh": "lip sync visemes aa ih uu ee oh mouth bag",
    "moi": "lips mouth bag orbital loops",
    "mat": "anime eyes iris cornea dish eye aim",
    "chuyen dong": "limited animation stepped interpolation 24fps smear lattice",
    "hoat hoa": "animation pose to pose stepped frame skip silhouette",
    "ti le": "proportions head height torso limbs anime ratio",
    "luoi": "topology retopology manual shrinkwrap quad loops",
    "vat ly": "wiggle 2 springbone physics collider tail leaf bone",
    "rung": "wiggle 2 springbone bust hair skirt jitter",
    "xuat": "export fbx glb vrm deform bones apply modifiers",
    "loi": "pitfall bug fix root cause troubleshooting",
    "bi den": "pitch black cycles outline transparent shadows backfacing",
    "giat": "frame skip stepped interpolation 24fps 2s 3s",
    "da": "skin albedo sss terminator warm shadow",
}

_VECTOR_STATE: dict[str, Any] = {"loaded": False, "collection": None, "error": None}


def strip_diacritics(text: str) -> str:
    """Convert Vietnamese accented string into plain lowercase ASCII for robust lookup."""
    decomposed = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()


def expand_query(query: str) -> tuple[str, list[str]]:
    """Expand Vietnamese & shorthand anime terms into enriched bilingual search tokens."""
    norm = strip_diacritics(query)
    additions: list[str] = []
    for vi_phrase, en_terms in VI_EN_SYNONYMS.items():
        if vi_phrase in norm:
            additions.append(en_terms)

    # Shorthand / Blender 5.x technical expansions.
    extra_rules = {
        "sdf": "signed distance field face shadow threshold map",
        "ilm": "inner line lightmap specular ambient occlusion",
        "vrm": "vrm humanoid expressions mtoon springbone",
        "rigify": "metarig bone collections def generate rig",
        "fcurves": "slotted actions channelbag blender 5",
        "mixrgb": "ShaderNodeMix RGBA blender 5",
        "autosmooth": "Smooth by Angle modifier blender 5",
    }
    raw_words = re.findall(r"[a-zA-Z0-9_]+", norm)
    for w in raw_words:
        if w in extra_rules:
            additions.append(extra_rules[w])

    expanded = f"{query} {' '.join(additions)}".strip()
    tokens = []
    seen = set()
    for tok in re.findall(r"[a-zA-Z0-9_]{2,}", strip_diacritics(expanded)):
        if tok not in seen:
            seen.add(tok)
            tokens.append(tok)
    return expanded, tokens


def get_db_connection() -> sqlite3.Connection:
    """Open read-only SQLite connection to lessons.sqlite3."""
    if not SQLITE_PATH.exists():
        raise FileNotFoundError(f"Index database missing at {SQLITE_PATH}. Run ingest.py first.")
    conn = sqlite3.connect(f"file:{SQLITE_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_vector_collection() -> Any | None:
    """Lazy-load ChromaDB collection with stdout redirected to stderr so stdio MCP stays pure."""
    if _VECTOR_STATE["loaded"]:
        return _VECTOR_STATE["collection"]
    _VECTOR_STATE["loaded"] = True
    if not CHROMA_DIR.exists():
        _VECTOR_STATE["error"] = f"Chroma directory missing at {CHROMA_DIR}"
        return None
    try:
        with contextlib.redirect_stdout(sys.stderr):
            import chromadb
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            ef = ONNXMiniLM_L6_V2()
            col = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        _VECTOR_STATE["collection"] = col
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        _VECTOR_STATE["error"] = repr(exc)
        _VECTOR_STATE["collection"] = None
    return _VECTOR_STATE["collection"]


def build_fts_query(tokens: list[str]) -> str:
    """Construct a safe SQLite FTS5 query string from alphanumeric tokens."""
    safe = [t for t in tokens[:18] if t.isalnum() and len(t) >= 2]
    if not safe:
        return ""
    return " OR ".join(f'"{t}"' for t in safe)


def search_anime_lessons(
    query: str,
    topic: str | None = None,
    tier: str = "all",
    limit: int = 6,
    use_vector: bool = True,
) -> dict[str, Any]:
    """Run hybrid BM25 + Chroma dense vector search with Reciprocal Rank Fusion and tier boosting."""
    limit = max(1, min(int(limit), 20))
    expanded_query, tokens = expand_query(query)
    fts_expr = build_fts_query(tokens)

    conn = get_db_connection()
    try:
        bm25_ranks: dict[str, int] = {}
        chunk_meta: dict[str, dict[str, Any]] = {}

        if fts_expr:
            sql = """
                SELECT c.chunk_id, c.doc_id, c.tier, c.topic, c.section, c.chunk_index, c.content,
                       d.title, d.source_url, d.blender_version, bm25(chunks_fts, 2.0, 1.5, 1.5, 1.0) AS rank_score
                FROM chunks_fts
                JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
                JOIN docs d ON d.doc_id = c.doc_id
                WHERE chunks_fts MATCH ?
            """
            params: list[Any] = [fts_expr]
            if tier and tier != "all":
                sql += " AND c.tier = ?"
                params.append(tier)
            if topic:
                sql += " AND c.topic = ?"
                params.append(topic)
            sql += " ORDER BY rank_score LIMIT ?"
            params.append(max(40, limit * 8))

            for idx, row in enumerate(conn.execute(sql, params), start=1):
                cid = row["chunk_id"]
                bm25_ranks[cid] = idx
                chunk_meta[cid] = dict(row)

        vec_ranks: dict[str, int] = {}
        col = get_vector_collection() if use_vector else None
        if col is not None:
            where_clauses: list[dict[str, Any]] = []
            if tier and tier != "all":
                where_clauses.append({"tier": tier})
            if topic:
                where_clauses.append({"topic": topic})
            where_filter: dict[str, Any] | None = None
            if len(where_clauses) == 1:
                where_filter = where_clauses[0]
            elif len(where_clauses) > 1:
                where_filter = {"$and": where_clauses}

            try:
                with contextlib.redirect_stdout(sys.stderr):
                    res = col.query(
                        query_texts=[expanded_query],
                        n_results=max(40, limit * 8),
                        where=where_filter,
                    )
                ids = (res.get("ids") or [[]])[0]
                for idx, cid in enumerate(ids, start=1):
                    vec_ranks[cid] = idx
                missing_ids = [cid for cid in ids if cid not in chunk_meta]
                if missing_ids:
                    placeholders = ",".join("?" for _ in missing_ids)
                    rows = conn.execute(
                        f"""
                        SELECT c.chunk_id, c.doc_id, c.tier, c.topic, c.section, c.chunk_index, c.content,
                               d.title, d.source_url, d.blender_version
                        FROM chunks c
                        JOIN docs d ON d.doc_id = c.doc_id
                        WHERE c.chunk_id IN ({placeholders})
                        """,
                        missing_ids,
                    ).fetchall()
                    for row in rows:
                        chunk_meta[row["chunk_id"]] = dict(row)
            except Exception:
                pass

        # Fuse rankings via Reciprocal Rank Fusion + tier weight multiplier.
        all_ids = set(bm25_ranks) | set(vec_ranks)
        scored: list[tuple[float, dict[str, Any]]] = []
        for cid in all_ids:
            info = chunk_meta.get(cid)
            if not info:
                continue
            rrf = 0.0
            if cid in bm25_ranks:
                rrf += 1.0 / (60.0 + bm25_ranks[cid])
            if cid in vec_ranks:
                rrf += 1.0 / (60.0 + vec_ranks[cid])
            rrf *= TIER_BOOST.get(info["tier"], 1.0)
            info["score"] = round(rrf, 6)
            scored.append((rrf, info))

        scored.sort(key=lambda item: item[0], reverse=True)

        # Preserve diversity across documents unless narrow tier/topic results require more.
        selected: list[dict[str, Any]] = []
        per_doc_counts: dict[str, int] = {}
        overflow: list[dict[str, Any]] = []
        max_per_doc = 2 if limit <= 8 else 3
        for _, info in scored:
            did = info["doc_id"]
            if per_doc_counts.get(did, 0) < max_per_doc:
                selected.append(info)
                per_doc_counts[did] = per_doc_counts.get(did, 0) + 1
            else:
                overflow.append(info)
            if len(selected) >= limit:
                break
        if len(selected) < limit:
            selected.extend(overflow[: limit - len(selected)])

        results = [
            {
                "doc_id": item["doc_id"],
                "title": item["title"],
                "tier": item["tier"],
                "topic": item["topic"],
                "section": item["section"],
                "score": item["score"],
                "blender_version": item["blender_version"],
                "source_url": item["source_url"],
                "snippet": item["content"][:950],
            }
            for item in selected[:limit]
        ]
        return {
            "query": query,
            "expanded_terms": expanded_query if expanded_query != query else None,
            "filters": {"topic": topic, "tier": tier},
            "result_count": len(results),
            "results": results,
        }
    finally:
        conn.close()


def read_anime_lesson(
    doc_id: str,
    section: str | None = None,
    offset: int = 0,
    limit: int = 16000,
) -> dict[str, Any]:
    """Read full or section-filtered guide/transcript text with pagination metadata."""
    offset = max(0, int(offset))
    limit = max(200, min(int(limit), 32000))

    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM docs WHERE doc_id = ?", (doc_id,)).fetchone()
        if row is None:
            suggestions = [
                r["doc_id"]
                for r in conn.execute(
                    "SELECT doc_id FROM docs WHERE doc_id LIKE ? ORDER BY CASE tier WHEN 'curated' THEN 0 ELSE 1 END, doc_id LIMIT 8",
                    (f"%{doc_id}%",),
                ).fetchall()
            ]
            return {"error": f"Document '{doc_id}' not found.", "suggestions": suggestions}

        body = row["body"]
        headings = [m.group(0) for m in re.finditer(r"^#{1,3}\s+.+$", body, re.MULTILINE)][:40]

        target_text = body
        matched_section = None
        if section:
            sec_norm = strip_diacritics(section)
            lines = body.splitlines()
            start_line = None
            start_level = 99
            for idx, ln in enumerate(lines):
                m = re.match(r"^(#{1,4})\s+(.+)$", ln)
                if m and sec_norm in strip_diacritics(m.group(2)):
                    start_line = idx
                    start_level = len(m.group(1))
                    matched_section = m.group(2).strip()
                    break
            if start_line is not None:
                end_line = len(lines)
                for idx in range(start_line + 1, len(lines)):
                    m = re.match(r"^(#{1,4})\s+(.+)$", lines[idx])
                    if m and len(m.group(1)) <= start_level:
                        end_line = idx
                        break
                target_text = "\n".join(lines[start_line:end_line])
            else:
                return {
                    "doc_id": doc_id,
                    "title": row["title"],
                    "error": f"Section matching '{section}' not found in '{doc_id}'.",
                    "available_headings": headings,
                }

        total_chars = len(target_text)
        slice_text = target_text[offset : offset + limit]
        has_more = (offset + len(slice_text)) < total_chars
        return {
            "doc_id": row["doc_id"],
            "title": row["title"],
            "tier": row["tier"],
            "topic": row["topic"],
            "blender_version": row["blender_version"],
            "source_url": row["source_url"],
            "matched_section": matched_section,
            "offset": offset,
            "returned_chars": len(slice_text),
            "total_chars": total_chars,
            "has_more": has_more,
            "next_offset": (offset + len(slice_text)) if has_more else None,
            "available_headings": headings,
            "content": slice_text,
        }
    finally:
        conn.close()


def get_anime_pitfalls(symptom_or_topic: str, limit: int = 8) -> dict[str, Any]:
    """Query structured anime 3D bug-symptom/root-cause/fix catalog rows."""
    limit = max(1, min(int(limit), 25))
    _, tokens = expand_query(symptom_or_topic)

    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM pitfalls ORDER BY pitfall_id").fetchall()
        scored: list[tuple[int, sqlite3.Row]] = []
        raw_norm = strip_diacritics(symptom_or_topic)
        for row in rows:
            blob = strip_diacritics(f"{row['category']} {row['symptom']} {row['root_cause']} {row['fix']}")
            hits = sum(2 if tok in strip_diacritics(row["symptom"]) else 1 for tok in tokens if tok in blob)
            if raw_norm and raw_norm in blob:
                hits += 4
            if hits > 0:
                scored.append((hits, row))

        scored.sort(key=lambda item: (item[0], -item[1]["pitfall_id"]), reverse=True)
        chosen = [r for _, r in scored[:limit]] if scored else list(rows[:limit])
        return {
            "query": symptom_or_topic,
            "matched_count": len(chosen),
            "pitfalls": [
                {
                    "id": r["pitfall_id"],
                    "category": r["category"],
                    "symptom": r["symptom"],
                    "root_cause": r["root_cause"],
                    "exact_fix": r["fix"],
                    "doc_id": r["doc_id"],
                }
                for r in chosen
            ],
        }
    finally:
        conn.close()


def list_anime_topics_and_courses(tier: str = "curated") -> dict[str, Any]:
    """List corpus metadata, topics, curated guides, or raw indexed courses/repos."""
    conn = get_db_connection()
    try:
        meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta").fetchall()}
        tier_counts = {
            r["tier"]: r["cnt"]
            for r in conn.execute("SELECT tier, COUNT(*) AS cnt FROM docs GROUP BY tier ORDER BY cnt DESC").fetchall()
        }
        topic_counts = {
            r["topic"]: r["cnt"]
            for r in conn.execute("SELECT topic, COUNT(*) AS cnt FROM docs GROUP BY topic ORDER BY cnt DESC").fetchall()
        }

        sql = "SELECT doc_id, tier, title, topic, kind, blender_version, source_url, chunk_count FROM docs"
        params: list[Any] = []
        if tier and tier != "all":
            sql += " WHERE tier = ?"
            params.append(tier)
        sql += " ORDER BY CASE tier WHEN 'curated' THEN 0 WHEN 'web_guide' THEN 1 WHEN 'github_source' THEN 2 ELSE 3 END, doc_id LIMIT 250"

        docs = [dict(r) for r in conn.execute(sql, params).fetchall()]
        return {
            "meta": meta,
            "tier_counts": tier_counts,
            "topic_counts": topic_counts,
            "requested_tier": tier,
            "documents": docs,
        }
    finally:
        conn.close()


def get_stats() -> dict[str, Any]:
    """Return index health summary including vector count."""
    info = list_anime_topics_and_courses(tier="curated")
    col = get_vector_collection()
    vec_count = col.count() if col is not None else 0
    return {
        "sqlite_path": str(SQLITE_PATH),
        "chroma_path": str(CHROMA_DIR),
        "vector_count": vec_count,
        "vector_error": _VECTOR_STATE.get("error"),
        "meta": info["meta"],
        "tier_counts": info["tier_counts"],
        "topic_counts": info["topic_counts"],
    }


MCP_TOOLS = [
    {
        "name": "search_anime_lessons",
        "description": (
            "Search the curated 3D Anime Character Modeling, Retopology, UV, Cel Shading, "
            "Face Normals, SDF Shadows, Rigify/Weight Painting, Physics, Shape Keys, Limited Animation, "
            "and Blender 5.2+ RAG knowledge base. Supports English and Vietnamese queries."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query in English or Vietnamese."},
                "topic": {
                    "type": "string",
                    "description": (
                        "Optional topic filter: pipeline-and-proportions, face-head-eyes, "
                        "body-topology-proportions, hair-modeling-and-physics, clothing-and-layers, "
                        "retopology-uv-texturing, shading-normals-outlines, rigging-and-weights, "
                        "facial-shapekeys-and-animation, troubleshooting-qa, courses-catalog."
                    ),
                },
                "tier": {
                    "type": "string",
                    "enum": ["all", "curated", "web_guide", "github_source", "youtube_episode"],
                    "default": "all",
                    "description": "Filter by corpus tier (curated gives distilled guides first).",
                },
                "limit": {"type": "integer", "default": 6, "minimum": 1, "maximum": 20},
            },
            "required": ["query"],
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "read_anime_lesson",
        "description": "Read a curated anime guide, web guide, GitHub doc, or YouTube transcript by doc_id and optional section heading.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "Exact doc_id from search or list results."},
                "section": {"type": "string", "description": "Optional heading substring to isolate one section."},
                "offset": {"type": "integer", "default": 0, "minimum": 0},
                "limit": {"type": "integer", "default": 16000, "minimum": 200, "maximum": 32000},
            },
            "required": ["doc_id"],
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "get_anime_pitfalls",
        "description": (
            "Look up common 3D anime AI agent mistakes, symptoms, root causes, and exact Blender 4.2/5.2+ fixes "
            "(e.g., face shadows, Solidify Cycles pitch black, Bone Heat errors, Skirt thigh bleed, ShaderNodeMixRGB, action.fcurves)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "symptom_or_topic": {"type": "string", "description": "Symptom, bug, modifier, API error, or Vietnamese phrase."},
                "limit": {"type": "integer", "default": 8, "minimum": 1, "maximum": 25},
            },
            "required": ["symptom_or_topic"],
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "list_anime_topics_and_courses",
        "description": "List indexed guides, course playlists, topics, and counts across tiers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "string",
                    "enum": ["curated", "web_guide", "github_source", "youtube_episode", "all"],
                    "default": "curated",
                }
            },
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
]


def handle_mcp_request(msg: dict[str, Any]) -> tuple[dict[str, Any] | None, bool]:
    """Dispatch a single JSON-RPC 2.0 request and return (response_dict_or_None, keep_running)."""
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}

    if method == "initialize":
        client_proto = str(params.get("protocolVersion") or "2025-06-18")
        chosen_proto = client_proto if client_proto in SUPPORTED_PROTOCOLS else "2025-06-18"
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": chosen_proto,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }, True

    if method in ("notifications/initialized", "notifications/cancelled"):
        return None, True

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}, True

    if method == "shutdown":
        return {"jsonrpc": "2.0", "id": req_id, "result": None}, False

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}, True

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "search_anime_lessons":
                payload = search_anime_lessons(
                    query=str(args["query"]),
                    topic=args.get("topic"),
                    tier=str(args.get("tier", "all")),
                    limit=int(args.get("limit", 6)),
                )
            elif name == "read_anime_lesson":
                payload = read_anime_lesson(
                    doc_id=str(args["doc_id"]),
                    section=args.get("section"),
                    offset=int(args.get("offset", 0)),
                    limit=int(args.get("limit", 16000)),
                )
            elif name == "get_anime_pitfalls":
                payload = get_anime_pitfalls(
                    symptom_or_topic=str(args["symptom_or_topic"]),
                    limit=int(args.get("limit", 8)),
                )
            elif name == "list_anime_topics_and_courses":
                payload = list_anime_topics_and_courses(tier=str(args.get("tier", "curated")))
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {name}"},
                }, True

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
                    "isError": bool(isinstance(payload, dict) and "error" in payload and "results" not in payload),
                },
            }, True
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"error": str(exc)}, ensure_ascii=False)}],
                    "isError": True,
                },
            }, True

    if req_id is None:
        return None, True

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }, True


def read_stdio_message(buf_in: Any) -> tuple[dict[str, Any] | None, str]:
    """Read either a Content-Length framed or newline-delimited JSON-RPC frame cleanly."""
    while True:
        line = buf_in.readline()
        if not line:
            return None, "ndjson"
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(b"{"):
            return json.loads(stripped.decode("utf-8")), "ndjson"
        if stripped.lower().startswith(b"content-length:"):
            length = int(stripped.split(b":", 1)[1].strip())
            if length <= 0 or length > MAX_MCP_MESSAGE_BYTES:
                raise ValueError(f"Invalid Content-Length: {length}")
            while True:
                hdr = buf_in.readline()
                if not hdr or hdr in (b"\r\n", b"\n"):
                    break
            raw_body = buf_in.read(length)
            if not raw_body:
                return None, "lsp"
            return json.loads(raw_body.decode("utf-8")), "lsp"


def write_stdio_message(buf_out: Any, payload: dict[str, Any], framing: str) -> None:
    """Serialize JSON-RPC message matching detected client framing."""
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if framing == "lsp":
        header = f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii")
        buf_out.write(header + raw)
    else:
        buf_out.write(raw + b"\n")
    buf_out.flush()


def run_mcp_server() -> None:
    """Run blocking stdio JSON-RPC 2.0 MCP loop keeping stdout strictly pure."""
    buf_in = sys.stdin.buffer
    buf_out = sys.stdout.buffer
    while True:
        try:
            msg, framing = read_stdio_message(buf_in)
        except Exception as exc:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
            write_stdio_message(buf_out, err_resp, "ndjson")
            continue
        if msg is None:
            break
        resp, keep_running = handle_mcp_request(msg)
        if resp is not None:
            write_stdio_message(buf_out, resp, framing)
        if not keep_running:
            break


def main() -> None:
    """CLI entrypoint for stats, search, read, pitfalls, list, and mcp modes."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Blender 3D Anime Character RAG + MCP Tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats", help="Print index statistics")

    p_search = sub.add_parser("search", help="Hybrid RAG search")
    p_search.add_argument("query")
    p_search.add_argument("--topic", default=None)
    p_search.add_argument("--tier", default="all")
    p_search.add_argument("--limit", type=int, default=6)
    p_search.add_argument("--no-vector", action="store_true")

    p_read = sub.add_parser("read", help="Read lesson document or section")
    p_read.add_argument("doc_id")
    p_read.add_argument("--section", default=None)
    p_read.add_argument("--offset", type=int, default=0)
    p_read.add_argument("--limit", type=int, default=16000)

    p_pit = sub.add_parser("pitfalls", help="Query anime 3D bug-fix catalog")
    p_pit.add_argument("query")
    p_pit.add_argument("--limit", type=int, default=8)

    p_list = sub.add_parser("list", help="List documents by tier")
    p_list.add_argument("--tier", default="curated")

    sub.add_parser("mcp", help="Run stdio JSON-RPC 2.0 MCP server")

    args = parser.parse_args()
    if args.cmd == "mcp":
        run_mcp_server()
        return

    if args.cmd == "stats":
        out = get_stats()
    elif args.cmd == "search":
        out = search_anime_lessons(
            query=args.query,
            topic=args.topic,
            tier=args.tier,
            limit=args.limit,
            use_vector=not args.no_vector,
        )
    elif args.cmd == "read":
        out = read_anime_lesson(doc_id=args.doc_id, section=args.section, offset=args.offset, limit=args.limit)
    elif args.cmd == "pitfalls":
        out = get_anime_pitfalls(symptom_or_topic=args.query, limit=args.limit)
    elif args.cmd == "list":
        out = list_anime_topics_and_courses(tier=args.tier)
    else:
        raise ValueError(f"Unknown command: {args.cmd}")

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
