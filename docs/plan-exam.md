# Exam Generation Feature Plan

Covers exam generation, quiz-taking UI, and export.

## Exam Generation Flow

```
User selects document → configures exam (count, types, difficulty)
    ↓
POST /api/generate
    ↓
ChromaDB similarity search (top-k chunks from selected document)
    ↓
Build prompt:
  - System: "Generate exam questions from the provided context.
             Return valid JSON array. Each question has:
             type, difficulty, question, options, correct_answer, explanation."
  - Context: [retrieved chunks]
  - User: "Generate N questions: X true/false, Y MCQ.
           Difficulty: A% easy, B% medium, C% hard."
    ↓
OpenAI GPT-4o-mini → JSON array of questions
    ↓
Validate JSON structure, return to frontend
    ↓
User takes quiz (practice or exam mode)
    ↓
Optional: save exam (POST /api/exams) or export results
```

## Question JSON Schema

```json
{
  "id": 1,
  "type": "mcq",
  "difficulty": "medium",
  "question": "What is the primary function of mitochondria?",
  "options": ["Protein synthesis", "Energy production", "Cell division", "Waste removal"],
  "correct_answer": "Energy production",
  "explanation": "Mitochondria are known as the powerhouse of the cell..."
}
```

```json
{
  "id": 2,
  "type": "true_false",
  "difficulty": "easy",
  "question": "DNA is a double-stranded helix.",
  "options": ["True", "False"],
  "correct_answer": "True",
  "explanation": "DNA consists of two complementary strands..."
}
```

## Export Formats

- **JSON** — raw data, same as internal format
- **Markdown** — human-readable study sheet with correct answers marked
- **CSV** — spreadsheet-friendly, one row per question
- **Text** — plain text, similar to Markdown but no formatting

## Checkpoints

### Phase 4A — Backend: Generation + Storage: DONE
- [x] /api/generate endpoint (configurable: question count, types, difficulty split)
- [x] Prompt engineering for true/false + MCQ generation with structured JSON output
- [x] /api/exams CRUD endpoints (save, list, load, delete)
- [x] /api/exams export endpoints (exam template + attempt results)
- [x] Export formats: JSON, Markdown, plain text, CSV
- [x] Update SQLite schema (exams table: add title, num_questions columns)

### Phase 4B — Frontend: Exam Configuration UI: DONE
- [x] exam.html — document selector, question count (1-20), type split, difficulty split
- [x] Difficulty presets (Easy/Balanced/Hard) + custom sliders
- [x] Client-side validation (types sum to total, difficulty sums to 100%)

### Phase 4C — Frontend: Quiz-Taking UI: DONE
- [x] Practice mode (one-at-a-time, immediate feedback, running score)
- [x] Exam mode (all questions, unanswered warning, grade on submit)
- [x] Results view (score, per-question breakdown with correct/wrong indicators, explanations)
- [x] Post-quiz actions: save exam, export exam (JSON/MD/TXT/CSV), export results (JSON/MD/TXT/CSV), retake, new exam
