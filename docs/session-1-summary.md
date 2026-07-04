# Session 1 Summary — Phase 1 Complete

## What's been done

### Files created/modified

| File | Purpose |
|---|---|
| `app.py` | Flask app with routes: `GET /` (serve frontend), `GET /api/documents` (list), `POST /api/documents` (upload), `GET /api/documents/<id>/preview` (extracted text), `DELETE /api/documents/<id>` (remove). Entire upload route wrapped in try/except to always return JSON. `init_db()` and `makedirs` run at module level (not inside `__main__`). |
| `database.py` | SQLite with 3 tables: `documents`, `chat_history`, `exams`. DB path uses `os.path.dirname(__file__)` for absolute path. DB filename is `app.db` (not `exam_generator.db` — that name was blocked by sandbox). |
| `ingestion.py` | Parsers for PDF (PyPDF2), PPTX (python-pptx), TXT. Exports `parse_file(path, type)`. Only parsing — no chunking/embedding yet. |
| `static/index.html` | Upload UI with drag-and-drop, document list with preview modal and remove button. Uses `res.text()` + `JSON.parse()` instead of `res.json()` to handle non-JSON error responses. |
| `requirements.txt` | flask, openai, chromadb, PyPDF2, python-pptx, python-dotenv |
| `.env.example` | `OPENAI_BASE_URL` and `OPENAI_API_KEY` |
| `Dockerfile` | Python 3.11 slim, single container |
| `docker-compose.yml` | One service, volumes for `uploads/`, `chroma_data/`, `app.db` |
| `.gitignore` | Ignores `__pycache__`, `.env`, `venv/`, `uploads/*`, `chroma_data/`, `app.db` |
| `.dockerignore` | Excludes venv, .env, .git, docs, references from build |
| `README.md` | Project overview + local/Docker run instructions |
| `docs/target.md` | Original project brief (moved from README) |
| `CLAUDE.md` | Updated checkpoint — Phase 1 marked DONE |

### Bugs fixed along the way

1. **DB filename** — `exam_generator.db` was blocked by sandbox; renamed to `app.db` everywhere
2. **DB path** — changed from relative `"app.db"` to `os.path.join(os.path.dirname(__file__), "app.db")` so it works from any working directory
3. **`init_db()` placement** — moved from `__main__` to module level so it runs regardless of how the app starts (debug reloader, Docker, gunicorn)
4. **JSON error responses** — wrapped entire upload route in try/except; Flask was returning HTML 500 pages causing `Unexpected token '<'` in frontend
5. **Frontend JSON parsing** — changed `res.json()` to `res.text()` + `JSON.parse()` with fallback

## What's next

- **Phase 2**: Chunking + embedding uploaded docs into ChromaDB
- **Phase 3**: Chatbot (RAG retrieval + OpenAI chat)
- **Phase 4**: Exam generation (MCQ quiz from documents)

## Git state

- Branch: `main`
- Latest commit: `cd0f88f` — "Phase 1: skeleton, document upload, and Docker setup"
- Working tree: clean
