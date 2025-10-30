import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from fastapi import UploadFile

from app.storage.disk import save_upload_to_disk
from app.services.ai_service_client import AIServiceClient
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate
from app.config import settings

async def create_candidate(db: AsyncSession, resume: UploadFile) -> Candidate:
    resume_path = await save_upload_to_disk(resume)
    candidate = Candidate(
        resume_file_path=resume_path,
        parsed=False,
        skills=[],
        experiences=[],
        education_details=[]
        )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate





async def get_candidate(db: AsyncSession, can_id: int) -> Optional[Candidate]:
    result = await db.execute(select(Candidate).where(Candidate.id == can_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
       return None
    return candidate



async def parse_candidate_resume(db: AsyncSession, can_id: int):
    ai_client = AIServiceClient()
    candidate = await get_candidate(db, can_id)
    
    parsed_data = await ai_client.parse_resume(candidate.resume_file_url)
    
    candidate.name = parsed_data.name
    candidate.skills = parsed_data.skills
    candidate.experiences = parsed_data.experiences
    candidate.education_details = parsed_data.education
    candidate.parsed = True
    
    await db.commit()
    
    

async def delete_candidate(db: AsyncSession, can_id: int) -> bool:
    candidate = await get_candidate(db, can_id)
    if not candidate:
        return False
        
    # Delete file from uploads folder
    if candidate.resume_file_path and os.path.exists(candidate.resume_file_path):
        os.remove(candidate.resume_file_path)
    
    # Delete from database
    await db.delete(candidate)
    await db.commit()
    return True


async def delete_all_candidates(db: AsyncSession) -> int:
    # Get all candidates to delete their files
    result = await db.execute(select(Candidate))
    candidates = result.scalars().all()
    
    # Delete all resume files
    for candidate in candidates:
        if candidate.resume_file_path and os.path.exists(candidate.resume_file_path):
            os.remove(candidate.resume_file_path)
    
    # Delete all records from database
    query = delete(Candidate)
    result = await db.execute(query)
    await db.commit()
    
    return len(candidates)