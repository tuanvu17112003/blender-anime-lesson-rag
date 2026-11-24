#!/usr/bin/env python3
"""Build SQLite FTS5 + ChromaDB ONNX dense vector index for 3D anime character RAG."""

from __future__ import annotations

import datetime
import html
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY_IMPL", "none")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import chromadb  # noqa: E402
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2  # noqa: E402

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
RAW_WEB_DIR = ROOT / "raw_sources" / "web"
RAW_GH_DIR = ROOT / "raw_sources" / "github"
RAW_YT_VIDEOS_DIR = ROOT / "raw_sources" / "youtube" / "videos"
PLAYLISTS_INDEX_PATH = ROOT / "raw_sources" / "youtube" / "playlists_index.json"

DATA_DIR = ROOT / "data"
SQLITE_PATH = DATA_DIR / "lessons.sqlite3"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "blender_anime_lessons"

MAX_CHUNK_CHARS = 2200
CHUNK_OVERLAP_CHARS = 220


def slugify(value: str) -> str:
    """Convert arbitrary string into a safe lowercase identifier."""
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower()).strip("_")
    return s[:96] or "doc"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse simple YAML frontmatter block if present."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end_idx = None
    for idx in range(1, min(len(lines), 80)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, text

    meta: dict[str, str] = {}
    current_key: str | None = None
    list_buf: list[str] = []
    for raw_line in lines[1:end_idx]:
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and current_key:
            list_buf.append(line.lstrip()[2:].strip())
            meta[current_key] = "; ".join(list_buf)
            continue
        if ":" in line and not line.startswith(" "):
            key, val = line.split(":", 1)
            current_key = key.strip()
            list_buf = []
            cleaned = val.strip().strip('"').strip("'")
            if cleaned:
                meta[current_key] = cleaned
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")
    return meta, body


def clean_blender_manual_markdown(raw_text: str) -> str:
    """Strip repetitive Sphinx Furo navigation trees and donation banners from scraped docs."""
    lines = raw_text.splitlines()
    title_line = lines[0] if lines else ""
    source_line = lines[1] if len(lines) > 1 and lines[1].startswith("Source:") else ""

    # Detect huge Furo sidebar preceding main heading marked with permalink glyph.
    main_idx = None
    for idx, line in enumerate(lines):
        if idx > 150 and ('[¶](#' in line or 'Link to this heading' in line):
            main_idx = idx
            break

    if main_idx is not None:
        kept = [title_line]
        if source_line:
            kept.append(source_line)
        kept.append("")
        kept.extend(lines[main_idx:])
        text = "\n".join(kept)
    else:
        text = raw_text

    # Remove Furo permalink anchors and consecutive excess blank lines cleanly.
    text = re.sub(r'\[¶\]\(#[^\s)]+\s+"Link to this heading"\)', "", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def normalize_transcript(raw: str) -> str:
    """Clean YouTube subtitle transcripts and remove repeated adjacent lines."""
    if not raw.strip():
        return ""
    cleaned = html.unescape(raw)
    cleaned = re.sub(r">>+", "", cleaned)
    raw_lines = [re.sub(r"\s+", " ", ln).strip() for ln in cleaned.splitlines()]

    deduped: list[str] = []
    for ln in raw_lines:
        if not ln:
            continue
        if not deduped or ln != deduped[-1]:
            deduped.append(ln)

    # Regroup every ~14 caption fragments into readable paragraphs for clean chunking.
    paragraphs: list[str] = []
    buf: list[str] = []
    for ln in deduped:
        buf.append(ln)
        if len(buf) >= 14 or (len(" ".join(buf)) > 520 and ln.endswith((".", "?", "!"))):
            paragraphs.append(" ".join(buf))
            buf = []
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(paragraphs)


def split_large_block(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split an oversized text block cleanly along paragraph or word boundaries."""
    if len(text) <= max_chars:
        return [text.strip()] if text.strip() else []

    parts: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        if end < n:
            cut = text.rfind("\n\n", start + max_chars // 2, end)
            if cut == -1:
                cut = text.rfind(". ", start + max_chars // 2, end)
                if cut != -1:
                    cut += 1
            if cut == -1:
                cut = text.rfind(" ", start + max_chars // 2, end)
            if cut != -1 and cut > start + 200:
                end = cut
        chunk = text[start:end].strip()
        if chunk:
            parts.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return parts


def chunk_markdown(body: str, max_chars: int = MAX_CHUNK_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[tuple[str, str]]:
    """Split markdown into (section_breadcrumb, content) chunks preserving headers."""
    lines = body.splitlines()
    sections: list[tuple[str, list[str]]] = []
    h1 = ""
    h2 = ""
    h3 = ""
    current_label = "Overview"
    buf: list[str] = []

    def update_label() -> str:
        crumbs = [c for c in (h2, h3) if c]
        if crumbs:
            return " > ".join(crumbs)
        return h1 or "Overview"

    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if m:
            if any(x.strip() for x in buf):
                sections.append((current_label, buf))
            buf = [line]
            level = len(m.group(1))
            title = m.group(2).strip("# ").strip()
            if level == 1:
                h1, h2, h3 = title, "", ""
            elif level == 2:
                h2, h3 = title, ""
            else:
                h3 = title
            current_label = update_label()
        else:
            buf.append(line)

    if any(x.strip() for x in buf):
        sections.append((current_label, buf))

    chunks: list[tuple[str, str]] = []
    for sec_label, sec_lines in sections:
        sec_text = "\n".join(sec_lines).strip()
        if not sec_text:
            continue
        for piece in split_large_block(sec_text, max_chars=max_chars, overlap=overlap):
            chunks.append((sec_label, piece))

    return chunks


def extract_pitfalls_from_doc(doc_id: str, text: str) -> list[tuple[str, str, str, str, str]]:
    """Extract numbered | # | Symptom | Root Cause | Fix | rows from pitfall catalog markdown."""
    rows: list[tuple[str, str, str, str, str]] = []
    category = "General"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            category = line[3:].strip()
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 4 and cells[0].isdigit():
            symptom, root_cause, fix = cells[1], cells[2], cells[3]
            if symptom and fix:
                rows.append((doc_id, category, symptom, root_cause, fix))
    return rows


def infer_topic_from_text(name_hint: str, body: str = "") -> str:
    """Heuristically assign one canonical anime 3D topic tag to raw external sources."""
    hay = f"{name_hint} {body[:600]}".lower()
    if any(k in hay for k in ("smear", "stepped", "limited animation", "action_slot", "actions.html")):
        return "facial-shapekeys-and-animation"
    if any(k in hay for k in ("shape key", "shape_keys", "expressions", "viseme", "blink", "lipsync")):
        return "facial-shapekeys-and-animation"
    if any(k in hay for k in ("rig", "weight", "skinning", "skirt", "wiggle", "springbone", "bone_constraint", "humanoid")):
        return "rigging-and-weights"
    if any(k in hay for k in ("normal", "cel", "toon", "shader", "gtshader", "mtoon", "solidify", "outline", "sdf", "guilty_gear", "genshin", "abnormal")):
        return "shading-normals-outlines"
    if any(k in hay for k in ("retopo", "uv", "ucupaint", "textur", "paint", "data_transfer")):
        return "retopology-uv-texturing"
    if any(k in hay for k in ("hair", "curve", "ribbon")):
        return "hair-modeling-and-physics"
    if any(k in hay for k in ("face", "head", "eye")):
        return "face-head-eyes"
    if any(k in hay for k in ("cloth", "dress", "outfit", "armor")):
        return "clothing-and-layers"
    return "pipeline-and-proportions"


def load_curated_docs() -> tuple[list[dict[str, Any]], list[tuple[str, str, str, str, str]]]:
    """Load Tier-1 curated guides from docs/*.md."""
    docs: list[dict[str, Any]] = []
    pitfalls: list[tuple[str, str, str, str, str]] = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        doc_id = meta.get("doc_id") or slugify(path.stem)
        title = meta.get("title") or path.stem
        topic = meta.get("topic") or "general"
        kind = meta.get("kind") or "guide"
        blender_ver = meta.get("blender_version") or "4.2 LTS / 5.2 LTS / 5.3"
        summary = f"Tags: {meta.get('tags', '')} | Sources: {meta.get('sources', '')}".strip(" |")

        if kind == "pitfall-catalog":
            pitfalls.extend(extract_pitfalls_from_doc(doc_id, body))

        docs.append(
            {
                "doc_id": doc_id,
                "tier": "curated",
                "title": title,
                "topic": topic,
                "kind": kind,
                "blender_version": blender_ver,
                "source_url": f"docs/{path.name}",
                "summary": summary[:400],
                "body": body,
            }
        )
    return docs, pitfalls


def load_web_guides() -> list[dict[str, Any]]:
    """Load Tier-2 scraped web articles and official Blender 5.x manual docs."""
    if not RAW_WEB_DIR.exists():
        return []
    docs: list[dict[str, Any]] = []
    for path in sorted(RAW_WEB_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        if path.name.startswith("docs.blender.org_"):
            body = clean_blender_manual_markdown(raw)
        else:
            body = raw.strip()
        if len(body) < 120:
            continue

        lines = body.splitlines()
        first_heading = next((ln.lstrip("# ").strip() for ln in lines[:10] if ln.startswith("#")), "")
        title = first_heading or path.stem.replace("_", " ").title()
        src_match = re.search(r"^Source:\s*(https?://\S+)", body, re.MULTILINE)
        source_url = src_match.group(1) if src_match else f"raw_sources/web/{path.name}"

        docs.append(
            {
                "doc_id": f"web_{slugify(path.stem)}",
                "tier": "web_guide",
                "title": title[:180],
                "topic": infer_topic_from_text(path.stem, body),
                "kind": "web-article",
                "blender_version": "4.x / 5.x",
                "source_url": source_url,
                "summary": body[:280].replace("\n", " "),
                "body": body,
            }
        )
    return docs


def should_include_github_md(rel_path: Path) -> bool:
    """Filter out non-English translations, changelogs, and boilerplate repo files."""
    posix = rel_path.as_posix().lower()
    if any(skip in posix for skip in ("/ja-jp/", ".ja.md", "changelog.md", "pypi.md", "/typings/", "/benchmarks/", "/development/")):
        return False
    if posix.startswith("vrm_addon_for_blender/"):
        return posix == "vrm_addon_for_blender/readme.md" or "/docs/en-us/" in posix
    if posix.startswith("vrm_specification/"):
        return "/specification/vrmc_" in posix or posix == "vrm_specification/readme.md"
    if posix.startswith("gabrieltoonshader/"):
        return "gtshader_manual.md" in posix or posix == "gabrieltoonshader/readme.md"
    if posix.startswith(("blender_wiggle_2/", "bnpr_abnormal/")):
        return posix.endswith("readme.md")
    return False


def load_github_docs() -> list[dict[str, Any]]:
    """Load selective English technical documentation from cloned GitHub repositories."""
    if not RAW_GH_DIR.exists():
        return []
    docs: list[dict[str, Any]] = []
    for path in sorted(RAW_GH_DIR.rglob("*.md")):
        rel = path.relative_to(RAW_GH_DIR)
        if not should_include_github_md(rel):
            continue
        body = path.read_text(encoding="utf-8", errors="replace").strip()
        if len(body) < 120:
            continue
        first_heading = next((ln.lstrip("# ").strip() for ln in body.splitlines()[:8] if ln.startswith("#")), "")
        repo_name = rel.parts[0]
        title = f"[{repo_name}] {first_heading or rel.name}"
        docs.append(
            {
                "doc_id": f"gh_{slugify(rel.with_suffix('').as_posix())}",
                "tier": "github_source",
                "title": title[:180],
                "topic": infer_topic_from_text(rel.as_posix(), body),
                "kind": "github-doc",
                "blender_version": "4.x / 5.x",
                "source_url": f"raw_sources/github/{rel.as_posix()}",
                "summary": body[:280].replace("\n", " "),
                "body": body,
            }
        )
    return docs


def build_playlist_lookup() -> dict[str, str]:
    """Map YouTube video_id -> 'Channel: Playlist Title' using playlists_index.json."""
    if not PLAYLISTS_INDEX_PATH.exists():
        return {}
    mapping: dict[str, str] = {}
    try:
        data = json.loads(PLAYLISTS_INDEX_PATH.read_text(encoding="utf-8"))
        for info in data.values():
            ptitle = f"{info.get('uploader', '')}: {info.get('playlist_title', '')}".strip(": ")
            for entry in info.get("entries", []):
                vid = entry.get("id")
                if vid and vid not in mapping:
                    mapping[vid] = ptitle
    except (OSError, json.JSONDecodeError):
        pass
    return mapping


def load_youtube_episodes() -> list[dict[str, Any]]:
    """Load downloaded YouTube tutorial transcripts and chapter metadata."""
    if not RAW_YT_VIDEOS_DIR.exists():
        return []
    playlist_map = build_playlist_lookup()
    docs: list[dict[str, Any]] = []

    for path in sorted(RAW_YT_VIDEOS_DIR.glob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        vid = item.get("id", "")
        alias = item.get("alias") or path.stem
        title = item.get("title") or alias
        channel = item.get("channel") or "Unknown"
        url = item.get("webpage_url") or (f"https://www.youtube.com/watch?v={vid}" if vid else "")
        desc = (item.get("description") or "")[:1200].strip()
        chapters = item.get("chapters") or []
        transcript = normalize_transcript(item.get("transcript") or "")
        playlist_name = playlist_map.get(vid, "")

        parts = [
            f"# {title}",
            f"- **Channel**: {channel}",
            f"- **URL**: {url}",
        ]
        if playlist_name:
            parts.append(f"- **Course / Playlist**: {playlist_name}")
        if item.get("duration"):
            mins = int(item["duration"]) // 60
            parts.append(f"- **Duration**: {mins} min")

        if chapters:
            chap_lines = ["## Chapters"]
            for ch in chapters[:60]:
                st = int(ch.get("start_time") or 0)
                chap_lines.append(f"- `{st // 60:02d}:{st % 60:02d}` {ch.get('title', '')}")
            parts.append("\n".join(chap_lines))

        if desc:
            parts.append(f"## Video Notes\n\n{desc}")

        if transcript:
            parts.append(f"## Transcript\n\n{transcript}")

        body = "\n\n".join(parts)
        summary = f"YouTube ({channel}): {title}"
        if chapters:
            summary += f" [{len(chapters)} chapters]"
        if transcript:
            summary += f" ({len(transcript)} transcript chars)"

        docs.append(
            {
                "doc_id": f"yt_{slugify(alias)}",
                "tier": "youtube_episode",
                "title": f"[{channel}] {title}"[:180],
                "topic": infer_topic_from_text(f"{alias} {title}", desc + "\n" + transcript[:400]),
                "kind": "youtube-video",
                "blender_version": "3.x / 4.x / 5.x",
                "source_url": url or f"raw_sources/youtube/videos/{path.name}",
                "summary": summary[:400],
                "body": body,
            }
        )
    return docs


def rebuild_sqlite_and_chroma() -> None:
    """Rebuild lessons.sqlite3 and persistent Chroma vector database cleanly."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    curated_docs, pitfalls = load_curated_docs()
    web_docs = load_web_guides()
    github_docs = load_github_docs()
    yt_docs = load_youtube_episodes()

    all_docs = curated_docs + web_docs + github_docs + yt_docs
    print(
        f"Loaded corpus: curated={len(curated_docs)}, web_guide={len(web_docs)}, "
        f"github_source={len(github_docs)}, youtube_episode={len(yt_docs)} -> total={len(all_docs)} docs, {len(pitfalls)} pitfalls"
    )

    if SQLITE_PATH.exists():
        SQLITE_PATH.unlink()

    conn = sqlite3.connect(SQLITE_PATH)
    try:
        conn.executescript(
            """
            PRAGMA journal_mode = WAL;
            CREATE TABLE meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE docs (
                doc_id TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                kind TEXT NOT NULL,
                blender_version TEXT NOT NULL,
                source_url TEXT NOT NULL,
                summary TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                topic TEXT NOT NULL,
                section TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                char_count INTEGER NOT NULL,
                content TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE chunks_fts USING fts5(
                chunk_id UNINDEXED,
                doc_id UNINDEXED,
                title,
                topic,
                section,
                content,
                tokenize='unicode61 remove_diacritics 2'
            );
            CREATE TABLE pitfalls (
                pitfall_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                category TEXT NOT NULL,
                symptom TEXT NOT NULL,
                root_cause TEXT NOT NULL,
                fix TEXT NOT NULL
            );
            """
        )

        chunk_records: list[dict[str, Any]] = []
        for doc in all_docs:
            pairs = chunk_markdown(doc["body"])
            doc_id = doc["doc_id"]
            conn.execute(
                """
                INSERT INTO docs (doc_id, tier, title, topic, kind, blender_version, source_url, summary, char_count, chunk_count, body)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    doc["tier"],
                    doc["title"],
                    doc["topic"],
                    doc["kind"],
                    doc["blender_version"],
                    doc["source_url"],
                    doc["summary"],
                    len(doc["body"]),
                    len(pairs),
                    doc["body"],
                ),
            )
            for idx, (sec, content) in enumerate(pairs):
                chunk_id = f"{doc_id}__{idx:04d}"
                conn.execute(
                    """
                    INSERT INTO chunks (chunk_id, doc_id, tier, topic, section, chunk_index, char_count, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (chunk_id, doc_id, doc["tier"], doc["topic"], sec, idx, len(content), content),
                )
                conn.execute(
                    """
                    INSERT INTO chunks_fts (chunk_id, doc_id, title, topic, section, content)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (chunk_id, doc_id, doc["title"], doc["topic"], sec, content),
                )
                chunk_records.append(
                    {
                        "chunk_id": chunk_id,
                        "document": f"{doc['title']} | {sec}\n{content}",
                        "metadata": {
                            "doc_id": doc_id,
                            "tier": doc["tier"],
                            "topic": doc["topic"],
                            "section": sec[:120],
                            "chunk_index": idx,
                        },
                    }
                )

        conn.executemany(
            "INSERT INTO pitfalls (doc_id, category, symptom, root_cause, fix) VALUES (?, ?, ?, ?, ?)",
            pitfalls,
        )

        meta_rows = [
            ("built_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            ("doc_count", str(len(all_docs))),
            ("chunk_count", str(len(chunk_records))),
            ("pitfall_count", str(len(pitfalls))),
            ("blender_target", "4.2 LTS / 5.2 LTS / 5.3"),
            ("embedding_model", "ONNXMiniLM_L6_V2 (all-MiniLM-L6-v2)"),
        ]
        conn.executemany("INSERT INTO meta (key, value) VALUES (?, ?)", meta_rows)
        conn.commit()
    finally:
        conn.close()

    print(f"SQLite FTS5 built cleanly: {SQLITE_PATH} ({len(chunk_records)} chunks)")

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = ONNXMiniLM_L6_V2()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 128
    total = len(chunk_records)
    for start in range(0, total, batch_size):
        batch = chunk_records[start : start + batch_size]
        collection.add(
            ids=[b["chunk_id"] for b in batch],
            documents=[b["document"] for b in batch],
            metadatas=[b["metadata"] for b in batch],
        )
        if (start // batch_size) % 10 == 0 or start + batch_size >= total:
            print(f"  Embedded Chroma batch: {min(start + batch_size, total)}/{total}")

    print(f"Chroma vector collection '{COLLECTION_NAME}' complete: {collection.count()} vectors.")


if __name__ == "__main__":
    rebuild_sqlite_and_chroma()
