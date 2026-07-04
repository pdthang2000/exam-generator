# Session 3 Summary — Phase 3: Chatbot

## What was done

### New file: `chat.py`
- `retrieve_chunks(query, document_ids, n_results=5)` — queries ChromaDB with similarity search, optionally filtered by selected document IDs using `$in` operator
- `chat(message, document_ids)` — full RAG chat flow:
  1. Retrieve top-5 relevant chunks from ChromaDB
  2. Build prompt: system instruction + context chunks + last 10 conversation messages + user question
  3. Call OpenAI GPT-4o-mini
  4. Save user message and assistant response to SQLite
  5. Return the answer

### Updated: `database.py`
- Added `insert_chat_message(role, content)` — stores a chat message in `chat_history` table
- Added `get_chat_history(limit=20)` — retrieves last N messages in chronological order
- Added `clear_chat_history()` — deletes all chat history

### Updated: `app.py`
- `POST /api/chat` — accepts `{message, document_ids}`, returns `{answer}` via RAG pipeline
- `DELETE /api/chat` — clears conversation history

### Updated: `static/index.html`
- Redesigned from single-page to two-panel layout:
  - **Left sidebar**: document upload area + document list (click to select/deselect for chat)
  - **Right panel**: chat interface with message history
- Selected documents highlighted with indigo border
- Chat header shows which documents are selected
- "Thinking..." indicator while waiting for AI response
- Enter to send, Shift+Enter for newline
- Clear Chat button to reset conversation
- Responsive: stacks vertically on mobile (< 768px)
- Bug fix: doc-item layout changed from horizontal to vertical stacking so Preview/Remove buttons don't overlap long filenames

## Files changed
| File | Change |
|---|---|
| `chat.py` | New — RAG retrieval + OpenAI chat logic |
| `database.py` | Added chat history CRUD functions |
| `app.py` | Added `/api/chat` POST + DELETE routes |
| `static/index.html` | Two-panel layout with chat UI + doc selector |
| `CLAUDE.md` | Updated Phase 3 checkpoint to DONE |

## Architecture notes
- Chat history is stored flat in `chat_history` table (document_id left NULL since chats can span multiple docs)
- Document selection is frontend-only state — sent with each chat request as `document_ids` array
- ChromaDB handles embedding the query automatically (same default model used for ingestion)
- System prompt instructs the model to answer from context only and match the user's language

## Next up
Phase 4 — Exam Generation (minimal): `/api/generate` endpoint, quiz UI
