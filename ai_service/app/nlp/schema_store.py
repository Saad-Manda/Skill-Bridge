from app.schemas.resume import Resume

def create_resume_schema(name: str, text: str, skills, education, experience):
    return Resume(
        name=name,
        raw_text=text,
        skills=skills,
        education=education,
        experience=experience
    )