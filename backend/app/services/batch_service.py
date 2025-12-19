import os
import aiofiles
from typing import Dict, Any
from app.config import settings
from app.core.celery_config import celery_app

async def save_batch_file(zip_file, task_name: str = "batch") -> str:
    """
    Saves incoming UploadFile to a temp zip path and returns the path.
    """
    os.makedirs(settings.UPLOAD_BATCH_DIR, exist_ok=True)
    tmp_name = f"{task_name}-{os.urandom(6).hex()}.zip"
    save_path = os.path.join(settings.UPLOAD_BATCH_DIR, tmp_name)
    async with aiofiles.open(save_path, "wb") as out:
        content = await zip_file.read()
        await out.write(content)
    return save_path

def get_task_status(task_id: str) -> Dict[str, Any]:
    res = celery_app.AsyncResult(task_id)
    return {
        "id": task_id,
        "status": res.status,
        "result": res.result if res.ready() else None,
        "failed": res.failed()
    }