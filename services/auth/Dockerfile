FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy root shared and the service
COPY shared /app/shared
COPY services/auth /app/services/auth

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.auth.main:app", "--host", "0.0.0.0", "--port", "8000"]
