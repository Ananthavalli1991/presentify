"""
Presentify Backend (FastAPI)
- POST /api/generate : accepts text, guidance, provider, api_key, template(.pptx/.potx)
Returns generated .pptx as attachment
Security: API keys are used only in-memory and never logged or persisted.
"""
import io, logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .utils import safe_filename, chunk_text_to_sections, extract_title_and_bullets
from .slide_maker import build_presentation
from .llm_router import build_outline
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("presentify-backend")

app = FastAPI(title="Presentify Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Root route → serve index.html
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h3>Presentify backend is running. POST /api/generate to create a deck.</h3>"

@app.post("/api/generate")
async def generate(
    text: str = Form(...),
    provider: str = Form(..., description="openai|anthropic|gemini"),
    api_key: str = Form(...),
    guidance: Optional[str] = Form(None),
    template: UploadFile = File(..., description=".pptx or .potx"),
):
    # Validate template
    fn = template.filename or "template.pptx"
    if not fn.lower().endswith((".pptx", ".potx")):
        raise HTTPException(status_code=400, detail="Template must be a .pptx or .potx file")

    tbytes = await template.read()
    max_size = 30 * 1024 * 1024  # 30 MB
    if len(tbytes) > max_size:
        raise HTTPException(status_code=413, detail=f"Template file too large (max {max_size//(1024*1024)}MB).")

    # Build outline via LLM (do NOT log api_key)
    slides = None
    try:
        slides = build_outline(text, guidance or "", provider, api_key)
    except Exception as e:
        logger.warning("LLM outline generation failed, falling back to deterministic parser. (%s)", str(e)[:200])
        sections = chunk_text_to_sections(text)
        slides = []
        for sec in sections[:20]:
            title, bullets = extract_title_and_bullets(sec)
            slides.append({"title": title or "Slide", "bullets": bullets})
        if not slides:
            raise HTTPException(status_code=500, detail="Failed to build outline and fallback produced no slides.")

    # Build the presentation using template
    try:
        out_bytes = build_presentation(tbytes, slides, title_fallback="Generated Deck")
    except Exception as e:
        logger.exception("Failed to build presentation: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to build presentation from template.")

    out_name = safe_filename(fn.rsplit(".",1)[0] + "_generated", ".pptx")
    return StreamingResponse(io.BytesIO(out_bytes),
                             media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                             headers={"Content-Disposition": f"attachment; filename={out_name}"})
