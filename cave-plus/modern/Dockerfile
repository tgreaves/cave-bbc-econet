FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/
COPY static/ ./static/
COPY rooms-parsed.yml .

EXPOSE 8000

CMD ["python3", "server/main.py"]
