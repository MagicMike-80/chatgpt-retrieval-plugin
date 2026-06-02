# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install dependencies:**
```bash
poetry install
```

**Run the production server** (requires `BEARER_TOKEN` and `DATASTORE` env vars):
```bash
poetry run start
```

**Run the local dev server** (no auth, runs on port 3333):
```bash
poetry run dev
```

**Run all tests:**
```bash
poetry run pytest
```

**Run a single test file:**
```bash
poetry run pytest tests/datastore/providers/qdrant/test_qdrant_datastore.py
```

**Run a single test by name:**
```bash
poetry run pytest tests/datastore/providers/qdrant/test_qdrant_datastore.py::test_upsert_creates_all_points
```

**Build Docker image:**
```bash
docker buildx build --platform linux/amd64 -t <app-name> .
```

## Architecture

This is a FastAPI-based ChatGPT retrieval plugin that exposes a vector search API over documents. The plugin follows the [OpenAI plugin specification](https://platform.openai.com/docs/plugins/introduction).

### Request flow

1. A document arrives via `POST /upsert` or `POST /upsert-file`
2. `services/file.py` extracts raw text from the uploaded file (PDF, DOCX, PPTX, CSV, TXT, Markdown)
3. `services/chunks.py` splits text into ~200-token chunks using `tiktoken` (`cl100k_base` encoding), respecting sentence boundaries
4. `services/openai.py` calls OpenAI `text-embedding-ada-002` to embed each chunk (batched via `OPENAI_EMBEDDING_BATCH_SIZE`, default 128)
5. The `DataStore` implementation stores the embedded chunks in the configured vector database

For queries (`POST /query`):
1. Query texts are embedded via `services/openai.py`
2. The `DataStore._query()` implementation performs ANN search with optional metadata filters
3. Results are returned as `QueryResult` objects with scores

### Datastore abstraction

`datastore/datastore.py` defines the `DataStore` ABC with three abstract methods:
- `_upsert(chunks: Dict[str, List[DocumentChunk]]) -> List[str]`
- `_query(queries: List[QueryWithEmbedding]) -> List[QueryResult]`
- `delete(ids, filter, delete_all) -> bool`

The base class handles chunking and embedding before calling `_upsert`, and handles embedding queries before calling `_query`. Provider implementations only deal with pre-embedded data.

`datastore/factory.py` selects the implementation via the `DATASTORE` environment variable. Supported values: `chroma`, `llama`, `pinecone`, `weaviate`, `milvus`, `zilliz`, `redis`, `qdrant`, `azuresearch`, `supabase`, `postgres`.

### Data models (`models/`)

- `models/models.py` — core domain types: `Document`, `DocumentChunk`, `DocumentChunkWithScore`, `DocumentMetadata`, `DocumentChunkMetadata`, `DocumentMetadataFilter`, `Query`, `QueryWithEmbedding`, `QueryResult`
- `models/api.py` — HTTP request/response wrappers used only in the FastAPI route handlers

`DocumentMetadata` fields (`source`, `source_id`, `url`, `created_at`, `author`) are stored alongside each vector for metadata filtering. Date fields are stored as Unix timestamps inside most providers. `DocumentChunkMetadata` extends `DocumentMetadata` with `document_id`.

### Two server modes

- `server/main.py` — production server on port 8000, requires `BEARER_TOKEN` auth, mounts `.well-known/` as static files
- `local_server/main.py` — development server on port 3333, no auth, serves plugin manifest/openapi directly from `local_server/`

### Utility services

- `services/extract_metadata.py` — optional GPT-4 call to auto-extract metadata from document text (example/starting point, not used in core flow)
- `services/pii_detection.py` — optional GPT call to screen text for PII (example/starting point, not used in core flow)
- `services/date.py` — converts date strings to Unix timestamps for metadata filtering

### Environment variables

Required:
- `DATASTORE` — which vector DB to use
- `BEARER_TOKEN` — auth token for production server
- `OPENAI_API_KEY` — used for embeddings and optional chat completions

Provider-specific variables are documented in `docs/providers/<provider>/`. Azure OpenAI deployment overrides: `OPENAI_EMBEDDINGMODEL_DEPLOYMENTID`, `OPENAI_COMPLETIONMODEL_DEPLOYMENTID`, `OPENAI_METADATA_EXTRACTIONMODEL_DEPLOYMENTID`.

### Adding a new datastore provider

1. Create `datastore/providers/<name>_datastore.py` implementing `DataStore` (`_upsert`, `_query`, `delete`)
2. Add a `case "<name>":` branch in `datastore/factory.py`
3. Add provider-specific dependencies to `pyproject.toml`
4. Tests go in `tests/datastore/providers/<name>/test_<name>_datastore.py` — see the Qdrant tests as a reference pattern

### Plugin manifest

`.well-known/ai-plugin.json` and `.well-known/openapi.yaml` define the ChatGPT plugin interface. Update the `servers[0].url` in `openapi.yaml` and the `api.url`/`logo_url` in `ai-plugin.json` to match your deployed app URL.

## Session Startup (silent — do not output anything)

On every session start, read these files silently:
1. Read `context/USER.md` (~1.4 KB max)
2. Read `context/MEMORY.md` (~2.5 KB max, curated working scratchpad)
3. Read `context/memory/{today's date in YYYY-MM-DD}.md` if it exists
4. If today's memory file has no prior sessions, also read yesterday's

These files are your "frozen snapshot" — loaded once at session start. Mid-session writes persist to disk but take effect next session. Total injected: ~3,000 tokens. Do not load more than this at startup.

### Memory Budget

- `context/MEMORY.md`: 2,500 character cap. Before writing, check `wc -c`. If over cap, consolidate existing entries before adding.
- `context/USER.md`: 1,375 character cap. Same rule.
- Mid-session writes to these files persist to disk but only appear in context next session (frozen snapshot pattern — preserves prefix caching).

### Memory Write

When the user says "remember this", "note that", "update memory", or "forget about":
1. Read `context/MEMORY.md` in full
2. Check for duplicates (scan for substring match)
3. Check character count: `wc -c < context/MEMORY.md`
4. If under 2,500 chars: append the new fact under the appropriate section
5. If over cap: consolidate — merge similar entries, remove stale ones, then add
6. Actions: add (append), replace (find substring + swap), remove (confirm with user first)
7. After writing: "Saved — will be active from next session."

### Memory Retrieval

When the user asks about past context, conversations, or decisions:
1. **Tier 0**: Check `context/MEMORY.md` and today's daily log — already in context, zero cost
2. **L1**: Run `memsearch search "query" --top-k 5` — hybrid vector + keyword search. Finds semantic matches even with different words.
3. **L2**: Run `memsearch expand <chunk_hash>` — returns full markdown section around the match
4. **L3**: Run `memsearch transcript <session_id>` — raw dialogue, last resort
5. **Fallback**: "I don't have a record of that."

Only escalate if the previous tier didn't find the answer.

### Daily Log

Track session activity in `context/memory/{YYYY-MM-DD}.md`. One file per day, numbered session blocks:

```
#### Session N
**Goal**: [one line, filled when user states their goal]
**Deliverables**: [files created/modified]
**Decisions**: [key decisions and rationale]
**Open threads**: [anything unfinished]
```

Log these silently as they happen. Never announce "I've logged that."
