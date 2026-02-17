# ProofSAR AI Enterprise Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY demo_data/ ./demo_data/

# Create necessary directories
RUN mkdir -p logs exports

# Expose ports
EXPOSE 8000 8501

# Create startup script
COPY <<EOF /app/start.sh
#!/bin/bash
echo "Starting ProofSAR AI Backend..."
cd backend && python main.py &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 5

echo "Starting ProofSAR AI Frontend..."
cd ../frontend && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo "ProofSAR AI is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"

# Wait for processes
wait \$BACKEND_PID \$FRONTEND_PID
EOF

RUN chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["/app/start.sh"]
