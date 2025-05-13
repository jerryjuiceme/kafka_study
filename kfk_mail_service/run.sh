# !/bin/bash

set -a && source .env && set +a

uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8002 --workers 1
