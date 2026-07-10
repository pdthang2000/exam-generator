import csv
import io
import json
import math
import os

from openai import OpenAI

from ingestion import get_chroma_collection

SYSTEM_PROMPT = """You are an exam question generator. Generate exam questions based ONLY on the provided context.

Return a valid JSON array of question objects. Each object must have exactly these fields:
- "id": sequential integer starting from 1
- "type": either "true_false" or "mcq"
- "difficulty": one of "easy", "medium", "hard"
- "question": the question text
- "options": for true_false: ["True", "False"]; for mcq: array of 4 distinct choices
- "correct_answer": the correct option (must exactly match one of the options)
- "explanation": brief explanation of why the answer is correct

Return ONLY the JSON array, no other text."""


def get_openai_client():
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )


def retrieve_chunks(document_id, n_results=10):
    collection = get_chroma_collection()
    results = collection.get(
        where={"document_id": document_id},
        limit=n_results,
    )
    return results["documents"] if results["documents"] else []


def generate_questions(document_id, num_questions, types, difficulty):
    chunks = retrieve_chunks(document_id)
    if not chunks:
        raise ValueError("No content found for this document")

    context = "\n\n---\n\n".join(chunks)

    tf_count = types.get("true_false", 0)
    mcq_count = types.get("mcq", 0)

    easy_pct = difficulty.get("easy", 33)
    medium_pct = difficulty.get("medium", 34)
    hard_pct = difficulty.get("hard", 33)

    easy_count = math.floor(num_questions * easy_pct / 100)
    hard_count = math.floor(num_questions * hard_pct / 100)
    medium_count = num_questions - easy_count - hard_count

    user_prompt = (
        f"Generate exactly {num_questions} exam questions from the context above.\n"
        f"Question types: {tf_count} true/false, {mcq_count} multiple choice (4 options each).\n"
        f"Difficulty distribution: {easy_count} easy, {medium_count} medium, {hard_count} hard.\n"
        f"Return ONLY a valid JSON array."
    )

    client = get_openai_client()
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Context from document:\n\n{context}"},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    questions = json.loads(raw)

    for i, q in enumerate(questions):
        q["id"] = i + 1
        if q.get("type") not in ("true_false", "mcq"):
            q["type"] = "mcq"
        if q.get("difficulty") not in ("easy", "medium", "hard"):
            q["difficulty"] = "medium"
        if q["type"] == "true_false":
            q["options"] = ["True", "False"]
        if q.get("correct_answer") not in q.get("options", []):
            q["correct_answer"] = q["options"][0]

    return questions


def export_exam_json(exam):
    return json.dumps(exam["questions"], indent=2, ensure_ascii=False)


def export_exam_markdown(exam):
    lines = [
        f"# {exam['title']}",
        f"**Document:** {exam.get('filename', 'N/A')} | "
        f"**Questions:** {exam['num_questions']} | "
        f"**Date:** {exam.get('created_at', 'N/A')}",
        "",
        "---",
        "",
    ]

    for q in exam["questions"]:
        lines.append(f"### Q{q['id']} [{q['type'].upper().replace('_', '/')} | {q['difficulty'].capitalize()}]")
        lines.append(q["question"])
        lines.append("")
        for opt in q["options"]:
            marker = " ✓" if opt == q["correct_answer"] else ""
            lines.append(f"- {opt}{marker}")
        lines.append("")
        lines.append(f"**Explanation:** {q.get('explanation', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def export_exam_text(exam):
    lines = [
        exam["title"],
        f"Document: {exam.get('filename', 'N/A')} | "
        f"Questions: {exam['num_questions']} | "
        f"Date: {exam.get('created_at', 'N/A')}",
        "",
    ]

    for q in exam["questions"]:
        lines.append(f"Q{q['id']} [{q['type']} | {q['difficulty']}]")
        lines.append(q["question"])
        for i, opt in enumerate(q["options"]):
            marker = " (correct)" if opt == q["correct_answer"] else ""
            lines.append(f"  {chr(65 + i)}) {opt}{marker}")
        lines.append(f"Explanation: {q.get('explanation', '')}")
        lines.append("")

    return "\n".join(lines)


def export_exam_csv(exam):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "type", "difficulty", "question",
                     "option_a", "option_b", "option_c", "option_d",
                     "correct_answer", "explanation"])

    for q in exam["questions"]:
        opts = q["options"] + [""] * (4 - len(q["options"]))
        writer.writerow([
            q["id"], q["type"], q["difficulty"], q["question"],
            opts[0], opts[1], opts[2], opts[3],
            q["correct_answer"], q.get("explanation", ""),
        ])

    return output.getvalue()


