import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
import os
from app.parser.resume_parser import parse_resume



app = FastAPI(title="AI Service")



@app.post("/parse_resume")
async def get_parsed_resume(resume: UploadFile = File(...)):
    contents = await resume.read()
    
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")
    

    suffix = os.path.splitext(resume.filename)[1] or ".pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = tmp.name
    
    try :
        tmp.write(contents)
        tmp.flush()
        tmp.close()
        
        parsed = parse_resume(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


    return {
    "name": parsed.get("name"),
    "email": parsed.get("email"),
    "phone": parsed.get("mobile_number"),
    "skills": parsed.get("skills", []),
    "experiences": parsed.get("experience", []),
    "education": parsed.get("education", []),
    "raw_text": parsed.get("raw_text", "")
}


@app.get("/health")
async def health():
    return {"status": "ok"}


