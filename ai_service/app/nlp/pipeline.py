import json
from pathlib import Path
from app.nlp.file_parser import parse_file
from app.nlp.preprocess import clean_text
from app.nlp.skill_extraction import extract_skills, extract_education, extract_experience
from app.nlp.schema_store import create_resume_schema, save_resume_json

DATA_DIR = Path("data/resumes/PDFs/")
OUT_DIR = Path("data/resumes/json_parsed/")
OUT_DIR.mkdir(exist_ok=True, parents=True)

all_resumes = []

for category_dir in DATA_DIR.iterdir():
    if category_dir.is_dir():
        for file in category_dir.glob("*.*"):
            raw_text = clean_text(parse_file(str(file)))
            skills = extract_skills(raw_text)
            education = extract_education(raw_text)
            experience = extract_experience(raw_text)
            
            resume = create_resume_schema(file.stem, raw_text, skills, education, experience)
            save_resume_json(resume, str(OUT_DIR / f"{file.stem}.json"))
            all_resumes.append(resume)

# Optionally, merge all parsed resumes into one big JSON
with open(OUT_DIR / "all_resumes.json", "w") as f:
    json.dump([r.dict() for r in all_resumes], f, indent=2)