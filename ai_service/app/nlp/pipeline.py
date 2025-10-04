import json
from pathlib import Path
from app.nlp.file_parser import parse_file
from app.nlp.preprocess import clean_text
from app.nlp.skill_extraction import extract_skills
from app.nlp.education_extraction import extract_education
from app.nlp.experience_extraction import extract_experiences
from app.nlp.schema_store import create_resume_schema


def parse_dir(dir):
    all_resumes = []
    for file in dir.glob("*.*"):
        try:
            raw = parse_file(str(file))
        except ValueError:
            # unsupported file type; skip and continue
            continue
        raw_text = clean_text(raw)
        skills = extract_skills(raw_text)
        education = extract_education(raw_text)
        experience = extract_experiences(raw_text)

        resume = create_resume_schema(
            file.stem, raw_text, skills, education, experience
        )
        all_resumes.append(resume)

    return all_resumes
