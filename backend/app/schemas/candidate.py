from pydantic import BaseModel, EmailStr
from typing import Optional, List


class CandidateBase(BaseModel):
    pass

class CandidateCreate(CandidateBase):
    pass

class CandidateRead(CandidateBase):
    id: int
    parsed: bool
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    experience_years: Optional[int] = None
    skills: List[str] = []
    raw_text: Optional[str] = None
    experiences: List[dict] = []
    education_details: List[dict] = []

    class Config:
        orm_mode = True

