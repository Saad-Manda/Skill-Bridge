from sqlalchemy import Column, Integer, DateTime, String, JSON, Text, Boolean
from sqlalchemy.sql import func

from .base import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    resume_file_url = Column(String, nullable=False)
    parsed = Column(Boolean, default=False)

    # After Parsing
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    skills = Column(JSON, default=list)
    
    # Extras for AI Client
    education_details = Column(JSON, nullable=True)  
    experiences = Column(JSON, nullable=True)  
    raw_text = Column(Text, nullable=True)
