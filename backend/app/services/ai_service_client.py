from httpx import AsyncClient
from typing import Dict, Any 
from app.config import settings

class AIServiceClient:
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL.rstrip('/')

    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        async with AsyncClient() as client:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.split('/')[-1], f, 'application/octet-stream')}
                response = await client.post(
                    f"{self.base_url}/parse-resume",
                    files=files,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
