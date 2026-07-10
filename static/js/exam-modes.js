function selectMode(mode) {
  quizMode = mode;
  document.getElementById("mode-review").classList.toggle("selected", mode === "review");
  document.getElementById("mode-practice").classList.toggle("selected", mode === "practice");
  document.getElementById("mode-exam").classList.toggle("selected", mode === "exam");
  document.getElementById("start-quiz-btn").disabled = false;
}

function startQuiz() {
  if (!quizMode || !generatedQuestions) return;
  userAnswers = {};
  if (quizMode === "review") {
    renderReviewMode();
  } else if (quizMode === "practice") {
    practiceIndex = 0;
    practiceScore = 0;
    practiceAnswered = false;
    renderPracticeQuestion();
  } else {
    renderExamMode();
  }
  showPhase("quiz");
}

// --- Review Mode ---

function renderReviewMode() {
  const questions = generatedQuestions;
  const area = document.getElementById("phase-quiz");

  let html = '<div class="card">';
  html += '<h2>Exam Review (' + questions.length + ' questions)</h2>';

  for (const q of questions) {
    const typeBadge = q.type === "true_false"
      ? '<span class="badge badge-tf">T/F</span>'
      : '<span class="badge badge-mcq">MCQ</span>';
    const diffBadge = '<span class="badge badge-' + q.difficulty + '">' + q.difficulty + '</span>';

    html += '<div class="q-card">';
    html += '<div class="q-header"><span class="q-num">Q' + q.id + '</span>' + typeBadge + diffBadge + '</div>';
    html += '<div class="q-text">' + escapeHtml(q.question) + '</div>';
    html += '<ul class="q-options">';
    for (const opt of q.options) {
      const cls = opt === q.correct_answer ? "correct-reveal disabled" : "disabled";
      html += '<li class="' + cls + '">' + escapeHtml(opt) + (opt === q.correct_answer ? ' &#10003;' : '') + '</li>';
    }
    html += '</ul>';
    if (q.explanation) {
      html += '<div class="q-explanation">' + escapeHtml(q.explanation) + '</div>';
    }
    html += '</div>';
  }

  html += '<div class="post-actions">';
  html += '<button class="btn-outline" onclick="saveExam()">Save Exam</button>';
  html += '<button class="btn-outline" onclick="newExam()">New Exam</button>';
  html += '<button class="btn-outline" onclick="backToModes()">Take Quiz</button>';
  html += '</div>';

  html += '<div class="post-actions" style="margin-top:8px">';
  html += '<div class="export-group"><label>Export:</label>';
  html += '<button class="btn-secondary" onclick="exportExam(\'json\')">JSON</button>';
  html += '<button class="btn-secondary" onclick="exportExam(\'markdown\')">MD</button>';
  html += '<button class="btn-secondary" onclick="exportExam(\'text\')">TXT</button>';
  html += '<button class="btn-secondary" onclick="exportExam(\'csv\')">CSV</button>';
  html += '</div>';
  html += '</div>';

  html += '</div>';
  area.innerHTML = html;
}

function backToModes() {
  quizMode = null;
  document.getElementById("mode-review").classList.remove("selected");
  document.getElementById("mode-practice").classList.remove("selected");
  document.getElementById("mode-exam").classList.remove("selected");
  document.getElementById("start-quiz-btn").disabled = true;
  showPhase("mode");
}

// --- Practice Mode ---

function renderPracticeQuestion() {
  const q = generatedQuestions[practiceIndex];
  const total = generatedQuestions.length;
  const area = document.getElementById("phase-quiz");

  const typeBadge = q.type === "true_false"
    ? '<span class="badge badge-tf">T/F</span>'
    : '<span class="badge badge-mcq">MCQ</span>';
  const diffBadge = '<span class="badge badge-' + q.difficulty + '">' + q.difficulty + '</span>';

  let html = '<div class="card">';
  html += '<div class="progress-bar">';
  html += '<span>Question ' + (practiceIndex + 1) + ' of ' + total + '</span>';
  html += '<span class="score-display">Score: ' + practiceScore + '/' + (practiceIndex) + '</span>';
  html += '</div>';

  html += '<div class="q-card">';
  html += '<div class="q-header"><span class="q-num">Q' + q.id + '</span>' + typeBadge + diffBadge + '</div>';
  html += '<div class="q-text">' + escapeHtml(q.question) + '</div>';
  html += '<ul class="q-options" id="practice-options">';
  for (let i = 0; i < q.options.length; i++) {
    html += '<li onclick="practiceSelect(this, ' + i + ')" data-idx="' + i + '">' + escapeHtml(q.options[i]) + '</li>';
  }
  html += '</ul>';
  html += '<div id="practice-feedback"></div>';
  html += '</div>';

  html += '<div class="quiz-nav">';
  html += '<button class="btn-outline" id="check-btn" disabled onclick="practiceCheck()">Check Answer</button>';
  html += '<button class="btn btn-primary" id="next-btn" style="width:auto;display:none" onclick="practiceNext()">' +
    (practiceIndex < total - 1 ? 'Next Question' : 'See Results') + '</button>';
  html += '</div>';
  html += '</div>';

  area.innerHTML = html;
  practiceAnswered = false;
}

