FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

# Create a start script
RUN echo '#!/bin/bash\n\
PORT="${PORT:-8080}"\n\
echo "Starting server on port $PORT"\n\
exec gunicorn --workers 2 --bind "0.0.0.0:$PORT" app:app\n\
' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]