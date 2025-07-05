FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

EXPOSE 8080

# Use direct command instead of script
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8080", "app:app"]