import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
import os
from app.parser.resume_parser import parse_resume



app = FastAPI(title="AI Service")



@app.post("/parse-resume")
async def get_parsed_resume(file: UploadFile = File(...)):
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try :
        parsed = parse_resume(tmp_path)
        return {
        "name": parsed.get("name"),
        "email": parsed.get("email"),
        "phone": parsed.get("mobile_number"),
        "skills": parsed.get("skills", []),
        "experiences": parsed.get("experience", []),
        "education": parsed.get("education", []),
        "raw_text": parsed.get("raw_text", "")
        }
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)






@app.get("/health")
async def health():
    return {"status": "ok"}


