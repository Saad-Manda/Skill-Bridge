from app.config import settings
from .batch_processor import process_resume

async def startup(ctx):
    pass
    
async def shutdown(ctx):
    pass
    
    
class WorkerSettings:
    redis_settings = {
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT
    }
    on_startup = startup
    on_shutdown = shutdown
    
    functions = [process_resume]
