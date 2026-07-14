"""
FastAPI backend for ResumeMatch AI with verbose logging.
Run with: uvicorn api:app --reload --port 8000
"""

import io
import os
import sys

# Prevent torch threading issues on CPU
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="ResumeMatch AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class _FakeFile(io.BytesIO):
    """Wraps bytes and inherits from BytesIO so it is a fully compatible file-like object with a name attribute."""
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    jd_text: str = Form(...),
    resume_text: str = Form(""),
    resume_file: UploadFile = File(None),
):
    print(">>> RECEIVED ANALYZE REQUEST", flush=True)
    
    # Resolve file name
    filename = resume_file.filename if resume_file else "resume.txt"
    print(f">>> Filename: {filename}", flush=True)
    print(f">>> JD length: {len(jd_text)} chars", flush=True)

    if resume_file:
        print(">>> Reading uploaded file bytes...", flush=True)
        raw = await resume_file.read()
        fake = _FakeFile(raw, filename)
        print(f">>> Read {len(raw)} bytes", flush=True)
    elif resume_text.strip():
        print(">>> Using pasted text...", flush=True)
        raw = resume_text.encode("utf-8")
        fake = _FakeFile(raw, "resume.txt")
    else:
        print(">>> ERROR: No resume provided", flush=True)
        return JSONResponse(
            {"error": "Please provide a resume — either paste text or upload a file."},
            status_code=400,
        )

    # Import pipeline here to trace execution
    print(">>> Importing analyzer pipeline...", flush=True)
    try:
        from matcher import analyze_resume_and_jd
    except Exception as e:
        print(f">>> ERROR importing matcher: {e}", flush=True)
        return JSONResponse({"error": f"Import error: {e}"}, status_code=500)

    print(">>> Running analyzer pipeline...", flush=True)
    try:
        result = analyze_resume_and_jd(
            resume_file=fake,
            filename=filename,
            jd_text=jd_text,
        )
        print(">>> PIPELINE ANALYSIS COMPLETE", flush=True)
        return result
    except Exception as exc:
        print(f">>> PIPELINE ERROR: {exc}", flush=True)
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(exc)}, status_code=500)

# Serve React static files if built (for Docker/HF Spaces production deployment)
if os.path.exists("static"):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
    
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return FileResponse("static/index.html")
