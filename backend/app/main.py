from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pdfminer.high_level import extract_text
from io import BytesIO

app = FastAPI(title="SkillMatch AI - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        return extract_text(BytesIO(pdf_bytes)) or ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {e}")

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(status_code=415, detail="Only PDF files are supported for now.")
    pdf_data = await file.read()
    if not pdf_data:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    text = extract_text_from_pdf(pdf_data)
    return {
        "filename": file.filename,
        "num_chars": len(text),
        "preview": text[:500],
        "full_text": text,
    }