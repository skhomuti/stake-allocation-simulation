#!/usr/bin/env bash
set -euo pipefail

# Run the FastAPI app with auto-reload
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

