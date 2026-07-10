const docSelect = document.getElementById("doc-select");
const numQuestions = document.getElementById("num-questions");
const tfCount = document.getElementById("tf-count");
const mcqCount = document.getElementById("mcq-count");
const typeHint = document.getElementById("type-hint");
const easySlider = document.getElementById("easy-slider");
const mediumSlider = document.getElementById("medium-slider");
const hardSlider = document.getElementById("hard-slider");
const easyValue = document.getElementById("easy-value");
const mediumValue = document.getElementById("medium-value");
const hardValue = document.getElementById("hard-value");
const diffTotal = document.getElementById("diff-total");
const generateBtn = document.getElementById("generate-btn");
const genStatus = document.getElementById("gen-status");

let allDocs = [];
let generatedQuestions = null;
let generating = false;
let quizMode = null;
let userAnswers = {};
let practiceIndex = 0;
let practiceScore = 0;
let practiceAnswered = false;

const PRESETS = {
  easy: [70, 20, 10],
  balanced: [33, 34, 33],
  hard: [10, 20, 70],
};

function showPhase(name) {
  ["config", "mode", "quiz", "results"].forEach(p => {
    document.getElementById("phase-" + p).classList.toggle("hidden", p !== name);
  });
  window.scrollTo(0, 0);
}

function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function getDocInfo() {
  const doc = allDocs.find(d => d.id === parseInt(docSelect.value));
  return {
    id: parseInt(docSelect.value),
    filename: doc ? doc.filename : "Unknown",
  };
}

function getExamTitle() {
  const doc = getDocInfo();
  return doc.filename + " - " + new Date().toLocaleDateString();
}
