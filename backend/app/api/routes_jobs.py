from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.services.job_service import create_job, get_job, list_jobs, update_job, delete_job


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobRead)
async def create_job_endpoint(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    job = await create_job(db, payload)
    return job
    
@router.get("/", response_model=List[JobRead])
async def list_jobs_endpoint(limit: int = Query(20, ge=1, le=200), offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await list_jobs(db, limit=limit, offset=offset)

@router.get("/{job_id}", response_model=JobRead)
async def get_job_endpoint(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobRead)
async def update_job_endpoint(job_id: int, payload: JobUpdate, db: AsyncSession = Depends(get_db)):
    job = await update_job(db, job_id, payload)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/{job_id}", status_code=204)
async def delete_job_endpoint(job_id: int, db: AsyncSession = Depends(get_db)):
    ok = await delete_job(db, job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return None