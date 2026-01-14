FROM python:3.11

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code
COPY . .

# Create data directory with permissions
RUN mkdir -p data/articles && chmod -R 777 data

# Expose HF Port
EXPOSE 7860

# Run API
CMD ["python", "main.py"]