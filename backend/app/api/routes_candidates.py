from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.candidate import CandidateRead, BatchUploadResponse
from app.services.batch_service import save_batch_file
from app.worker.arq_worker import WorkerSettings
from app.services.candidate_service import  get_candidate, delete_candidate, delete_all_candidates
from uuid import uuid4
import json
import zipfile
from typing import List
import os
from arq import create_pool
from arq.connections import ArqRedis



router = APIRouter(prefix="/candidates", tags=["candidates"])

# @router.post("/", response_model=CandidateRead)
# async def create_candidate_endpoint(db: AsyncSession = Depends(get_db), resume: UploadFile = File(...)):
#     candidate = await create_candidate(db, resume=resume)
#     return candidate
arq_pool: ArqRedis = None

@router.on_event("startup")
async def startup():
    global arq_pool
    arq_pool = await create_pool(WorkerSettings.redis_settings)

@router.on_event("shutdown")
async def shutdown():
    if arq_pool:
       await arq_pool.close()



@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate_endpoint(candidate_id: int, db: AsyncSession = Depends(get_db)):
    candidate = await get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


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


@router.post("/batch", response_model=BatchUploadResponse)
async def upload_resume_batch(zip_file: UploadFile = File(...)):
    if not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip file is allowed")

    # Save the uploaded zip file
    zip_path = await save_batch_file(zip_file)
    extract_dir = os.path.dirname(zip_path)

    job_ids = []
    files_to_process = []

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        for root, _, files in os.walk(extract_dir):
            if '__MACOSX' in root:
                continue
            for fn in files:
                if fn.startswith('.') or fn.startswith('._'):
                    continue
                if fn.lower().endswith((".pdf", ".docx")):
                    file_path = os.path.join(root, fn)
                    files_to_process.append((file_path, fn))

        for file_path, original_filename in files_to_process:
            job = await arq_pool.enqueue_job("process_resume", file_path, original_filename)
            job_ids.append(job.job_id)

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    return BatchUploadResponse(
        total_files=len(job_ids),
        processed=0,
        failed=[],
        message="Batch processing started",
        job_ids=job_ids
    )

@router.post("/batch/status", response_model=BatchUploadResponse)
async def get_batch_status_endpoint(job_ids: List[str] = Body(..., embed=True)):
    processed = 0
    failed = []

    for job_id in job_ids:
        job = await arq_pool.job_result(job_id)
        if not job:
            continue
        if job.success:
            processed += 1
        else:
            result = await job.result()
            failed.append(result.get("filename", "unknown"))

    return BatchUploadResponse(
        total_files=len(job_ids),
        processed=processed,
        failed=failed,
        message="Status check complete",
        job_ids=job_ids
    )


# @router.get("/batch/{batch_id}", response_model=BatchUploadResponse)
# async def get_batch_status_endpoint(batch_id: str):
#     info = get_task_status(batch_id)

#     if info["status"] == "SUCCESS":
#         result = info["result"] or {}
#         total = result.get("processed", 0) + len(result.get("failed", []))

#         return BatchUploadResponse(
#             total_files=total,
#             processed=result.get("processed", 0),
#             failed=result.get("failed", []),
#             message="Processing complete",
#             batch_id=batch_id
#         )
#     elif info["status"] in ("PENDING", "STARTED", "RETRY"):
#         return BatchUploadResponse(
#             total_files=0,
#             processed=0,
#             failed=[],
#             message=f"Status: {info['status']}",
#             batch_id=batch_id
#         )
#     else:
#         return BatchUploadResponse(
#             total_files=0,
#             processed=0,
#             failed=[],
#             message=f"Status: {info['status']} - {info.get('result', 'Unknown error')}",
#             batch_id=batch_id
#         )
