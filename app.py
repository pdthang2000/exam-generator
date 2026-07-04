import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from database import init_db, insert_document, get_all_documents, delete_document, update_chunk_count, clear_chat_history
from ingestion import parse_file, ingest_document, delete_document_chunks
from chat import chat as chat_answer

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

    message = data["message"].strip()
    document_ids = data.get("document_ids", [])

    try:
        answer = chat_answer(message, document_ids)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["DELETE"])
def clear_chat():
    clear_chat_history()
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


os.makedirs(UPLOAD_DIR, exist_ok=True)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
