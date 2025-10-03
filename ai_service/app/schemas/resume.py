from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    title: str
    company: str
    duration_months: float

class Education(BaseModel):
    degree: Optional[str]
    field: Optional[str]
    institution: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    grade: Optional[str]

class Resume(BaseModel):
    name: str
    raw_text: str
    skills: List[str]
    experience: List[Experience]
    education: List[Education]