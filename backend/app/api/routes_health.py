from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db, test_connection

router = APIRouter()


@router.get("/health", tags=["health"])
async def health(db: AsyncSession = Depends(get_db)):
    try:

        ok = await test_connection()
        if not ok:
            raise RuntimeError("DB returned unexpected value")
        return {"status": "ok", "db": True}
    except Exception as exc:

        raise HTTPException(status_code=503, detail=f"DB healthcheck failed: {exc}")
