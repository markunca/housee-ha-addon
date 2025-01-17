FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY proxy/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY proxy/ .

CMD ["python", "app.py"]
