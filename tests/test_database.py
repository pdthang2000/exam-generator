import json

from database import (
    insert_document, get_all_documents, delete_document, update_chunk_count,
    insert_chat_message, get_chat_history, clear_chat_history,
    insert_exam, get_all_exams, get_exam, delete_exam,
)


class TestDocuments:
    def test_insert_and_list(self):
        doc_id = insert_document("test.pdf", "pdf")
        docs = get_all_documents()
        assert len(docs) == 1
        assert docs[0]["id"] == doc_id
        assert docs[0]["filename"] == "test.pdf"

    def test_update_chunk_count(self):
        doc_id = insert_document("test.pdf", "pdf")
        update_chunk_count(doc_id, 42)
        docs = get_all_documents()
        assert docs[0]["chunk_count"] == 42

    def test_delete(self):
        doc_id = insert_document("test.pdf", "pdf")
        delete_document(doc_id)
        assert get_all_documents() == []


class TestChatHistory:
    def _make_doc(self):
        return insert_document("test.pdf", "pdf")

    def test_insert_and_get(self):
        doc_id = self._make_doc()
        insert_chat_message(doc_id, "user", "hello")
        insert_chat_message(doc_id, "assistant", "hi there")
        history = get_chat_history(doc_id, limit=10)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_scoped_to_document(self):
        doc1 = insert_document("a.pdf", "pdf")
        doc2 = insert_document("b.pdf", "pdf")
        insert_chat_message(doc1, "user", "hello doc1")
        insert_chat_message(doc2, "user", "hello doc2")
        assert len(get_chat_history(doc1)) == 1
        assert len(get_chat_history(doc2)) == 1
        assert get_chat_history(doc1)[0]["content"] == "hello doc1"

    def test_clear(self):
        doc_id = self._make_doc()
        insert_chat_message(doc_id, "user", "hello")
        clear_chat_history(doc_id)
        assert get_chat_history(doc_id) == []

    def test_clear_only_affects_target_doc(self):
        doc1 = insert_document("a.pdf", "pdf")
        doc2 = insert_document("b.pdf", "pdf")
        insert_chat_message(doc1, "user", "msg1")
        insert_chat_message(doc2, "user", "msg2")
        clear_chat_history(doc1)
        assert get_chat_history(doc1) == []
        assert len(get_chat_history(doc2)) == 1

    def test_limit(self):
        doc_id = self._make_doc()
        for i in range(5):
            insert_chat_message(doc_id, "user", f"msg {i}")
        history = get_chat_history(doc_id, limit=3)
        assert len(history) == 3
        assert history[0]["content"] == "msg 2"


class TestExams:
    def _make_questions(self):
        return [
            {
                "id": 1, "type": "mcq", "difficulty": "medium",
                "question": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "explanation": "Basic math",
            }
        ]

    def test_insert_and_list(self):
        doc_id = insert_document("test.pdf", "pdf")
        questions = self._make_questions()
        exam_id = insert_exam(doc_id, "Test Exam", json.dumps(questions), len(questions))

        exams = get_all_exams()
        assert len(exams) == 1
        assert exams[0]["id"] == exam_id
        assert exams[0]["title"] == "Test Exam"
        assert exams[0]["num_questions"] == 1
        assert exams[0]["filename"] == "test.pdf"

    def test_get_exam(self):
        doc_id = insert_document("test.pdf", "pdf")
        questions = self._make_questions()
        exam_id = insert_exam(doc_id, "Test Exam", json.dumps(questions), 1)

        exam = get_exam(exam_id)
        assert exam is not None
        assert exam["title"] == "Test Exam"
        assert json.loads(exam["questions_json"]) == questions

    def test_get_nonexistent(self):
        assert get_exam(999) is None

    def test_delete(self):
        doc_id = insert_document("test.pdf", "pdf")
        exam_id = insert_exam(doc_id, "Test", json.dumps([]), 0)
        delete_exam(exam_id)
        assert get_exam(exam_id) is None

    def test_cascade_on_document_delete(self):
        doc_id = insert_document("test.pdf", "pdf")
        insert_exam(doc_id, "Test", json.dumps([]), 0)
        delete_document(doc_id)
        assert get_all_exams() == []