function practiceSelect(el, idx) {
  if (practiceAnswered) return;
  document.querySelectorAll("#practice-options li").forEach(li => li.classList.remove("selected"));
  el.classList.add("selected");
  userAnswers[String(generatedQuestions[practiceIndex].id)] = generatedQuestions[practiceIndex].options[idx];
  document.getElementById("check-btn").disabled = false;
}

function practiceCheck() {
  if (practiceAnswered) return;
  practiceAnswered = true;

  const q = generatedQuestions[practiceIndex];
  const chosen = userAnswers[String(q.id)];
  const isCorrect = chosen === q.correct_answer;
  if (isCorrect) practiceScore++;

  document.querySelectorAll("#practice-options li").forEach(li => {
    li.classList.add("disabled");
    const optText = li.textContent;
    if (optText === q.correct_answer) {
      li.classList.add("correct-reveal");
    } else if (optText === chosen && !isCorrect) {
      li.classList.add("wrong-reveal");
    }
  });

  const fb = document.getElementById("practice-feedback");
  fb.innerHTML = '<div class="q-explanation">' +
    (isCorrect ? '<strong>Correct!</strong> ' : '<strong>Incorrect.</strong> The answer is: ' + escapeHtml(q.correct_answer) + '. ') +
    escapeHtml(q.explanation || '') + '</div>';

  document.getElementById("check-btn").style.display = "none";
  document.getElementById("next-btn").style.display = "";

  const scoreEl = document.querySelector(".score-display");
  if (scoreEl) scoreEl.textContent = "Score: " + practiceScore + "/" + (practiceIndex + 1);
}

function practiceNext() {
  practiceIndex++;
  if (practiceIndex < generatedQuestions.length) {
    renderPracticeQuestion();
  } else {
    showResults();
  }
}

// --- Exam Mode ---

function renderExamMode() {
  const questions = generatedQuestions;
  const area = document.getElementById("phase-quiz");

  let html = '<div class="card">';
  html += '<div class="progress-bar">';
  html += '<span>' + questions.length + ' questions</span>';
  html += '<span class="score-display" id="exam-answered">Answered: 0/' + questions.length + '</span>';
  html += '</div>';

  for (const q of questions) {
    const typeBadge = q.type === "true_false"
      ? '<span class="badge badge-tf">T/F</span>'
      : '<span class="badge badge-mcq">MCQ</span>';
    const diffBadge = '<span class="badge badge-' + q.difficulty + '">' + q.difficulty + '</span>';

    html += '<div class="q-card" id="exam-q-' + q.id + '">';
    html += '<div class="q-header"><span class="q-num">Q' + q.id + '</span>' + typeBadge + diffBadge + '</div>';
    html += '<div class="q-text">' + escapeHtml(q.question) + '</div>';
    html += '<ul class="q-options">';
    for (let i = 0; i < q.options.length; i++) {
      html += '<li onclick="examSelect(' + q.id + ', this, ' + i + ')" data-qid="' + q.id + '" data-idx="' + i + '">' + escapeHtml(q.options[i]) + '</li>';
    }
    html += '</ul>';
    html += '</div>';
  }

  html += '<button class="btn btn-primary" style="margin-top: 12px" onclick="submitExam()">Submit Exam</button>';
  html += '</div>';

  area.innerHTML = html;
}

function examSelect(qid, el, idx) {
  const q = generatedQuestions.find(q => q.id === qid);
  document.querySelectorAll('#exam-q-' + qid + ' .q-options li').forEach(li => li.classList.remove("selected"));
  el.classList.add("selected");
  userAnswers[String(qid)] = q.options[idx];

  const answered = Object.keys(userAnswers).length;
  const el2 = document.getElementById("exam-answered");
  if (el2) el2.textContent = "Answered: " + answered + "/" + generatedQuestions.length;
}

function submitExam() {
  const unanswered = generatedQuestions.filter(q => !userAnswers[String(q.id)]);
  if (unanswered.length > 0) {
    if (!confirm(unanswered.length + " question(s) unanswered. Submit anyway?")) return;
  }
  showResults();
}
