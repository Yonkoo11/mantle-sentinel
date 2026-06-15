# Sentinel audit API — bundles the auditor pipeline (Slither + solc) behind FastAPI.
# Build context is the REPO ROOT so it can copy both agent/ and backend/.
FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# default solc for analysis (single-file / flattened contracts)
RUN solc-select install 0.8.24 && solc-select use 0.8.24

COPY agent/ ./agent/
COPY backend/ ./backend/

ENV PORT=8000
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
