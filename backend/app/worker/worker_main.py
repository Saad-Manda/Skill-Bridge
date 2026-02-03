import asyncio
import json
from app.worker.batch_processor import process_resume_batch

import redis.asyncio as redis

async def main():
    while True:
        _, raw = await redis.brpop("resume_batches")
        job = json.loads(raw)

        await process_resume_batch(
            batch_id=job["batch_id"],
            zip_path=job["zip_path"]
        )

if __name__ == "__main__":
    asyncio.run(main())