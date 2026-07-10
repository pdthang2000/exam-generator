# AI Exam Generator — Architecture & Decisions

## Feature Plans

- [plan-chatbot.md](plan-chatbot.md) — Document upload, ingestion, chatbot
- [plan-exam.md](plan-exam.md) — Exam generation, quiz-taking, export

## Architecture Overview

```
Frontend (HTML/JS)                    Backend (Flask)
─────────────────                    ───────────────
Document Manager  ──── upload ────→  /api/documents     → parse, chunk, embed → ChromaDB
Chat Interface    ──── message ───→  /api/chat           → retrieve chunks → OpenAI → response
Exam Config       ──── generate ──→  /api/generate       → retrieve chunks → OpenAI → questions
Exam Quiz         ──── save ─────→  /api/exams           → store exam template
                  ──── export ───→  /api/exams/export    → JSON/MD/TXT/CSV download
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

## SQLite Schema

```sql
documents:     id, filename, file_type, upload_time, chunk_count
chat_history:  id, document_id, role, content, timestamp
exams:         id, document_id, title, questions_json, num_questions, created_at
```

- `chat_history.document_id`: scopes conversation to one document
- `questions_json`: JSON string containing the full question array
- `title`: auto-generated from document name + timestamp
- User responses are NOT stored — exported on demand instead

## Out of Scope

- No LangChain, no LangGraph
- No HuggingFace models
- No quality labeling system
- No user auth
- No Streamlit
- No Q&A (free-text) question type (future consideration)
- No AI grading of free-text answers (future consideration)
- No multi-document exams (future consideration)
