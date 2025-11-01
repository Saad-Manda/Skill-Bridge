from app.core.celery_config import celery_app
from .batch_processor import process_resume_batch

# This makes the task available to Celery
__all__ = ['celery_app', 'process_resume_batch']