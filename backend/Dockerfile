FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment variables for Dapr sidecar compatibility
ENV PORT=8000
ENV HOST=0.0.0.0
# Dapr will inject these at runtime:
# - DAPR_HTTP_PORT: Dapr sidecar HTTP port (default 3500)
# - DAPR_GRPC_PORT: Dapr sidecar gRPC port (default 50001)

# Expose the application port
# Note: Dapr sidecar runs on ports 3500 (HTTP) and 50001 (gRPC)
EXPOSE 8000

# Health check for Kubernetes liveness/readiness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the FastAPI application with uvicorn
# For local dev (Hugging Face): python main.py
# For Kubernetes: uvicorn for better control
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
