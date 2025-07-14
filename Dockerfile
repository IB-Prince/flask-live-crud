FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

# Use shell form CMD and hardcode port 8080 to avoid $PORT issues on Railway
EXPOSE 8080
CMD gunicorn --workers 2 --bind 0.0.0.0:8080 app:app