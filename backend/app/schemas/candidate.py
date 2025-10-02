from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class CandidateBase(BaseModel):
    resume_file_url: str

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

    class Config:
        orm_mode = True



    