import os
import json
from flask import Flask, request, jsonify, send_from_directory
import openai
import PyPDF2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")
client = openai.OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)


def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def generate_questions(text: str) -> list[dict]:
    prompt = f"""You are an exam generator. Based on the following text, create exactly 10 multiple choice questions.

Rules:
- Each question must have exactly 4 options labeled A, B, C, D
- Only one option is correct
- Questions should test understanding of key concepts in the text
- Return ONLY valid JSON, no extra text

Return this exact JSON structure:
[
  {{
    "question": "...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A"
  }}
]

Text:
{text[:12000]}"""

    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    # Handle both {"questions": [...]} and [...] responses
    if isinstance(data, list):
        return data
    for key in data:
        if isinstance(data[key], list):
            return data[key]
    raise ValueError("Unexpected response format from OpenAI")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files["pdf"]
    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF"}), 400

    try:
        text = extract_text_from_pdf(pdf_file)
        if not text.strip():
            return jsonify({"error": "Could not extract text from PDF"}), 400

        questions = generate_questions(text)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)
