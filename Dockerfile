FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "run.py"]


# Dockerfile vs docker-compose.yml
# File                                 Purpose
# Dockerfile                Recipe for YOUR Flask app only
# docker-compose.yml        Manages BOTH Flask app + PostgreSQL together