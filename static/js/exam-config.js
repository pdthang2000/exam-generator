async function loadDocuments() {
  const res = await fetch("/api/documents");
  allDocs = await res.json();
  if (allDocs.length === 0) {
    docSelect.innerHTML = '<option value="">No documents — upload one first</option>';
  } else {
    docSelect.innerHTML = '<option value="">Select a document...</option>' +
      allDocs.map(d => '<option value="' + d.id + '">' + d.filename + ' (' + d.file_type.toUpperCase() + ', ' + (d.chunk_count || 0) + ' chunks)</option>').join("");
  }
  validate();
}

function updateTypeHint() {
  const total = parseInt(numQuestions.value) || 0;
  const tf = parseInt(tfCount.value) || 0;
  const mcq = parseInt(mcqCount.value) || 0;
  const sum = tf + mcq;
  typeHint.textContent = "Must sum to " + total + (sum !== total ? " (currently " + sum + ")" : "");
  typeHint.classList.toggle("invalid", sum !== total);
}

numQuestions.addEventListener("input", () => { updateTypeHint(); validate(); });
tfCount.addEventListener("input", () => { updateTypeHint(); validate(); });
mcqCount.addEventListener("input", () => { updateTypeHint(); validate(); });

function setActivePreset(name) {
  document.querySelectorAll(".preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.preset === name);
  });
}

function matchPreset() {
  const e = parseInt(easySlider.value), m = parseInt(mediumSlider.value), h = parseInt(hardSlider.value);
  for (const [name, vals] of Object.entries(PRESETS)) {
    if (e === vals[0] && m === vals[1] && h === vals[2]) { setActivePreset(name); return; }
  }
  setActivePreset("custom");
}

function updateDifficultyDisplay() {
  const e = parseInt(easySlider.value), m = parseInt(mediumSlider.value), h = parseInt(hardSlider.value);
  easyValue.textContent = e + "%";
  mediumValue.textContent = m + "%";
  hardValue.textContent = h + "%";
  const total = e + m + h;
  diffTotal.textContent = "Total: " + total + "%";
  diffTotal.classList.toggle("valid", total === 100);
  diffTotal.classList.toggle("invalid", total !== 100);
  matchPreset();
}

easySlider.addEventListener("input", () => { updateDifficultyDisplay(); validate(); });
mediumSlider.addEventListener("input", () => { updateDifficultyDisplay(); validate(); });
hardSlider.addEventListener("input", () => { updateDifficultyDisplay(); validate(); });

document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const preset = btn.dataset.preset;
    if (preset === "custom") { setActivePreset("custom"); return; }
    const vals = PRESETS[preset];
    easySlider.value = vals[0]; mediumSlider.value = vals[1]; hardSlider.value = vals[2];
    updateDifficultyDisplay(); validate();
  });
});

function validate() {
  const docOk = !!docSelect.value;
  const total = parseInt(numQuestions.value) || 0;
  const totalOk = total >= 1 && total <= 20;
  const tf = parseInt(tfCount.value) || 0;
  const mcq = parseInt(mcqCount.value) || 0;
  const typeOk = tf + mcq === total && tf >= 0 && mcq >= 0;
  const e = parseInt(easySlider.value), m = parseInt(mediumSlider.value), h = parseInt(hardSlider.value);
  const diffOk = e + m + h === 100;
  generateBtn.disabled = !docOk || !totalOk || !typeOk || !diffOk || generating;
}

docSelect.addEventListener("change", validate);

generateBtn.addEventListener("click", async () => {
  if (generating) return;
  generating = true;
  generateBtn.disabled = true;
  generateBtn.innerHTML = '<span class="spinner"></span>Generating...';
  genStatus.innerHTML = "";

  const body = {
    document_id: parseInt(docSelect.value),
    num_questions: parseInt(numQuestions.value),
    types: { true_false: parseInt(tfCount.value) || 0, mcq: parseInt(mcqCount.value) || 0 },
    difficulty: { easy: parseInt(easySlider.value), medium: parseInt(mediumSlider.value), hard: parseInt(hardSlider.value) },
  };

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Generation failed");
    generatedQuestions = data.questions;
    userAnswers = {};
    showPhase("mode");
  } catch (err) {
    genStatus.innerHTML = '<div class="status error">' + err.message + '</div>';
  }

  generating = false;
  generateBtn.innerHTML = "Generate Exam";
  validate();
});
