# AI Service

This microservice exposes a small FastAPI app that can parse uploaded resume files.

Run locally:

1. Create a venv and install dependencies from `ai_service/requirements.txt`.

2. Start the service from the repo root:

```bash
python ai_service/run_server.py
```

The service listens on port 8001 by default. Use `HOST`, `PORT`, and `RELOAD` env vars to change behavior.
