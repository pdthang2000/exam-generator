# AI Exam Generator

## What is this
A RAG-based app with two features: chatbot Q&A over uploaded documents, and exam generation from those documents. Course final project for FSoft AI Application Engineer.

## Full plan
See [docs/plan.md](docs/plan.md) for architecture, tech stack, file structure, and phase details.

## Tech stack
- Backend: Flask (Python)
- Frontend: Plain HTML/JS
- LLM: OpenAI API (GPT-4o-mini) via `OPENAI_BASE_URL`
- Embeddings: ChromaDB default (local, free — course API key only allows GPT-4o-mini)
- Vector store: ChromaDB (persistent, `chroma_data/`)
- Database: SQLite (`app.db`)
- File parsing: PyPDF2, python-pptx

## How to run

### Local
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in API key
python app.py          # http://localhost:8080
```

### Docker
```bash
cp .env.example .env  # fill in API key
docker compose up --build   # http://localhost:8080
```

## Project structure
```
app.py          — Flask routes, entry point
ingestion.py    — Parse files, chunk, embed, store in ChromaDB
chat.py         — RAG retrieval + OpenAI chat
exam.py         — Minimal exam generation
database.py     — SQLite setup + queries
static/         — HTML/JS frontend
uploads/        — Raw uploaded files
chroma_data/    — ChromaDB persistent storage
```

## Current checkpoint

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

### Phase 3 — Chatbot: NOT STARTED
- [ ] /api/chat endpoint
- [ ] RAG retrieval from ChromaDB
- [ ] Conversation history
- [ ] Chat UI with document selector

### Phase 4 — Exam Generation (minimal): NOT STARTED
- [ ] /api/generate endpoint
- [ ] Quiz UI (based on reference)
