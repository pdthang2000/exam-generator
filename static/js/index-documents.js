async function loadDocuments() {
  const res = await fetch("/api/documents");
  allDocs = await res.json();

  if (selectedDocId && !allDocs.some(d => d.id === selectedDocId)) {
    selectedDocId = null;
  }

  renderDocList();
  updateChatState();
}

function renderDocList() {
  if (allDocs.length === 0) {
    docListEl.innerHTML = '<div class="empty-state">No documents uploaded yet.</div>';
    return;
  }

  docListEl.innerHTML = allDocs.map(doc => {
    const sel = selectedDocId === doc.id ? "selected" : "";
    return '<div class="doc-item ' + sel + '" data-id="' + doc.id + '">' +
      '<div class="doc-info" onclick="toggleDoc(' + doc.id + ')">' +
        '<div class="doc-icon ' + doc.file_type + '">' + (ICONS[doc.file_type] || "\u{1F4C4}") + '</div>' +
        '<div class="doc-text">' +
          '<div class="doc-name">' + doc.filename + '</div>' +
          '<div class="doc-meta">' + doc.file_type.toUpperCase() + ' · ' + (doc.chunk_count || 0) + ' chunks</div>' +
        '</div>' +
      '</div>' +
      '<div class="doc-actions">' +
        '<button class="btn-preview" onclick="event.stopPropagation();previewDoc(' + doc.id + ',\'' + doc.filename.replace(/'/g, "\\'") + '\')">Preview</button>' +
        '<button class="btn-danger" onclick="event.stopPropagation();deleteDoc(' + doc.id + ')">Remove</button>' +
      '</div>' +
    '</div>';
  }).join("");
}

function toggleDoc(id) {
  selectedDocId = selectedDocId === id ? null : id;
  renderDocList();
  updateChatState();
  if (selectedDocId) {
    showChatLoading();
    loadChatHistory(selectedDocId);
  } else {
    chatMessages.innerHTML = '<div class="chat-empty">Select a document to start chatting.</div>';
  }
}

async function previewDoc(id, filename) {
  const overlay = document.getElementById("preview-overlay");
  document.getElementById("preview-title").textContent = filename;
  document.getElementById("preview-content").textContent = "Loading...";
  overlay.classList.add("open");

  try {
    const res = await fetch("/api/documents/" + id + "/preview");
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    document.getElementById("preview-content").textContent = data.text;
  } catch (err) {
    document.getElementById("preview-content").textContent = "Error: " + err.message;
  }
}

function closePreview() {
  document.getElementById("preview-overlay").classList.remove("open");
}

document.getElementById("preview-overlay").addEventListener("click", e => {
  if (e.target === e.currentTarget) closePreview();
});

async function deleteDoc(id) {
  if (!confirm("Are you sure you want to remove this document?")) return;
  await fetch("/api/documents/" + id, { method: "DELETE" });
  loadDocuments();
}
