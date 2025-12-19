import re
import spacy
from typing import List
from spacy.matcher import Matcher
from app.schemas.resume import Education


# lazy-load spaCy model and matcher to avoid import-time failure when model is missing
_nlp = None
_matcher = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def get_matcher():
    global _matcher
    if _matcher is None:
        nlp = get_nlp()
        _matcher = Matcher(nlp.vocab)
        degree_patterns = [
            [
                {
                    "LOWER": {
                        "IN": [
                            "bachelor",
                            "master",
                            "phd",
                            "mba",
                            "associate",
                            "doctorate",
                        ]
                    }
                }
            ],
            [
                {
                    "TEXT": {
                        "REGEX": r"(B\.Sc|M\.Sc|B\.Tech|M\.Tech|B\.Eng|LLB|LLM|MD|DO|DDS)"
                    }
                }
            ],
        ]
        for pattern in degree_patterns:
            _matcher.add("DEGREE", [pattern])
    return _matcher


gpa_pattern = re.compile(
    r"(GPA|CGPA)\s*[:\-]?\s*([\d\.]+)\s*\/?\s*([\d\.]+)?", re.IGNORECASE
)
perc_pattern = re.compile(r"(\d{2,3}\.?\d?)\s?%", re.IGNORECASE)
year_pattern = re.compile(r"(?:19|20)\d{2}")
date_range_re = re.compile(
    r"(?P<start>(?:[A-Za-z]{3,9}\s+)?(?:19|20)\d{2})\s*(?:\u2013|\u2014|-|to)\s*(?P<end>(?:[A-Za-z]{3,9}\s+)?(?:19|20)\d{2}|present)",
    re.IGNORECASE,
)


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
            edu_lines.extend(lines[i : i + window])
    return edu_lines if edu_lines else lines  # fallback = whole resume


def parse_education_line(line: str) -> Education:
    doc = get_nlp()(line)
    matches = get_matcher()(doc)

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
        tokens = get_nlp()(remainder)
        nouns = [t.text for t in tokens if t.pos_ in ["NOUN", "PROPN"]]
        if nouns:
            field = " ".join(nouns[:3])  # crude heuristic

    # INSTITUTION (look for org entities)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"]:
            institution = ent.text

    # YEARS / ranges
    start_year = None
    end_year = None

    # Prefer explicit date ranges like '2016 - 2020' or 'Jan 2017 – Present'
    dr = date_range_re.search(line)
    if dr:

        def _strip_year(s: str):
            m = year_pattern.search(s)
            return int(m.group(0)) if m else None

        start_year = _strip_year(dr.group("start"))
        end_raw = dr.group("end")
        if end_raw and end_raw.strip().lower() == "present":
            end_year = None
        else:
            end_year = _strip_year(end_raw)
    else:
        found = year_pattern.findall(line)
        years = [int(y) for y in found] if found else []
        if len(years) >= 2:
            start_year, end_year = min(years), max(years)
        elif len(years) == 1:
            # single year -> treat as completion/end year
            start_year, end_year = None, years[0]
        else:
            start_year, end_year = None, None

    return Education(
        degree=degree,
        field=field,
        institution=institution,
        start_year=start_year,
        end_year=end_year,
        grade=grade,
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
