from fastapi import FastAPI
from .config import settings
from .api.routes_health import router as health_router

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

# include future routers under /api or top-level as you like
app.include_router(health_router, prefix="")

@app.get("/")
async def root():
    return {"project": settings.PROJECT_NAME}
