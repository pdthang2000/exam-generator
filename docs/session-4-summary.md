# Session 4 Summary — Phase 4: Exam Generation + Frontend Refactor

## What was done

### New file: `exam.py`
- `generate_exam(document_id, num_questions, num_mcq, num_tf, easy_pct, medium_pct, hard_pct)` — retrieves chunks from ChromaDB, builds a prompt specifying question count/types/difficulty split, calls OpenAI GPT-4o-mini, returns validated JSON array of questions
- Each question: `{id, type, difficulty, question, options, correct_answer, explanation}`
- Supports two question types: `mcq` (4 options) and `true_false` (True/False)
- `export_exam_template(questions, fmt)` / `export_exam_attempt(questions, answers, score, fmt)` — export in JSON, Markdown, plain text, or CSV

### New file: `static/exam.html`
- Document selector dropdown (populated from `/api/documents`)
- Question count slider (1–20), type split (MCQ vs true/false), difficulty presets (Easy/Balanced/Hard/Custom)
- Client-side validation: types must sum to total, difficulty must sum to 100%
- Two quiz modes:
  - **Practice mode**: one question at a time, immediate feedback with explanation, running score
  - **Exam mode**: all questions shown, unanswered warning on submit, grade at end
- Results view: score, per-question breakdown (correct/wrong indicators, explanations)
- Post-quiz actions: save exam, export exam template, export results, retake, new exam

### Updated: `app.py`
- `POST /api/generate` — validates config (types sum, difficulty sums to 100%), calls `generate_exam()`, returns questions JSON
- `POST /api/exams` — save exam (title, questions, linked to document)
- `GET /api/exams` — list saved exams (optionally filtered by document_id)
- `GET /api/exams/<id>` — load single exam
- `DELETE /api/exams/<id>` — delete exam
- `POST /api/exams/<id>/export` — export exam template or attempt results
- `GET /api/chat/history/<doc_id>` — load conversation history when switching documents
- `DELETE /api/chat/<doc_id>` — clear only that document's chat history

### Updated: `database.py`
- `insert_exam()`, `get_exams()`, `get_exam()`, `delete_exam()` — full CRUD for exams table
- SQLite migration: added `title` and `num_questions` columns to exams table (with ALTER TABLE fallback for existing DBs)
- Chat history functions now scoped by `document_id`: `insert_chat_message(document_id, ...)`, `get_chat_history(document_id, ...)`, `clear_chat_history(document_id)`

### Updated: `chat.py`
- Changed from multi-document to single-document: `retrieve_chunks(query, document_id)` and `chat(message, document_id)`
- Removed `$in` operator logic — simplified to single document filter

### Updated: `static/index.html`
- Changed from multi-document selection (Set of IDs) to single-document selection
- Chat input disabled when no document selected
- Switching documents loads that document's conversation history via new API
- Clear Chat clears only the selected document's history
- Added centered loading spinner when loading a document's chat history
- Navigation link to exam page

### Frontend refactor (second commit)
- Split `index.html` inline JS (257 lines) into 4 modules: `index-state.js`, `index-upload.js`, `index-documents.js`, `index-chat.js`
- Split `exam.html` inline JS (640 lines) into 5 modules: `exam-state.js`, `exam-config.js`, `exam-modes.js`, `exam-results.js`, `exam-export.js`
- Extracted inline CSS into `index.css` (372 lines) and `exam.css` (401 lines)
- Improved chat loading UX: centered 32px spinner with text, replacing small inline spinner

### Tests: 47 pytest tests
- `tests/test_database.py` — document CRUD, chat history (per-document), exam CRUD
- `tests/test_exam_export.py` — all 4 export formats for both exam templates and attempt results
- `tests/test_routes.py` — all API routes (upload, documents, chat, generate, exams, export)
- `tests/conftest.py` — shared fixtures (temp app, temp DB, sample questions)

### Docs restructuring
- Split `docs/plan.md` into `docs/plan-chatbot.md` and `docs/plan-exam.md` (feature-specific checkpoints)
- `docs/plan.md` slimmed to architecture overview, decisions, and schema only
- `CLAUDE.md` slimmed to high-level project overview

## Bug fixed: multi-document chat selection
- **What**: chat sidebar allowed selecting multiple documents simultaneously
- **Why**: used a `Set` for `selectedDocIds`, backend had `$in` filter logic for ChromaDB
- **How**: changed to single `selectedDocId`, simplified backend to filter by one document, scoped chat history per document

## Files changed

| File | Change |
|---|---|
| `exam.py` | New — exam generation, export logic |
| `static/exam.html` | New — exam config + quiz + results UI |
| `static/exam.css` | New — extracted exam page styles |
| `static/index.css` | New — extracted chat page styles |
| `static/js/exam-state.js` | New — shared exam state |
| `static/js/exam-config.js` | New — exam configuration panel |
| `static/js/exam-modes.js` | New — practice + exam mode logic |
| `static/js/exam-results.js` | New — results view rendering |
| `static/js/exam-export.js` | New — client-side export actions |
| `static/js/index-state.js` | New — shared chat state |
| `static/js/index-upload.js` | New — file upload handling |
| `static/js/index-documents.js` | New — document list + selection |
| `static/js/index-chat.js` | New — chat send/receive/clear |
| `tests/conftest.py` | New — pytest fixtures |
| `tests/test_database.py` | New — 17 database tests |
| `tests/test_exam_export.py` | New — 12 export tests |
| `tests/test_routes.py` | New — 18 route tests |
| `app.py` | Added exam + export routes, per-doc chat routes |
| `chat.py` | Simplified to single-document |
| `database.py` | Added exam CRUD, per-doc chat, migration |
| `static/index.html` | Single-doc selection, loading spinner, CSS/JS extracted |
| `docs/plan.md` | Slimmed to architecture only |
| `docs/plan-chatbot.md` | New — chatbot checkpoints |
| `docs/plan-exam.md` | New — exam checkpoints |
| `CLAUDE.md` | Slimmed to high-level overview |

## Architecture notes
- Exam questions generated in a single OpenAI call with structured JSON output
- Exams stored as `questions_json` blob in SQLite — no separate questions table
- Export happens server-side for saved exams, client-side for unsaved results
- Chat history now properly scoped: one document = one conversation thread
- Frontend JS modules use global state objects (`AppState`, `ExamState`) — no build step needed

## Git state

- Branch: `main`
- Commits: `5c4de8e` (Phase 4A+4B) and `158880a` (frontend refactor)
- Working tree: clean

## Next up
- Phase 4C marked DONE — quiz-taking UI is complete
- Potential future: Q&A (free-text) questions, AI grading, multi-document exams
