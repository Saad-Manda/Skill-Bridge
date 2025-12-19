from celery import Celery
from app.config import settings


celery_app = Celery(
    "skillbridge_worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=['app.worker.batch_processor']

)

celery_app.conf.task_track_started = True
celery_app.conf.worker_prefetch_multiplier = 1


# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)