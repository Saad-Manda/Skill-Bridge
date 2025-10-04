import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import asyncio
from app.nlp.pipeline import parse_dir


app = FastAPI(title="AI Service")


def parse_uploaded_file(file_bytes, filename):
    """
    Workaround to use parse_dir on a single uploaded file.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        safe_name = Path(filename).name
        tmp_path = Path(tmpdirname) / safe_name
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)

        resumes = parse_dir(Path(tmpdirname))
        return resumes[0] if resumes else None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    file_bytes = await file.read()
    try:
        parsed_resume = await asyncio.to_thread(
            parse_uploaded_file, file_bytes, file.filename
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal parsing error")

    if not parsed_resume:
        raise HTTPException(status_code=400, detail="Could not parse uploaded file")

    return parsed_resume
