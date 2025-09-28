from pydantic import BaseModel
from typing import List

class Experience(BaseModel):
    title: str
    company: str
    years: float

class Education(BaseModel):
    degree: str
    field: str
    institution: str

class Resume(BaseModel):
    skills: List[str]
    experience: List[Experience]
    education: List[Education]