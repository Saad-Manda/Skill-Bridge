from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    min_experience: Optional[int] = None
    skills: Optional[List[str]] = []


class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    min_experience: Optional[int]
    skills: Optional[List[str]]
    
class JobRead(JobBase):
    id: int
    created_at: Optional[datetime]
    

class Config:
    orm_mode = True