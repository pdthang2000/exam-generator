# AI Exam Generator

## What is this
A RAG-based app with two features: chatbot Q&A over uploaded documents, and exam generation from those documents. Course final project for FSoft AI Application Engineer.

## Plans
- [docs/plan-chatbot.md](docs/plan-chatbot.md) — Document upload, ingestion, chatbot feature
- [docs/plan-exam.md](docs/plan-exam.md) — Exam generation, quiz-taking feature
- [docs/plan.md](docs/plan.md) — Architecture overview, decisions, schema

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

### Tests
```bash
python -m pytest tests/ -v
```

## Project structure
```
app.py              — Flask routes, entry point
ingestion.py        — Parse files, chunk, embed, store in ChromaDB
chat.py             — RAG retrieval + OpenAI chat
exam.py             — Exam generation + export logic
database.py         — SQLite setup + queries (documents, chat_history, exams)
static/index.html   — Two-panel UI: document sidebar + chat
static/exam.html    — Exam page: config, quiz, results
tests/              — Unit tests (pytest)
uploads/            — Raw uploaded files
chroma_data/        — ChromaDB persistent storage
```
