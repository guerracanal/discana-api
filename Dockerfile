FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 --access-logfile - --error-logfile - wsgi:app