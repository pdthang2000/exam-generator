function updateChatState() {
  if (!selectedDocId) {
    chatDocHint.textContent = "Select a document on the left to start chatting";
    chatInput.disabled = true;
    chatInput.placeholder = "Select a document first...";
    sendBtn.disabled = true;
  } else {
    const doc = allDocs.find(d => d.id === selectedDocId);
    chatDocHint.textContent = "Chatting with: " + (doc ? doc.filename : "");
    chatInput.disabled = false;
    chatInput.placeholder = "Ask a question about your document...";
    sendBtn.disabled = !chatInput.value.trim() || sending;
  }
}

function showChatLoading() {
  chatMessages.innerHTML =
    '<div class="chat-loading">' +
      '<div class="chat-loading-spinner"></div>' +
      '<span>Loading conversation...</span>' +
    '</div>';
}

async function loadChatHistory(docId) {
  try {
    const res = await fetch("/api/chat/history/" + docId);
    if (selectedDocId !== docId) return;
    const history = await res.json();
    chatMessages.innerHTML = "";
    if (history.length === 0) {
      chatMessages.innerHTML = '<div class="chat-empty">No conversation yet. Ask a question to get started.</div>';
    } else {
      for (const msg of history) {
        appendMsg(msg.role, msg.content);
      }
    }
  } catch (err) {
    if (selectedDocId !== docId) return;
    chatMessages.innerHTML = '<div class="chat-empty">Failed to load history.</div>';
  }
}

chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  sendBtn.disabled = !selectedDocId || !chatInput.value.trim() || sending;
});

chatInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) sendMessage();
  }
});

sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message || sending || !selectedDocId) return;

  sending = true;
  sendBtn.disabled = true;
  chatInput.value = "";
  chatInput.style.height = "auto";

  const emptyEl = chatMessages.querySelector(".chat-empty");
  if (emptyEl) emptyEl.remove();

  appendMsg("user", message);
  const thinkingEl = appendMsg("thinking", "Thinking...");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        document_id: selectedDocId || null,
      }),
    });

    const data = await res.json();
    thinkingEl.remove();

    if (!res.ok) throw new Error(data.error || "Chat failed");
    appendMsg("assistant", data.answer);
  } catch (err) {
    thinkingEl.remove();
    appendMsg("assistant", "Error: " + err.message);
  }

  sending = false;
  sendBtn.disabled = !selectedDocId || !chatInput.value.trim();
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendMsg(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

document.getElementById("clear-chat-btn").addEventListener("click", async () => {
  if (!selectedDocId) return;
  await fetch("/api/chat/" + selectedDocId, { method: "DELETE" });
  chatMessages.innerHTML = '<div class="chat-empty">No conversation yet. Ask a question to get started.</div>';
});

// --- Init ---
loadDocuments();
updateChatState();
