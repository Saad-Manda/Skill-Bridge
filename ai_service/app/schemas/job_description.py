from pydantic import BaseModel
from typing import List, Optional

class JobDescription(BaseModel):
    title: str
    raw_text: str
    required_skills: List[str]
    min_experience_years: Optional[float]
    responsibilities: Optional[List[str]] = []
    education_requirements: Optional[List[str]] = []
    location: Optional[str] = None
    employment_type: Optional[str] = None    # Full-time, Part-time