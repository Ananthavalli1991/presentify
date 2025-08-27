# Presentify — Submission-ready

This repository contains a submission-ready Presentify project that converts bulk text/markdown into a PowerPoint using a user-supplied template and LLM provider key.

## Contents
- `backend/` — FastAPI service exposing `/api/generate`
- `frontend/` — Static frontend (HTML/CSS/JS) for simple demos
- `demo/` — Streamlit demo app (viewer + optional quick generation demo)
- `requirements.txt`, `README.md`, `LICENSE`

## Quickstart (Local)

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Start backend:
```
uvicorn backend.app:app --reload --port 8000
```

3. Serve frontend (optional):
```
python -m http.server --directory frontend 8080
# open http://localhost:8080
```

4. Try Streamlit demo (optional viewer + generation UI):
```
streamlit run demo/streamlit_app.py
```

## Notes for evaluation checklist
- Output Functionality: Backend `POST /api/generate` accepts text, guidance, provider, api_key, and template; returns `.pptx` attachment.
- Code Quality: Files under `backend/` are modular and documented; no API keys are logged or stored.
- UI/UX: frontend demo includes status messages; Streamlit demo provides slide preview, progress, and download button.

## Security & Privacy
- API keys are used only in-memory to make provider calls. The app **does not** persist or log keys.
- The backend enforces a 30MB template upload limit.

## Deployment suggestions
- Deploy backend to Render or Fly as a container (uvicorn).
- Serve frontend via GitHub Pages pointing to the backend origin, or mount static files in FastAPI for single-origin hosting.

---
