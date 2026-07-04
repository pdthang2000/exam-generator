# AI Exam Generator

A RAG-based app that ingests documents (PDF, PPTX, TXT), lets you chat about them, and generates exam questions using AI.

## Quick Start

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

### Docker Commands

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up --build -d

# Stop
docker compose down

# View logs (when running in background)
docker compose logs -f

# Rebuild after code changes
docker compose up --build
```

## Project Structure

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

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Plain HTML/JS
- **LLM:** OpenAI API (GPT-4o-mini)
- **Embeddings:** text-embedding-3-small
- **Vector Store:** ChromaDB (persistent)
- **Database:** SQLite
- **File Parsing:** PyPDF2, python-pptx

## Docs

- [Build Plan](docs/plan.md) — architecture, phases, and details
- [Project Target](docs/target.md) — original project brief
