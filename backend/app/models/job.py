from sqlalchemy import Column, Integer, DateTime, String, JSON, Text
from sqlalchemy.sql import func

from .base import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(255), nullable = False, index = True)
    company = Column(String(255), nullable = True, index = True)
    location = Column(String(255), nullable = True)
    description = Column(Text, nullable = True)
    skills = Column(JSON, nullable = True)
    min_experience = Column(Integer, nullable = True)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at = Column(DateTime(timezone=True), onupdate = func.now())
    