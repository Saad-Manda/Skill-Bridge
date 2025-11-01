import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from fastapi import UploadFile, HTTPException

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
    
    # Check if candidate exists
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id {can_id} not found")
    
    # Check if resume file exists
    if not candidate.resume_file_path or not os.path.exists(candidate.resume_file_path):
        raise HTTPException(
            status_code=400, 
            detail="Resume file not found or path is invalid"
        )
    
    parsed_data = await ai_client.parse_resume(candidate.resume_file_path)
    
    candidate.name = parsed_data.get("name")
    candidate.skills = parsed_data.get("skills", [])
    candidate.experiences = parsed_data.get("experiences", [])
    candidate.education_details = parsed_data.get("education_details", [])
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


async def create_candidate_from_parsed(db: AsyncSession, resume_path: str, parsed: dict) -> Candidate:
    candidate = Candidate(
        resume_file_path=resume_path,
        parsed=True,
        name=parsed.get("name"),
        email=parsed.get("email"),
        phone=parsed.get("phone") or parsed.get("mobile_number"),
        experience_years=parsed.get("total_experience"),
        skills=parsed.get("skills") or [],
        education_details=parsed.get("education") or parsed.get("education_details") or [],
        experiences=parsed.get("experiences") or [],
        raw_text=parsed.get("raw_text") or parsed.get("text") or None
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate