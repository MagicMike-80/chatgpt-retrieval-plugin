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
