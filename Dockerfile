FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first
COPY requirements-prod.txt .

# Install Python dependencies with memory optimization
RUN pip install --no-cache-dir -r requirements-prod.txt \
    && rm -rf ~/.cache/pip

# Copy app code
COPY . .

# Create data folder
RUN mkdir -p data/articles

# Expose Streamlit port
EXPOSE 8501

# Set memory-efficient environment variables
ENV PYTHONUNBUFFERED=1
ENV MALLOC_TRIM_THRESHOLD_=100000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit with memory limits
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.maxUploadSize=5"]