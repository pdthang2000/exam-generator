import csv
import io
import json

from exam import export_exam, export_attempt


SAMPLE_EXAM = {
    "title": "Biology Quiz",
    "filename": "bio.pdf",
    "num_questions": 2,
    "created_at": "2026-07-10",
    "questions": [
        {
            "id": 1, "type": "mcq", "difficulty": "medium",
            "question": "What is the powerhouse of the cell?",
            "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi"],
            "correct_answer": "Mitochondria",
            "explanation": "Mitochondria produce ATP.",
        },
        {
            "id": 2, "type": "true_false", "difficulty": "easy",
            "question": "DNA is double-stranded.",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "DNA has two complementary strands.",
        },
    ],
}


class TestExportExam:
    def test_json(self):
        content, ct, ext = export_exam(SAMPLE_EXAM, "json")
        data = json.loads(content)
        assert len(data) == 2
        assert data[0]["question"] == "What is the powerhouse of the cell?"
        assert ct == "application/json"
        assert ext == ".json"

    def test_markdown(self):
        content, ct, ext = export_exam(SAMPLE_EXAM, "markdown")
        assert "# Biology Quiz" in content
        assert "Mitochondria" in content
        assert ext == ".md"

    def test_text(self):
        content, ct, ext = export_exam(SAMPLE_EXAM, "text")
        assert "Biology Quiz" in content
        assert "Q1" in content
        assert ext == ".txt"

    def test_csv(self):
        content, ct, ext = export_exam(SAMPLE_EXAM, "csv")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert rows[0][0] == "id"
        assert len(rows) == 3
        assert rows[1][8] == "Mitochondria"
        assert ext == ".csv"

    def test_csv_true_false_pads_options(self):
        content, _, _ = export_exam(SAMPLE_EXAM, "csv")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        tf_row = rows[2]
        assert tf_row[4] == "True"
        assert tf_row[5] == "False"
        assert tf_row[6] == ""
        assert tf_row[7] == ""

    def test_unknown_format_falls_back_to_json(self):
        content, ct, ext = export_exam(SAMPLE_EXAM, "xml")
        assert ct == "application/json"


class TestExportAttempt:
    def test_json(self):
        answers = {"1": "Mitochondria", "2": "False"}
        score = {"correct": 1, "total": 2, "percentage": 50}
        content, ct, ext = export_attempt(SAMPLE_EXAM, answers, score, "json")
        data = json.loads(content)
        assert data["score"]["correct"] == 1
        assert data["questions"][0]["is_correct"] is True
        assert data["questions"][1]["is_correct"] is False

    def test_markdown(self):
        answers = {"1": "Nucleus", "2": "True"}
        score = {"correct": 1, "total": 2, "percentage": 50}
        content, _, _ = export_attempt(SAMPLE_EXAM, answers, score, "markdown")
        assert "Score:" in content
        assert "1/2" in content

    def test_csv(self):
        answers = {"1": "Mitochondria", "2": "True"}
        score = {"correct": 2, "total": 2, "percentage": 100}
        content, _, _ = export_attempt(SAMPLE_EXAM, answers, score, "csv")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert rows[1][-2] == "correct"
        assert rows[2][-2] == "correct"

    def test_missing_answer(self):
        answers = {}
        score = {"correct": 0, "total": 2, "percentage": 0}
        content, _, _ = export_attempt(SAMPLE_EXAM, answers, score, "text")
        assert "No answer" in content
