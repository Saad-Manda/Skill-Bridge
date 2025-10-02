from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

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
    