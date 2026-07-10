function computeScore() {
  let correct = 0;
  for (const q of generatedQuestions) {
    if (userAnswers[String(q.id)] === q.correct_answer) correct++;
  }
  const total = generatedQuestions.length;
  return { correct, total, percentage: Math.round(correct / total * 100) };
}

function showResults() {
  const score = computeScore();
  const area = document.getElementById("phase-results");

  let html = '<div class="card">';
  html += '<div class="results-header">';
  html += '<div class="results-score">' + score.correct + '/' + score.total + '</div>';
  html += '<div class="results-label">' + score.percentage + '% correct</div>';
  html += '</div>';

  for (const q of generatedQuestions) {
    const chosen = userAnswers[String(q.id)] || "No answer";
    const isCorrect = chosen === q.correct_answer;

    const typeBadge = q.type === "true_false"
      ? '<span class="badge badge-tf">T/F</span>'
      : '<span class="badge badge-mcq">MCQ</span>';
    const diffBadge = '<span class="badge badge-' + q.difficulty + '">' + q.difficulty + '</span>';

    html += '<div class="q-card">';
    html += '<div class="q-header">';
    html += '<span class="result-indicator ' + (isCorrect ? 'correct' : 'wrong') + '">' + (isCorrect ? '&#10003;' : '&#10007;') + '</span>';
    html += '<span class="q-num">Q' + q.id + '</span>' + typeBadge + diffBadge;
    html += '</div>';
    html += '<div class="q-text">' + escapeHtml(q.question) + '</div>';
    html += '<ul class="q-options">';
    for (const opt of q.options) {
      let cls = "disabled";
      if (opt === q.correct_answer && opt === chosen) cls += " correct-reveal";
      else if (opt === q.correct_answer) cls += " correct-reveal";
      else if (opt === chosen) cls += " wrong-reveal";
      html += '<li class="' + cls + '">' + escapeHtml(opt);
      if (opt === chosen && opt !== q.correct_answer) html += ' <small>(your answer)</small>';
      if (opt === q.correct_answer && opt !== chosen) html += ' <small>(correct)</small>';
      html += '</li>';
    }
    html += '</ul>';
    if (q.explanation) {
      html += '<div class="q-explanation">' + escapeHtml(q.explanation) + '</div>';
    }
    html += '</div>';
  }

  html += '<div class="post-actions">';
  html += '<button class="btn-outline" onclick="saveExam()">Save Exam</button>';
  html += '<button class="btn-outline" onclick="retakeQuiz()">Retake</button>';
  html += '<button class="btn-outline" onclick="newExam()">New Exam</button>';
  html += '</div>';

  html += '<div class="post-actions" style="margin-top:8px">';
  html += '<div class="export-group"><label>Export Exam:</label>';
  html += '<button class="btn-secondary" onclick="exportExam(\'json\')">JSON</button>';
  html += '<button class="btn-secondary" onclick="exportExam(\'markdown\')">MD</button>';
  html += '<button class="btn-secondary" onclick="exportExam(\'text\')">TXT</button>';
  html += '<button class="btn-secondary" onclick="exportExam(\'csv\')">CSV</button>';
  html += '</div>';
  html += '<div class="export-group"><label>Export Results:</label>';
  html += '<button class="btn-secondary" onclick="exportResults(\'json\')">JSON</button>';
  html += '<button class="btn-secondary" onclick="exportResults(\'markdown\')">MD</button>';
  html += '<button class="btn-secondary" onclick="exportResults(\'text\')">TXT</button>';
  html += '<button class="btn-secondary" onclick="exportResults(\'csv\')">CSV</button>';
  html += '</div>';
  html += '</div>';

  html += '</div>';
  area.innerHTML = html;
  showPhase("results");
}

async function saveExam() {
  if (!generatedQuestions) return;
  try {
    const res = await fetch("/api/exams", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_id: getDocInfo().id,
        title: getExamTitle(),
        questions: generatedQuestions,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Save failed");
    alert("Exam saved (ID: " + data.id + ")");
  } catch (err) {
    alert("Error: " + err.message);
  }
}

function retakeQuiz() {
  userAnswers = {};
  practiceIndex = 0;
  practiceScore = 0;
  if (quizMode === "practice") {
    renderPracticeQuestion();
  } else {
    renderExamMode();
  }
  showPhase("quiz");
}

function newExam() {
  generatedQuestions = null;
  userAnswers = {};
  quizMode = null;
  document.getElementById("mode-review").classList.remove("selected");
  document.getElementById("mode-practice").classList.remove("selected");
  document.getElementById("mode-exam").classList.remove("selected");
  document.getElementById("start-quiz-btn").disabled = true;
  showPhase("config");
}
