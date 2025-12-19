from pathlib import Path
import uuid
from fastapi import HTTPException
from app.config import settings

def secure_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"

def validate_extension(filename: str):
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_exts:
        raise HTTPException(status_code=400, detail=f"Only {settings.allowed_exts} allowed. Got {ext}")

def validate_size(file_obj, max_size: int):
    # file_obj is UploadFile — we can't get full size without reading.
    # We check during streaming write in storage code. This helper exists for clarity.
    if max_size and max_size <= 0:
        raise HTTPException(status_code=400, detail="Invalid max_size config.")
