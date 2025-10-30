from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.utils.files import secure_filename, validate_extension

CHUNK_SIZE = 1024 * 1024

def ensure_upload_dir():
    p = Path(settings.upload_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p

async def save_upload_to_disk(upload_file: UploadFile) -> str:
    validate_extension(upload_file.filename)
    upload_dir = ensure_upload_dir()
    filename = secure_filename(upload_file.filename)
    dest = upload_dir / filename

    written = 0
    try:
        with dest.open("wb") as f:
            while True:
                chunk = await upload_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                written += len(chunk)
                if written > settings.max_file_size:
                    # cleanup file and raise
                    f.close()
                    dest.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File too large")
                f.write(chunk)
    finally:
        await upload_file.close()

    return str(dest)