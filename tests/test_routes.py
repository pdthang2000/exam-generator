import json
import os
import io

import pytest

import database
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    upload_dir = str(tmp_path / "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    monkeypatch.setattr("app.UPLOAD_DIR", upload_dir)

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload_txt(client, filename="test.txt", content="Hello world. This is test content for chunking."):
    data = {"file": (io.BytesIO(content.encode()), filename)}
    return client.post("/api/documents", data=data, content_type="multipart/form-data")


class TestDocumentRoutes:
    def test_list_empty(self, client):
        res = client.get("/api/documents")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_upload_and_list(self, client):
        res = _upload_txt(client)
        assert res.status_code == 201
        data = res.get_json()
        assert data["filename"] == "test.txt"
        assert data["chunk_count"] >= 1

        res = client.get("/api/documents")
        assert len(res.get_json()) == 1

    def test_upload_bad_type(self, client):
        data = {"file": (io.BytesIO(b"data"), "test.exe")}
        res = client.post("/api/documents", data=data, content_type="multipart/form-data")
        assert res.status_code == 400

    def test_delete(self, client):
        _upload_txt(client)
        docs = client.get("/api/documents").get_json()
        res = client.delete(f"/api/documents/{docs[0]['id']}")
        assert res.status_code == 200
        assert client.get("/api/documents").get_json() == []

    def test_delete_nonexistent(self, client):
        res = client.delete("/api/documents/999")
        assert res.status_code == 404


class TestChatRoutes:
    def test_empty_message(self, client):
        res = client.post("/api/chat", json={"message": "", "document_id": 1})
        assert res.status_code == 400

    def test_no_body(self, client):
        res = client.post("/api/chat", content_type="application/json")
        assert res.status_code == 400

    def test_missing_document_id(self, client):
        res = client.post("/api/chat", json={"message": "hello"})
        assert res.status_code == 400
        assert "document_id" in res.get_json()["error"]

    def test_clear(self, client):
        _upload_txt(client)
        docs = client.get("/api/documents").get_json()
        res = client.delete(f"/api/chat/{docs[0]['id']}")
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

    def test_history_empty(self, client):
        _upload_txt(client)
        docs = client.get("/api/documents").get_json()
        res = client.get(f"/api/chat/history/{docs[0]['id']}")
        assert res.status_code == 200
        assert res.get_json() == []


class TestExamCrudRoutes:
    def _save_exam(self, client, doc_id=None):
        questions = [
            {
                "id": 1, "type": "mcq", "difficulty": "easy",
                "question": "Q?", "options": ["A", "B", "C", "D"],
                "correct_answer": "A", "explanation": "Because.",
            }
        ]
        return client.post("/api/exams", json={
            "document_id": doc_id,
            "title": "My Exam",
            "questions": questions,
        })

    def test_save_and_list(self, client):
        res = self._save_exam(client)
        assert res.status_code == 201
        exam_id = res.get_json()["id"]

        res = client.get("/api/exams")
        exams = res.get_json()
        assert len(exams) == 1
        assert exams[0]["title"] == "My Exam"

    def test_load(self, client):
        res = self._save_exam(client)
        exam_id = res.get_json()["id"]

        res = client.get(f"/api/exams/{exam_id}")
        data = res.get_json()
        assert data["title"] == "My Exam"
        assert len(data["questions"]) == 1
        assert "questions_json" not in data

    def test_load_nonexistent(self, client):
        res = client.get("/api/exams/999")
        assert res.status_code == 404

    def test_delete(self, client):
        res = self._save_exam(client)
        exam_id = res.get_json()["id"]

        res = client.delete(f"/api/exams/{exam_id}")
        assert res.status_code == 200

        res = client.get(f"/api/exams/{exam_id}")
        assert res.status_code == 404

    def test_save_no_questions(self, client):
        res = client.post("/api/exams", json={"title": "Empty"})
        assert res.status_code == 400

    def test_export_json(self, client):
        exam_id = self._save_exam(client).get_json()["id"]
        res = client.get(f"/api/exams/{exam_id}/export?format=json")
        assert res.status_code == 200
        assert res.content_type.startswith("application/json")
        data = json.loads(res.data)
        assert isinstance(data, str) or isinstance(data, list)

    def test_export_csv(self, client):
        exam_id = self._save_exam(client).get_json()["id"]
        res = client.get(f"/api/exams/{exam_id}/export?format=csv")
        assert res.status_code == 200
        assert "csv" in res.content_type

    def test_export_nonexistent(self, client):
        res = client.get("/api/exams/999/export?format=json")
        assert res.status_code == 404


class TestExportAttemptRoute:
    def test_export_attempt(self, client):
        res = client.post(
            "/api/exams/export-attempt?format=json",
            json={
                "title": "My Attempt",
                "questions": [
                    {
                        "id": 1, "type": "mcq", "difficulty": "easy",
                        "question": "Q?", "options": ["A", "B"],
                        "correct_answer": "A", "explanation": "Yes.",
                    }
                ],
                "answers": {"1": "A"},
                "score": {"correct": 1, "total": 1, "percentage": 100},
            },
        )
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data["score"]["correct"] == 1

    def test_no_body(self, client):
        res = client.post("/api/exams/export-attempt", content_type="application/json")
        assert res.status_code == 400


class TestGenerateRoute:
    def test_missing_document_id(self, client):
        res = client.post("/api/generate", json={"num_questions": 5})
        assert res.status_code == 400

    def test_nonexistent_document(self, client):
        res = client.post("/api/generate", json={
            "document_id": 999,
            "num_questions": 5,
            "types": {"true_false": 2, "mcq": 3},
            "difficulty": {"easy": 33, "medium": 34, "hard": 33},
        })
        assert res.status_code == 404

    def test_type_sum_mismatch(self, client):
        _upload_txt(client)
        docs = client.get("/api/documents").get_json()
        res = client.post("/api/generate", json={
            "document_id": docs[0]["id"],
            "num_questions": 5,
            "types": {"true_false": 1, "mcq": 1},
            "difficulty": {"easy": 33, "medium": 34, "hard": 33},
        })
        assert res.status_code == 400
        assert "sum" in res.get_json()["error"].lower()

    def test_difficulty_sum_mismatch(self, client):
        _upload_txt(client)
        docs = client.get("/api/documents").get_json()
        res = client.post("/api/generate", json={
            "document_id": docs[0]["id"],
            "num_questions": 5,
            "types": {"true_false": 2, "mcq": 3},
            "difficulty": {"easy": 50, "medium": 50, "hard": 50},
        })
        assert res.status_code == 400
        assert "100" in res.get_json()["error"]
