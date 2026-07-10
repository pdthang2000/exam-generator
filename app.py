import json
import os
from flask import Flask, Response, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from database import (
    init_db, insert_document, get_all_documents, delete_document,
    update_chunk_count, get_chat_history, clear_chat_history,
    insert_exam, get_all_exams, get_exam, delete_exam,
)
from ingestion import parse_file, ingest_document, delete_document_chunks
from chat import chat as chat_answer
from exam import generate_questions, export_exam, export_attempt

load_dotenv()

app = Flask(__name__, static_folder="static")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "pptx", "txt"}


def get_file_type(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/documents", methods=["GET"])
def list_documents():
    return jsonify(get_all_documents())


@app.route("/api/documents", methods=["POST"])
def upload_document():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        file_type = get_file_type(file.filename)
        if file_type not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({"error": "Invalid filename"}), 400

        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        text = parse_file(file_path, file_type)
        if not text.strip():
            os.remove(file_path)
            return jsonify({"error": "Could not extract text from file"}), 400

        doc_id = insert_document(filename, file_type)

        chunk_count = ingest_document(doc_id, text)
        update_chunk_count(doc_id, chunk_count)

        return jsonify({"id": doc_id, "filename": filename, "file_type": file_type, "chunk_count": chunk_count}), 201
    except Exception as e:
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<int:doc_id>/preview", methods=["GET"])
def preview_document(doc_id):
    docs = get_all_documents()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    file_path = os.path.join(UPLOAD_DIR, doc["filename"])
    if not os.path.exists(file_path):
        return jsonify({"error": "File missing from disk"}), 404

    try:
        text = parse_file(file_path, doc["file_type"])
        return jsonify({"id": doc_id, "filename": doc["filename"], "text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "Message is required"}), 400

    document_id = data.get("document_id")
    if not document_id:
        return jsonify({"error": "document_id is required"}), 400

    message = data["message"].strip()

    try:
        answer = chat_answer(message, document_id)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat/history/<int:doc_id>", methods=["GET"])
def chat_history(doc_id):
    history = get_chat_history(doc_id, limit=50)
    return jsonify(history)


@app.route("/api/chat/<int:doc_id>", methods=["DELETE"])
def clear_chat(doc_id):
    clear_chat_history(doc_id)
    return jsonify({"ok": True})


@app.route("/api/documents/<int:doc_id>", methods=["DELETE"])
def remove_document(doc_id):
    docs = get_all_documents()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    file_path = os.path.join(UPLOAD_DIR, doc["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    delete_document_chunks(doc_id)
    delete_document(doc_id)
    return jsonify({"ok": True})


@app.route("/exam")
def exam_page():
    return send_from_directory("static", "exam.html")


@app.route("/api/generate", methods=["POST"])
def generate_exam():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    document_id = data.get("document_id")
    if not document_id:
        return jsonify({"error": "document_id is required"}), 400

    doc = next((d for d in get_all_documents() if d["id"] == document_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    num_questions = data.get("num_questions", 5)
    if not 1 <= num_questions <= 20:
        return jsonify({"error": "num_questions must be between 1 and 20"}), 400

    types = data.get("types", {})
    tf_count = types.get("true_false", 0)
    mcq_count = types.get("mcq", 0)
    if tf_count + mcq_count != num_questions:
        return jsonify({"error": "Type counts must sum to num_questions"}), 400

    difficulty = data.get("difficulty", {"easy": 33, "medium": 34, "hard": 33})
    total_pct = difficulty.get("easy", 0) + difficulty.get("medium", 0) + difficulty.get("hard", 0)
    if total_pct != 100:
        return jsonify({"error": "Difficulty percentages must sum to 100"}), 400

    try:
        questions = generate_questions(document_id, num_questions, types, difficulty)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/exams", methods=["POST"])
def save_exam():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    document_id = data.get("document_id")
    questions = data.get("questions", [])
    title = data.get("title", "Untitled Exam")

    if not questions:
        return jsonify({"error": "questions are required"}), 400

    exam_id = insert_exam(document_id, title, json.dumps(questions, ensure_ascii=False), len(questions))
    return jsonify({"id": exam_id}), 201


@app.route("/api/exams", methods=["GET"])
def list_exams():
    return jsonify(get_all_exams())


@app.route("/api/exams/<int:exam_id>", methods=["GET"])
def load_exam(exam_id):
    exam = get_exam(exam_id)
    if not exam:
        return jsonify({"error": "Exam not found"}), 404
    exam["questions"] = json.loads(exam["questions_json"])
    del exam["questions_json"]
    return jsonify(exam)


@app.route("/api/exams/<int:exam_id>", methods=["DELETE"])
def remove_exam(exam_id):
    exam = get_exam(exam_id)
    if not exam:
        return jsonify({"error": "Exam not found"}), 404
    delete_exam(exam_id)
    return jsonify({"ok": True})


@app.route("/api/exams/<int:exam_id>/export", methods=["GET"])
def export_exam_endpoint(exam_id):
    exam = get_exam(exam_id)
    if not exam:
        return jsonify({"error": "Exam not found"}), 404

    exam["questions"] = json.loads(exam["questions_json"])
    fmt = request.args.get("format", "json")
    content, content_type, ext = export_exam(exam, fmt)

    return Response(
        content,
        mimetype=content_type,
        headers={"Content-Disposition": f"attachment; filename=exam_{exam_id}{ext}"},
    )


@app.route("/api/exams/export-attempt", methods=["POST"])
def export_attempt_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    questions = data.get("questions", [])
    answers = data.get("answers", {})
    score = data.get("score", {})
    title = data.get("title", "Exam Attempt")
    fmt = request.args.get("format", "json")

    exam = {
        "title": title,
        "filename": data.get("filename", "N/A"),
        "num_questions": len(questions),
        "created_at": data.get("created_at", "N/A"),
        "questions": questions,
    }

    content, content_type, ext = export_attempt(exam, answers, score, fmt)

    return Response(
        content,
        mimetype=content_type,
        headers={"Content-Disposition": f"attachment; filename=attempt{ext}"},
    )


os.makedirs(UPLOAD_DIR, exist_ok=True)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
