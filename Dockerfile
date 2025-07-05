FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

# Railway provides PORT environment variable
EXPOSE $PORT

# Use Railway's PORT environment variable
CMD ["sh", "-c", "gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app"]