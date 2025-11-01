from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.candidate import CandidateRead, BatchUploadResponse
from app.services.batch_service import save_batch_file, get_task_status
from app.worker.batch_processor import process_resume_batch  
from app.services.candidate_service import create_candidate, get_candidate, delete_candidate, delete_all_candidates



router = APIRouter(prefix="/candidates", tags=["candidates"])

# @router.post("/", response_model=CandidateRead)
# async def create_candidate_endpoint(db: AsyncSession = Depends(get_db), resume: UploadFile = File(...)):
#     candidate = await create_candidate(db, resume=resume)
#     return candidate

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
    
    # Start Celery task
    task = process_resume_batch.delay(zip_path)
    
    return BatchUploadResponse(
        total_files=0,
        processed=0,
        failed=[],
        message="Batch processing started",
        batch_id=task.id
    )
    
    
@router.get("/batch/{batch_id}", response_model=BatchUploadResponse)
async def get_batch_status_endpoint(batch_id: str):
    info = get_task_status(batch_id)
    
    if info["status"] == "SUCCESS":
        result = info["result"] or {}
        total = result.get("processed", 0) + len(result.get("failed", []))
        
        return BatchUploadResponse(
            total_files=total,
            processed=result.get("processed", 0), 
            failed=result.get("failed", []),
            message="Processing complete",
            batch_id=batch_id
        )
    elif info["status"] in ("PENDING", "STARTED", "RETRY"):
        return BatchUploadResponse(
            total_files=0,
            processed=0,
            failed=[],
            message=f"Status: {info['status']}",
            batch_id=batch_id
        )  
    else:
        return BatchUploadResponse(
            total_files=0,
            processed=0,
            failed=[],
            message=f"Status: {info['status']} - {info.get('result', 'Unknown error')}",
            batch_id=batch_id
        )