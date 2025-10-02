import spacy
import re
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = ["Python", "Java", "SQL", "Machine Learning"]  # extend later

def extract_skills(text: str) -> List[str]:
    doc = nlp(text)
    skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    for kw in SKILL_KEYWORDS:
        if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
            skills.append(kw)
    return list(set(skills))

def extract_education(text: str) -> List[str]:
    patterns = [
        r"(Bachelor|Master|B\.Sc|M\.Sc|Ph\.D|MBA|B\.A|M\.A)\s?in\s?\w+",
        r"(High School|Secondary School)"
    ]
    edu = []
    for p in patterns:
        edu.extend(re.findall(p, text, re.IGNORECASE))
    return edu

def extract_experience(text: str) -> List[Dict]:
    pattern = r"(\d+)\s+(?:years|yrs)\s+(?:of)?\s+experience\s+(?:at|with)?\s+([A-Za-z &]+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [{"years": int(m[0]), "company": m[1]} for m in matches]    