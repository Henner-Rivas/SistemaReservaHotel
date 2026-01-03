FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY shared /app/shared
COPY services/reservations /app/services/reservations

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.reservations.main:app", "--host", "0.0.0.0", "--port", "8000"]
