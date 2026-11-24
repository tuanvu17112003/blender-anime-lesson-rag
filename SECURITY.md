# Security Policy

## Architectural Safety Guarantees

- **Offline-Only RAG & MCP Server (`anime_rag.py`)**: Zero runtime outbound HTTP requests (`openWorldHint: false`), zero telemetry (`ANONYMIZED_TELEMETRY=False`, `CHROMA_TELEMETRY_IMPL=none`), and zero secret/API-key dependencies.
- **Read-Only Database Access**: `anime_rag.py` opens SQLite in URI read-only mode (`?mode=ro`) with parameterized SQL queries (`sqlite3`) and FTS5 token sanitization.
- **Bounded Stdio Framing**: JSON-RPC `Content-Length` frames are strictly bounded (`<= 4 MiB`) to prevent malformed-frame memory exhaustion.
- **Download Isolation (`fetch_sources.py`)**: External YouTube transcripts, GitHub companions, and scraped references are fetched strictly over `https://` with sanitized path validation into gitignored `raw_sources/`.

## Reporting a Vulnerability

If you discover a bug, path-handling edge case, or potential security concern in this repository, please open a private security advisory on GitHub or contact the maintainer rather than filing public exploit details.
