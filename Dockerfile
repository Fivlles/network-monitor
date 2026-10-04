FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Athens

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor.py .

CMD ["python", "monitor.py"]