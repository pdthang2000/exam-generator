const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const fileNameEl = document.getElementById("file-name");
const uploadBtn = document.getElementById("upload-btn");
const statusEl = document.getElementById("status");
const docListEl = document.getElementById("doc-list");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const chatDocHint = document.getElementById("chat-doc-hint");

let selectedFile = null;
let selectedDocId = null;
let allDocs = [];
let sending = false;

const ALLOWED = ["pdf", "pptx", "txt"];
const ICONS = { pdf: "\u{1F4D5}", pptx: "\u{1F4CA}", txt: "\u{1F4DD}" };
