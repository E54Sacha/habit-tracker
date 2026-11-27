# The API image: the same one runs locally, in CI and on Render.
FROM python:3.12-slim

# No .pyc files, logs printed straight away (visible in Render's logs).
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencies first: this layer is reused as long as requirements.txt doesn't change.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

# Don't run as root inside the container.
RUN useradd --create-home --uid 10001 api
USER api

# Render sets $PORT. Migrations run before every start, so the database is always up to date.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'"]
