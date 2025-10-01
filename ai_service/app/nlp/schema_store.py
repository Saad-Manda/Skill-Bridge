from app.schemas.resume import ResumeSchema
import json

def create_resume_schema(name: str, text: str, skills, education, experience):
    return ResumeSchema(
        name=name,
        raw_text=text,
        skills=skills,
        education=education,
        experience=experience
    )

def save_resume_json(resume, out_path: str):
    with open(out_path, "w") as f:
        f.write(resume.json(indent=2))