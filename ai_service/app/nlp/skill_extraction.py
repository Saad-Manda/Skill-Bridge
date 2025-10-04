import spacy
import re
from typing import List
from spacy.matcher import PhraseMatcher


# lazy-load spaCy and a PhraseMatcher to avoid import-time failure
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
        _matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        PHRASES = [
            "telemetry",
            "iv",
            "wound care",
            "wound vac",
            "bedside report",
            "hourly rounding",
            "patient experience",
            "management of aggressive behavior",
            "gpn",
            "rn",
            "charge nurse",
            "resident care manager",
        ]
        patterns = [nlp.make_doc(p) for p in PHRASES]
        _matcher.add("SKILL", patterns)
    return _matcher


SKILL_KEYWORDS = ["Python", "Java", "SQL", "Machine Learning"]  # extend later


def extract_skills(text: str) -> List[str]:
    nlp = get_nlp()
    matcher = get_matcher()
    doc = nlp(text)
    skills = set()
    for _, start, end in matcher(doc):
        skills.add(doc[start:end].text)
    # fallback keyword search
    for kw in SKILL_KEYWORDS:
        if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
            skills.add(kw)
    return list(skills)


def extract_education(text: str) -> List[str]:
    patterns = [
        r"(Bachelor|Master|B\.Sc|M\.Sc|Ph\.D|MBA|B\.A|M\.A)\s?in\s?\w+",
        r"(High School|Secondary School)",
    ]
    edu = []
    for p in patterns:
        edu.extend(re.findall(p, text, re.IGNORECASE))
    return edu
