const apiBase = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://localhost:8000"
  : window.location.origin.replace(/\/$/, "");

const form = document.getElementById('gen-form');
const statusEl = document.getElementById('status');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  statusEl.textContent = "Generating…";
  const btn = form.querySelector('button');
  btn.disabled = true;

  const text = document.getElementById('text').value.trim();
  const guidance = document.getElementById('guidance').value.trim();
  const provider = document.getElementById('provider').value;
  const api_key = document.getElementById('api_key').value.trim();
  const template = document.getElementById('template').files[0];

  const fd = new FormData();
  fd.append('text', text);
  fd.append('guidance', guidance);
  fd.append('provider', provider);
  fd.append('api_key', api_key);
  fd.append('template', template);

  try {
    const res = await fetch(apiBase + '/api/generate', {
      method: 'POST',
      body: fd,
    });
    if (!res.ok) {
      const detail = await res.json().catch(()=>({detail: res.statusText}));
      throw new Error(detail.detail || JSON.stringify(detail));
    }
    const blob = await res.blob();
    const disposition = res.headers.get('Content-Disposition') || 'attachment; filename=generated.pptx';
    const match = /filename=([^;]+)/i.exec(disposition);
    const filename = match ? match[1] : 'generated.pptx';

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename.replace(/"/g, '');
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    statusEl.textContent = "Done — downloaded: " + filename;
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Error: " + err.message;
  } finally {
    btn.disabled = false;
  }
});