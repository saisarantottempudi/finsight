FROM python:3.12-slim
WORKDIR /ingestion
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "fetcher.py"]
