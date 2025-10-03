import re
from typing import List, Dict

def extract_experience(text: str) -> List[Dict]:
    pattern = r"(\d+)\s+(?:years|yrs)\s+(?:of)?\s+experience\s+(?:at|with)?\s+([A-Za-z &]+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [{"years": int(m[0]), "company": m[1]} for m in matches]