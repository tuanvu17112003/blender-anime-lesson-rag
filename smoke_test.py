#!/usr/bin/env python3
"""End-to-end verification tests for Blender Anime Hybrid RAG CLI & stdio MCP server."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RAG_SCRIPT = ROOT / "anime_rag.py"
PYTHON = sys.executable


def run_cli(*args: str) -> dict[str, Any]:
    """Run anime_rag CLI subcommand and parse JSON output."""
    proc = subprocess.run(
        [PYTHON, "-B", str(RAG_SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(proc.stdout)


def send_lsp(proc: subprocess.Popen[bytes], payload: dict[str, Any]) -> None:
    """Send Content-Length framed JSON-RPC message."""
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    proc.stdin.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw)
    proc.stdin.flush()


def recv_lsp(proc: subprocess.Popen[bytes]) -> dict[str, Any]:
    """Read Content-Length framed JSON-RPC message verifying zero stray stdout noise."""
    length = None
    while True:
        line = proc.stdout.readline()
        assert line, "Unexpected EOF waiting for MCP header"
        stripped = line.strip()
        if not stripped:
            if length is not None:
                break
            continue
        assert stripped.lower().startswith(b"content-length:"), f"Stray non-LSP line on stdout: {stripped!r}"
        length = int(stripped.split(b":", 1)[1].strip())
    body = proc.stdout.read(length)
    return json.loads(body.decode("utf-8"))


def main() -> None:
    print("1. Checking CLI stats...")
    stats = run_cli("stats")
    doc_count = int(stats["meta"]["doc_count"])
    chunk_count = int(stats["meta"]["chunk_count"])
    pitfall_count = int(stats["meta"]["pitfall_count"])
    vec_count = int(stats["vector_count"])
    assert doc_count >= 11, f"Expected >=11 docs, got {doc_count}"
    assert chunk_count == vec_count and chunk_count >= 40, f"SQLite chunks ({chunk_count}) != Chroma vectors ({vec_count})"
    assert pitfall_count >= 35, f"Expected >=35 pitfalls, got {pitfall_count}"
    print(f"   OK: {doc_count} docs, {chunk_count} chunks/vectors, {pitfall_count} pitfalls")

    print("2. Checking English & Vietnamese Hybrid Search...")
    for q in (
        "anime face shadow sdf normals data transfer",
        "cach xu ly bong khuon mat va vien outline trong blender",
        "skirt weight paint rigify thigh springbone",
        "blender 5 action fcurves slotted channelbag",
    ):
        res = run_cli("search", q, "--limit", "4")
        assert res["result_count"] >= 2, f"Too few hits for {q}"
        print(f"   OK '{q[:42]}...' -> top={res['results'][0]['doc_id']} (score={res['results'][0]['score']})")

    print("3. Checking Pitfalls Lookup...")
    for pq in ("Quadriflow", "ShaderNodeMixRGB", "Bone Heat", "Apply Modifiers"):
        pres = run_cli("pitfalls", pq, "--limit", "3")
        assert pres["matched_count"] >= 1, f"No pitfall match for {pq}"
        print(f"   OK pitfall '{pq}' -> #{pres['pitfalls'][0]['id']}: {pres['pitfalls'][0]['symptom'][:60]}")

    print("4. Checking Lesson Read & Section Filter...")
    read_res = run_cli("read", "cel-shading-anime-face-normals-and-outlines", "--section", "SDF")
    assert "content" in read_res and "atan2" in read_res["content"], "Expected SDF math inside read section"
    print(f"   OK section read -> {read_res['returned_chars']} chars")

    print("5. Checking Strict Stdio MCP JSON-RPC 2.0 Session...")
    proc = subprocess.Popen(
        [PYTHON, "-B", str(RAG_SCRIPT), "mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        send_lsp(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        init_resp = recv_lsp(proc)
        assert init_resp["result"]["protocolVersion"] == "2025-06-18"
        assert init_resp["result"]["serverInfo"]["name"] == "blender-anime-lessons"

        send_lsp(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send_lsp(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools_resp = recv_lsp(proc)
        tool_names = [t["name"] for t in tools_resp["result"]["tools"]]
        assert tool_names == [
            "search_anime_lessons",
            "read_anime_lesson",
            "get_anime_pitfalls",
            "list_anime_topics_and_courses",
        ], f"Unexpected tools: {tool_names}"

        calls = [
            (3, "list_anime_topics_and_courses", {"tier": "curated"}),
            (4, "get_anime_pitfalls", {"symptom_or_topic": "khuon mat to bong", "limit": 3}),
            (5, "search_anime_lessons", {"query": "smear frames stepped animation 24fps", "limit": 3}),
            (6, "read_anime_lesson", {"doc_id": "master-anime-pipeline-and-proportions", "limit": 1200}),
        ]
        for cid, tname, targs in calls:
            send_lsp(proc, {"jsonrpc": "2.0", "id": cid, "method": "tools/call", "params": {"name": tname, "arguments": targs}})
            cresp = recv_lsp(proc)
            assert not cresp["result"].get("isError", False), f"Tool {tname} failed: {cresp}"
            txt = cresp["result"]["content"][0]["text"]
            parsed = json.loads(txt)
            assert parsed, f"Empty tool output for {tname}"
            print(f"   OK MCP tool `{tname}` -> {len(txt)} chars JSON")

        send_lsp(proc, {"jsonrpc": "2.0", "id": 7, "method": "shutdown", "params": {}})
        recv_lsp(proc)
    finally:
        proc.stdin.close()
        stderr_tail = proc.stderr.read().decode("utf-8", errors="replace").strip()
        rc = proc.wait(timeout=15)
        assert rc == 0, f"MCP process exited non-zero ({rc}); stderr={stderr_tail}"
        print(f"   MCP exited cleanly (rc=0; stderr len={len(stderr_tail)})")

    print("\nALL SMOKE TESTS PASSED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
