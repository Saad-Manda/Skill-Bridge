import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import asyncio
from app.nlp.pipeline import parse_dir



app = FastAPI(title="AI Service")





@app.get("/health")
async def health():
    return {"status": "ok"}


