FROM python:3.11-slim

# System deps for MCP stdio servers
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Runtime directories (overridden by volumes in compose)
RUN mkdir -p sessions queue workspace

# Default: run the production gateway
CMD ["python", "sessions/en/s05_gateway.py"]
