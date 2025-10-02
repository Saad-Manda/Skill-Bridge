from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


async def create_job(db: AsyncSession, job_in: JobCreate) -> Job:
    job = Job(**job_in.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def get_job(db: AsyncSession, job_id: int) -> Optional[Job]:
    return await db.get(Job, job_id)

async def list_jobs(db: AsyncSession, limit: 50, offset: 0) -> List[Job]:
    q = await db.execute(select(Job).limit(limit).offset(offset))
    return q.scalars().all()

async def update_job(db: AsyncSession, job_id: int, job_in: JobUpdate) -> Optional[Job]:
    job = await db.get(Job, job_id)
    
    if not job:
        return None
    for field, value in job_in.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def delete_job(db: AsyncSession, job_id: int) -> bool:
    job = await db.get(Job, job_id)
    
    if not job:
        return False
    await db.delete(job)
    await db.commit()
    return True

    
        