EXPORTERS = {
    "json": (export_exam_json, "application/json", ".json"),
    "markdown": (export_exam_markdown, "text/markdown", ".md"),
    "text": (export_exam_text, "text/plain", ".txt"),
    "csv": (export_exam_csv, "text/csv", ".csv"),
}


def export_exam(exam, fmt="json"):
    exporter, content_type, ext = EXPORTERS.get(fmt, EXPORTERS["json"])
    content = exporter(exam)
    return content, content_type, ext


def export_attempt_markdown(exam, answers, score):
    lines = [
        f"# Exam Results: {exam['title']}",
        f"**Score:** {score['correct']}/{score['total']} ({score['percentage']}%)",
        f"**Document:** {exam.get('filename', 'N/A')} | **Date:** {exam.get('created_at', 'N/A')}",
        "",
        "---",
        "",
    ]

    for q in exam["questions"]:
        qid = str(q["id"])
        user_answer = answers.get(qid, "No answer")
        is_correct = user_answer == q["correct_answer"]
        marker = "✓" if is_correct else "✗"

        lines.append(f"### Q{q['id']} [{q['type'].upper().replace('_', '/')} | {q['difficulty'].capitalize()}] {marker}")
        lines.append(q["question"])
        lines.append("")
        for opt in q["options"]:
            prefix = ""
            if opt == q["correct_answer"] and opt == user_answer:
                prefix = "✓ "
            elif opt == q["correct_answer"]:
                prefix = "← correct "
            elif opt == user_answer:
                prefix = "✗ "
            lines.append(f"- {prefix}{opt}")
        lines.append("")
        lines.append(f"**Explanation:** {q.get('explanation', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def export_attempt_text(exam, answers, score):
    lines = [
        f"Exam Results: {exam['title']}",
        f"Score: {score['correct']}/{score['total']} ({score['percentage']}%)",
        f"Document: {exam.get('filename', 'N/A')} | Date: {exam.get('created_at', 'N/A')}",
        "",
    ]

    for q in exam["questions"]:
        qid = str(q["id"])
        user_answer = answers.get(qid, "No answer")
        is_correct = user_answer == q["correct_answer"]
        marker = "CORRECT" if is_correct else "WRONG"

        lines.append(f"Q{q['id']} [{q['type']} | {q['difficulty']}] - {marker}")
        lines.append(q["question"])
        lines.append(f"  Your answer: {user_answer}")
        lines.append(f"  Correct answer: {q['correct_answer']}")
        lines.append(f"  Explanation: {q.get('explanation', '')}")
        lines.append("")

    return "\n".join(lines)


def export_attempt_csv(exam, answers, score):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "type", "difficulty", "question",
                     "correct_answer", "your_answer", "result", "explanation"])

    for q in exam["questions"]:
        qid = str(q["id"])
        user_answer = answers.get(qid, "No answer")
        is_correct = user_answer == q["correct_answer"]
        writer.writerow([
            q["id"], q["type"], q["difficulty"], q["question"],
            q["correct_answer"], user_answer,
            "correct" if is_correct else "wrong",
            q.get("explanation", ""),
        ])

    return output.getvalue()


def export_attempt_json(exam, answers, score):
    result = {
        "title": exam["title"],
        "score": score,
        "questions": [],
    }
    for q in exam["questions"]:
        qid = str(q["id"])
        user_answer = answers.get(qid, "No answer")
        result["questions"].append({
            **q,
            "user_answer": user_answer,
            "is_correct": user_answer == q["correct_answer"],
        })
    return json.dumps(result, indent=2, ensure_ascii=False)


ATTEMPT_EXPORTERS = {
    "json": (export_attempt_json, "application/json", ".json"),
    "markdown": (export_attempt_markdown, "text/markdown", ".md"),
    "text": (export_attempt_text, "text/plain", ".txt"),
    "csv": (export_attempt_csv, "text/csv", ".csv"),
}


def export_attempt(exam, answers, score, fmt="json"):
    exporter, content_type, ext = ATTEMPT_EXPORTERS.get(fmt, ATTEMPT_EXPORTERS["json"])
    content = exporter(exam, answers, score)
    return content, content_type, ext
