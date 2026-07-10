dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => handleFile(fileInput.files[0]));
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  handleFile(e.dataTransfer.files[0]);
});

function handleFile(f) {
  if (!f) return;
  const ext = f.name.split(".").pop().toLowerCase();
  if (!ALLOWED.includes(ext)) {
    statusEl.innerHTML = '<div class="status error">Unsupported file type. Allowed: PDF, PPTX, TXT</div>';
    return;
  }
  selectedFile = f;
  fileNameEl.textContent = f.name;
  uploadBtn.disabled = false;
  statusEl.innerHTML = "";
}

uploadBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  uploadBtn.disabled = true;
  statusEl.innerHTML = '<div class="status loading"><span class="spinner"></span>Uploading & indexing...</div>';

  const form = new FormData();
  form.append("file", selectedFile);

  try {
    const res = await fetch("/api/documents", { method: "POST", body: form });
    const raw = await res.text();
    let data;
    try { data = JSON.parse(raw); } catch { throw new Error("Server error"); }
    if (!res.ok) throw new Error(data.error || "Upload failed");
    statusEl.innerHTML = '<div class="status success">Indexed (' + data.chunk_count + ' chunks)</div>';
    selectedFile = null;
    fileNameEl.textContent = "";
    fileInput.value = "";
    loadDocuments();
  } catch (err) {
    statusEl.innerHTML = '<div class="status error">' + err.message + '</div>';
    uploadBtn.disabled = false;
  }
});
