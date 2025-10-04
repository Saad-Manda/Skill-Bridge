from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from app.services.ai_service_client import AIServiceClient
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


async def create_candidate(db: AsyncSession, can_in: CandidateCreate) -> Candidate:
    candidate = Candidate(resume_file_url=can_in.resume_file_url)
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