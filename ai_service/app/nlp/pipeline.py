import json
from pathlib import Path
from app.nlp.file_parser import parse_file
from app.nlp.preprocess import clean_text
from app.nlp.skill_extraction import extract_skills
from app.nlp.education_extraction import extract_education
from app.nlp.experience_extraction import extract_experience
from app.nlp.schema_store import create_resume_schema


def parse_dir(dir):
    all_resumes = []
    for file in dir.glob("*.*"):
        raw_text = clean_text(parse_file(str(file)))
        skills = extract_skills(raw_text)
        education = extract_education(raw_text)
        experience = extract_experience(raw_text)

        resume = create_resume_schema(file.stem, raw_text, skills, education, experience)
        all_resumes.append(resume)
    
    return all_resumes