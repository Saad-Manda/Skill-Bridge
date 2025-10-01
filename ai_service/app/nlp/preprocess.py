import re

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)  # normalize whitespace
    text = text.strip()
    return text