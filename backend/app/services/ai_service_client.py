from httpx import AsyncClient
from app.config import settings

class AIServiceClient:
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL
        self.client = AsyncClient()

    async def parse_resume(self, file_url: str):
        response = await self.client.post(
            f"{self.base_url}/parse",
            json={"file_url": file_url}
        )
        return response.json()