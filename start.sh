#!/bin/bash

# Startup script for the Purabali application
# This script can preload the model and start the application

set -e

echo "Starting Purabali application..."

# Check if we should preload the model
if [ "${PRELOAD_MODEL:-false}" = "true" ]; then
    echo "Preloading model..."
    python app/preload_model.py
    echo "Model preloading completed."
else
    echo "Skipping model preloading (set PRELOAD_MODEL=true to enable)"
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 