import os
import json
from .base_parser import ResumeParser

def parse_resume(resume_path: str) -> dict:
    if not resume_path or not os.path.exists(resume_path):
        raise FileNotFoundError(f"File not found: {resume_path}")

    # Initialize parser
    parser = ResumeParser(resume_path=resume_path)

    # Extract parsed details
    parsed_data = parser.get_extracted_data()

    # Optionally sanitize non-serializable types (e.g., sets, numpy, etc.)
    def sanitize(obj):
        if isinstance(obj, (set, tuple)):
            return list(obj)
        return obj

    cleaned_data = {k: sanitize(v) for k, v in parsed_data.items()}

    return cleaned_data


if __name__ == "__main__":
    test_resume = "MdMinhajUddinResume.pdf"
    result = parse_resume(test_resume)
    print(json.dumps(result, indent=4))