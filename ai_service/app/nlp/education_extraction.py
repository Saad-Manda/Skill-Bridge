import re
import spacy
from typing import List
from spacy.matcher import Matcher
from app.schemas.resume import Education

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

degree_patterns = [
    [{"LOWER": {"IN": ["bachelor", "master", "phd", "mba", "associate", "doctorate"]}}],
    [{"TEXT": {"REGEX": r"(B\.Sc|M\.Sc|B\.Tech|M\.Tech|B\.Eng|LLB|LLM|MD|DO|DDS)"}}],
]

for pattern in degree_patterns:
    matcher.add("DEGREE", [pattern])

gpa_pattern = re.compile(r"(GPA|CGPA)\s*[:\-]?\s*([\d\.]+)\s*\/?\s*([\d\.]+)?", re.IGNORECASE)
perc_pattern = re.compile(r"(\d{2,3}\.?\d?)\s?%", re.IGNORECASE)
year_pattern = re.compile(r"(19|20)\d{2}")


def extract_education_section(text: str, window: int = 8) -> List[str]:
    """
    Find lines under 'Education' section or similar keywords.
    Returns a list of candidate lines.
    """
    edu_keywords = ["education", "academic", "qualification", "coursework", "studies"]
    lines = text.split("\n")
    edu_lines = []
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in edu_keywords):
            edu_lines.extend(lines[i:i+window])
    return edu_lines if edu_lines else lines  # fallback = whole resume


def parse_education_line(line: str) -> Education:
    doc = nlp(line)
    matches = matcher(doc)

    degree, field, institution, grade = None, None, None, None
    years = []

    # DEGREE detection
    for match_id, start, end in matches:
        span = doc[start:end]
        degree = span.text

    # FIELD (take last NOUN after degree)
    if degree:
        degree_end = line.lower().find(degree.lower()) + len(degree)
        remainder = line[degree_end:].strip()
        tokens = nlp(remainder)
        nouns = [t.text for t in tokens if t.pos_ in ["NOUN", "PROPN"]]
        if nouns:
            field = " ".join(nouns[:3])  # crude heuristic

    # INSTITUTION (look for org entities)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"]:
            institution = ent.text

    # GRADE
    gpa_match = gpa_pattern.search(line)
    if gpa_match:
        grade = gpa_match.group(0)
    else:
        perc_match = perc_pattern.search(line)
        if perc_match:
            grade = perc_match.group(0)

    # YEARS
    years = year_pattern.findall(line)
    years = [int("".join(y)) for y in years] if years else []

    return Education(
        degree=degree,
        field=field,
        institution=institution,
        start_year=min(years) if years else None,
        end_year=max(years) if years else None,
        grade=grade
    )


def extract_education(text: str) -> List[Education]:
    section = extract_education_section(text)
    results = []

    for line in section:
        entry = parse_education_line(line)
        if entry.degree or entry.institution:  
            results.append(entry)

    return results

if __name__ == "__main__":
    sample_text = """
    EDUCATION
    Bachelor of Technology in Computer Science, ABC University, GPA 8.5/10, 2016 - 2020
    Master of Science, Data Science, XYZ Institute, 2021
    High School, DEF Senior Secondary School, 85%, 2014
    """

    edu = extract_education(sample_text)
    for e in edu:
        print(e.json())