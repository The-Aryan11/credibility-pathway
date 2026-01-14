FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data/articles && chmod -R 777 data
EXPOSE 7860
CMD ["python", "main.py"]