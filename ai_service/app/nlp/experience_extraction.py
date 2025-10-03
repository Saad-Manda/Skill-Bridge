import re
from datetime import datetime
from typing import List, Dict, Optional
from app.schemas.resume import Experience

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def parse_date(date_str: str) -> Optional[datetime]:
    """Convert raw date string into datetime object (or None)."""
    if not date_str:
        return None
    date_str = date_str.strip().lower()
    if date_str == "present":
        return datetime.now()
    # Try Month YYYY
    for m in MONTHS:
        if date_str.startswith(m):
            year = int(re.findall(r"\d{4}", date_str)[0])
            return datetime(year, MONTHS[m], 1)
    # Try just YYYY
    match = re.match(r"(\d{4})", date_str)
    if match:
        return datetime(int(match.group(1)), 1, 1)
    return None


def parse_single_experience(block: str) -> Experience:
    """
    Parse a single block of text into an experience schema:
    {position, company, start, end, duration_months}
    """
    # Regex for date range
    range_pattern = r"((?:[A-Za-z]{3,9}\s+)?\d{4})\s*(?:–|-|to)\s*(Present|(?:[A-Za-z]{3,9}\s+)?\d{4})"
    match = re.search(range_pattern, block, flags=re.IGNORECASE)

    start_date, end_date = None, None
    start_str, end_str = None, None

    if match:
        start_str, end_str = match.groups()
        start_date, end_date = parse_date(start_str), parse_date(end_str)

    # Split lines to guess company & position
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    company, position = None, None

    for line in lines:
        if re.search(r"(inc|corp|ltd|llc|technologies|solutions|company|group)", line, re.I):
            company = line
        elif re.search(r"(engineer|developer|manager|analyst|consultant|lead|intern)", line, re.I):
            position = line

    duration = None
    if start_date and end_date:
        duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    return Experience(
        title=position,
        company=company,
        duration_months=duration
    )


def extract_experiences(text: str) -> List[Experience]:
    """
    Extract all experiences from resume text.
    """
    # Regex for all date ranges
    range_pattern = r"((?:[A-Za-z]{3,9}\s+)?\d{4})\s*(?:–|-|to)\s*(Present|(?:[A-Za-z]{3,9}\s+)?\d{4})"
    matches = list(re.finditer(range_pattern, text, flags=re.IGNORECASE))

    experiences = []
    for i, match in enumerate(matches):
        start_idx = match.start()
        # Take a chunk of text around the date range
        chunk_start = max(0, start_idx - 150)  # 150 chars before date
        chunk_end = min(len(text), match.end() + 100)  # 100 chars after date
        block = text[chunk_start:chunk_end]

        exp = parse_single_experience(block)
        if exp: 
            experiences.append(exp)

    return experiences