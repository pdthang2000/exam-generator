# Session 2 Summary — Phase 2 Complete

## What's been done

### Phase 2: Ingestion Pipeline

| File | Changes |
|---|---|
| `ingestion.py` | Added `chunk_text()` — splits text into ~2000-char chunks with 200-char overlap, breaks at paragraph (`\n\n`) or sentence (`. `) boundaries. Added `get_chroma_collection()` — persistent ChromaDB client. Added `ingest_document(doc_id, text)` — chunks text, stores in ChromaDB with metadata. Added `delete_document_chunks(doc_id)` — removes all chunks for a document from ChromaDB. Removed OpenAI embedding code (see issue below). |
| `database.py` | Added `update_chunk_count(doc_id, count)` — updates the `chunk_count` column after ingestion. |
| `app.py` | Upload route now calls `ingest_document()` + `update_chunk_count()` after parsing. Delete route calls `delete_document_chunks()` before removing from SQLite. Response includes `chunk_count`. |
| `static/index.html` | Document list now shows chunk count (e.g. `PDF · 7/4/2026 · 12 chunks`). Upload status shows "Uploading, parsing, and indexing document..." during processing. Success message shows chunk count. |
| `CLAUDE.md` | Updated embeddings tech stack entry. Phase 2 marked DONE. |

### Issue encountered: OpenAI embedding access

The course API key (`OPENAI_BASE_URL`) only allows `GPT-4o-mini` — calling `text-embedding-3-small` returns 403. Switched to ChromaDB's built-in default embedding function which runs locally (all-MiniLM-L6-v2, 384 dimensions). No API cost, no external dependency. This means queries in Phase 3 must also use ChromaDB's built-in embedding (pass `query_texts` to `collection.query()`, not pre-computed embeddings).

### ChromaDB Viewer

To inspect ChromaDB data with the VS Code ChromaDB Viewer extension:
```bash
pip install chromadb-server
chroma run --path /absolute/path/to/chroma_data --port 8000
```
Connect extension to `http://localhost:8000`. Uses v2 API with `default_tenant`/`default_database`.

## What's next

- **Phase 3**: Chatbot — `/api/chat` endpoint, RAG retrieval from ChromaDB, conversation history in SQLite, chat UI with document selector
- **Phase 4**: Exam generation — MCQ quiz from documents

## Git state

- Branch: `main`
- Latest commit: `cd0f88f` (Phase 2 changes not yet committed)
- Modified: `ingestion.py`, `database.py`, `app.py`, `static/index.html`, `CLAUDE.md`
