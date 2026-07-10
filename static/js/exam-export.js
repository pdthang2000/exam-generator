function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type: type });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function exportExam(fmt) {
  if (!generatedQuestions) return;
  const exam = {
    title: getExamTitle(),
    filename: getDocInfo().filename,
    num_questions: generatedQuestions.length,
    created_at: new Date().toISOString(),
    questions: generatedQuestions,
  };

  const EXT = { json: ".json", markdown: ".md", text: ".txt", csv: ".csv" };
  const MIME = { json: "application/json", markdown: "text/markdown", text: "text/plain", csv: "text/csv" };
  let content;

  if (fmt === "json") {
    content = JSON.stringify(generatedQuestions, null, 2);
  } else if (fmt === "csv") {
    content = buildCsv(generatedQuestions);
  } else if (fmt === "markdown") {
    content = buildExamMd(exam);
  } else {
    content = buildExamTxt(exam);
  }

  downloadFile(content, "exam" + (EXT[fmt] || ".txt"), MIME[fmt] || "text/plain");
}

function exportResults(fmt) {
  if (!generatedQuestions) return;
  const score = computeScore();
  const exam = {
    title: getExamTitle(),
    filename: getDocInfo().filename,
    num_questions: generatedQuestions.length,
    created_at: new Date().toISOString(),
    questions: generatedQuestions,
  };

  const EXT = { json: ".json", markdown: ".md", text: ".txt", csv: ".csv" };

  fetch("/api/exams/export-attempt?format=" + fmt, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: exam.title, filename: exam.filename, created_at: exam.created_at, questions: generatedQuestions, answers: userAnswers, score: score }),
  })
  .then(res => res.blob())
  .then(blob => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "results" + (EXT[fmt] || ".txt");
    a.click();
    URL.revokeObjectURL(a.href);
  })
  .catch(err => alert("Export failed: " + err.message));
}

function buildCsv(questions) {
  const rows = [["id","type","difficulty","question","option_a","option_b","option_c","option_d","correct_answer","explanation"]];
  for (const q of questions) {
    const opts = [...q.options]; while (opts.length < 4) opts.push("");
    rows.push([q.id, q.type, q.difficulty, q.question, opts[0], opts[1], opts[2], opts[3], q.correct_answer, q.explanation || ""]);
  }
  return rows.map(r => r.map(c => '"' + String(c).replace(/"/g, '""') + '"').join(",")).join("\n");
}

function buildExamMd(exam) {
  let md = "# " + exam.title + "\n**Document:** " + exam.filename + " | **Questions:** " + exam.num_questions + "\n\n---\n\n";
  for (const q of exam.questions) {
    md += "### Q" + q.id + " [" + q.type.toUpperCase().replace("_", "/") + " | " + q.difficulty[0].toUpperCase() + q.difficulty.slice(1) + "]\n" + q.question + "\n\n";
    for (const opt of q.options) md += "- " + opt + (opt === q.correct_answer ? " ✓" : "") + "\n";
    md += "\n**Explanation:** " + (q.explanation || "") + "\n\n---\n\n";
  }
  return md;
}

function buildExamTxt(exam) {
  let txt = exam.title + "\nDocument: " + exam.filename + " | Questions: " + exam.num_questions + "\n\n";
  for (const q of exam.questions) {
    txt += "Q" + q.id + " [" + q.type + " | " + q.difficulty + "]\n" + q.question + "\n";
    q.options.forEach((opt, i) => { txt += "  " + String.fromCharCode(65 + i) + ") " + opt + (opt === q.correct_answer ? " (correct)" : "") + "\n"; });
    txt += "Explanation: " + (q.explanation || "") + "\n\n";
  }
  return txt;
}

// --- Init ---
loadDocuments();
updateTypeHint();
updateDifficultyDisplay();
