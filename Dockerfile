FROM python:3.11

WORKDIR /app

# Install system dependencies (Fix for libGL error)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data/articles
RUN chmod -R 777 /app

CMD ["python", "main.py"]