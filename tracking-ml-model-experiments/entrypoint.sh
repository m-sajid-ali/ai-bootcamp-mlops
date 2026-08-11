#!/usr/bin/env bash
set -e

# Allow access from other machines on the LAN (classroom demo).
# export MLFLOW_SERVER_ALLOWED_HOSTS="*"
# export MLFLOW_SERVER_CORS_ALLOWED_ORIGINS="*"

# Start the MLflow UI in the background (reads the SQLite DB in the mounted /workspace).
# mlflow ui \
#     --backend-store-uri sqlite:///mlflow.db \
#     --host 0.0.0.0 --port 5000 \
#     > /workspace/mlflow-ui.log 2>&1 &

# echo "MLflow UI starting on http://localhost:5000  (log: mlflow-ui.log)"
echo "Open a shell with:  docker compose exec lab bash"

# Keep the container alive as PID 1 so it stops cleanly.
exec sleep infinity