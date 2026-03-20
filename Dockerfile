FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-create the instance directory so named volume inherits it with correct permissions
RUN mkdir -p /app/instance

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

EXPOSE 8000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "run:app"]
