from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.candidate import CandidateRead
from app.services.candidate_service import create_candidate, get_candidate, delete_candidate, delete_all_candidates

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.post("/", response_model=CandidateRead)
async def create_candidate_endpoint(db: AsyncSession = Depends(get_db), resume: UploadFile = File(...)):
    candidate = await create_candidate(db, resume=resume)
    return candidate

@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate_endpoint(candidate_id: int, db: AsyncSession = Depends(get_db)):
    candidate = await get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return  candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate_endpoint(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await delete_candidate(db, candidate_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )
    return {"message": "Candidate deleted successfully"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_candidates_endpoint(
    db: AsyncSession = Depends(get_db)
):
    count = await delete_all_candidates(db)
    return {"message": f"Successfully deleted {count} candidates"}