from pathlib import Path
import os
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
env_path = ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)


def main():
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "true").lower() in ("1", "true", "yes")


    from app.main import app  

    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
