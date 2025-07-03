# ─── Stage 1: Builder ─────────────────────────────────────
FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential gcc libglib2.0-0 libgomp1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# ─── Stage 2: Runtime ─────────────────────────────────────
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set persistent model cache paths
ENV HF_HOME=/cache/huggingface \
    TORCH_HOME=/cache/torch \
    SENTENCE_TRANSFORMERS_HOME=/cache/sentence-transformers \
    MODEL_CACHE_DIR=/home/appuser/model_storage

# Security: run as non-root user
RUN useradd -m appuser

# Create cache and model storage directories and set permissions
RUN mkdir -p /cache /home/appuser/model_storage && chown -R appuser:appuser /cache /home/appuser/model_storage

WORKDIR /home/appuser

# Copy built wheels and install dependencies
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels

# Copy application code (excluding unnecessary files)
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser .env* ./
COPY --chown=appuser:appuser migration.sql ./

# Create necessary directories for the app
RUN mkdir -p app/static app/templates

# Optional: Preload model during build (uncomment if you want to cache model in image)
# RUN python app/preload_model.py

# Use non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/')" || exit 1

# Entrypoint to your app
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
