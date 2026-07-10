# Chatbot Feature Plan

Covers document upload, ingestion pipeline, and RAG chatbot.

## Chatbot Flow

```
User selects one document → types question
    ↓
ChromaDB similarity search (top 5 chunks, filtered by selected document)
    ↓
Build prompt:
  - System: "Answer based on the provided context. If not in context, say so."
  - Context: [retrieved chunks]
  - History: [last 10 messages for this document from SQLite]
  - User: [current question]
    ↓
OpenAI GPT-4o-mini → answer
    ↓
Save message + response to SQLite (linked to document_id)
    ↓
Return to frontend
```

## Key decisions

- Chat is scoped to **one document at a time** (single-select in sidebar)
- Each document has **one conversation** — "Clear Chat" wipes it
- Chat input is **disabled** when no document is selected
- Switching documents loads that document's conversation history (display only, no API call)
- Vector query + OpenAI call only happens when user sends a message

## Checkpoints

### Phase 1 — Skeleton + Document Upload: DONE
- [x] Flask app with basic routes
- [x] SQLite schema
- [x] File upload endpoint (PDF, PPTX, TXT)
- [x] Parse text from each file type
- [x] Frontend: upload area + document list
- [x] Docker setup (Dockerfile + docker-compose.yml)

### Phase 2 — Ingestion Pipeline: DONE
- [x] Chunking logic (~2000 char chunks with 200 char overlap, splits on paragraph/sentence boundaries)
- [x] Embedding via ChromaDB default model (local, no API cost)
- [x] Store in ChromaDB (persistent, `chroma_data/`)
- [x] Link document metadata in SQLite (chunk_count updated on upload)

### Phase 3 — Chatbot: DONE
- [x] /api/chat endpoint (POST for messages, DELETE to clear history)
- [x] RAG retrieval from ChromaDB (top-5 chunks, filtered by single selected document)
- [x] Conversation history (last 10 messages from SQLite, included in prompt)
- [x] Chat UI with single-document selector (sidebar layout, click to select one doc)
- [x] Per-document chat history (messages stored and retrieved by document_id)
- [x] Disable chat input when no document is selected
- [x] Load document's chat history on document switch
- [x] Clear Chat clears only the selected document's history
