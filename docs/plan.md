# AI Exam Generator — Build Plan

## Architecture Overview

```
Frontend (HTML/JS)                    Backend (Flask)
─────────────────                    ───────────────
Document Manager  ──── upload ────→  /api/documents    → parse, chunk, embed → ChromaDB
Chat Interface    ──── message ───→  /api/chat          → retrieve chunks → OpenAI → response
Exam Page         ──── generate ──→  /api/generate      → same retrieve → OpenAI → questions
                                         │
                                     SQLite (metadata, chat history, exams)
```

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| LLM | OpenAI API (GPT-4o-mini) via course endpoint | Does everything: question gen, chat, formatting |
| Embeddings | ChromaDB default (all-MiniLM-L6-v2, local) | Course API key only allows GPT-4o-mini, no embedding access |
| Vector store | ChromaDB (persistent) | Simple, local, zero infrastructure |
| Structured data | SQLite | Exams, scores, chat history — zero config |
| Backend | Flask | Simple, reference code exists |
| Frontend | Plain HTML/JS | Full control, no framework dependency |
| File parsing | PyPDF2 + python-pptx + plain read | Minimal dependencies |
| NOT using | LangChain, LangGraph, HuggingFace models, Streamlit | See docs/suggest_review.md |

## Tech Stack

**Python dependencies:** Flask, openai, chromadb, PyPDF2, python-pptx, python-dotenv

## File Structure

```
exam-generator/
├── app.py                  # Flask app, routes, entry point
├── ingestion.py            # Parse files, chunk text, embed, store in ChromaDB
├── chat.py                 # RAG retrieval + OpenAI chat logic
├── exam.py                 # Minimal exam generation (like reference)
├── database.py             # SQLite setup + queries
├── static/
│   ├── index.html          # Main page — document manager + chat
│   └── exam.html           # Exam page (minimal, based on reference)
├── uploads/                # Raw uploaded files
├── chroma_data/            # ChromaDB persistent storage
├── exam_generator.db       # SQLite file
├── .env
├── .env.example
└── requirements.txt
```

## Build Phases

### Phase 1 — Skeleton + Document Upload

- Flask app with basic routes
- SQLite schema (documents, chat_history tables)
- File upload endpoint (PDF, PPTX, TXT)
- Parse text from each file type
- Frontend: upload area + document list

### Phase 2 — Ingestion Pipeline

- Chunk parsed text (~2000 chars / ~500 tokens, with 200-char overlap)
- Embed chunks via ChromaDB default model (local, free)
- Store in ChromaDB (persistent mode)
- Link document metadata in SQLite (chunk_count)

### Phase 3 — Chatbot (main focus)

- `/api/chat` endpoint: receive message + document context
- Retrieve top-k chunks from ChromaDB
- Build prompt with chunks + conversation history
- Stream or return OpenAI response
- Store chat messages in SQLite
- Frontend: chat UI with message history, document selector

#### Chatbot Flow

```
User selects document(s) → types question
    ↓
ChromaDB similarity search (top 5 chunks, filtered by selected docs, embedded automatically)
    ↓
Build prompt:
  - System: "Answer based on the provided context. If not in context, say so."
  - Context: [retrieved chunks]
  - History: [last N messages from SQLite]
  - User: [current question]
    ↓
OpenAI GPT-4o-mini → answer
    ↓
Save message + response to SQLite
    ↓
Return to frontend
```

### Phase 4 — Exam Generation (minimal)

- `/api/generate` endpoint: retrieve chunks → OpenAI prompt → MCQs
- Keep close to reference: hardcoded 10 questions, 4 options
- Frontend: reuse reference index.html quiz UI, adapted to work with already-uploaded documents

## SQLite Schema

```sql
documents:     id, filename, file_type, upload_time, chunk_count
chat_history:  id, document_id, role, content, timestamp
exams:         id, document_id, questions_json, created_at
```

## Out of Scope

- No LangChain, no LangGraph
- No HuggingFace models
- No quality labeling system
- No multi-export formats
- No user auth
- No Streamlit
