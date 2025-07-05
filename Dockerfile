FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

EXPOSE 8080

# Create a startup script to handle port properly
RUN echo '#!/bin/bash\n\
# Set default port if PORT is not set\n\
if [ -z "$PORT" ]; then\n\
    export PORT=8080\n\
fi\n\
echo "Starting gunicorn on port $PORT"\n\
exec gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app' > /start.sh

RUN chmod +x /start.sh

CMD ["/start.sh"]