from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration_months: Optional[float] = None

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