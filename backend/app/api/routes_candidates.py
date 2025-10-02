from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateRead
from app.services.candidate_service import create_candidate, get_candidate

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.post("/", response_model=CandidateRead)
async def create_candidate_endpoint(candidate: CandidateCreate, db: AsyncSession = Depends(get_db)):
    candidate = await create_candidate(db, candidate)
    return  candidate

@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate_endpoint(candidate_id: int, db: AsyncSession = Depends(get_db)):
    candidate = await get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return  candidate
