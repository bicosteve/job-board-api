# syntax=docker/dockerfile:1

# Stage 1: builder - compile wheels for all python dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Build-time dependencies needed to compile some wheels (mysqlclient, cffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Build wheels for all requirements so the final image stays slim
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt



# Stage 2: runtime - minimal image that only contains what is needed to run

FROM python:3.12-slim AS runtime

# Build-time args
ARG APP_PORT=5005

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=${APP_PORT} \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    HEALTHCHECK_PATH=/v0/api/health/check

WORKDIR /app

# Runtime-only OS dependencies (no compilers in the final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python deps from the pre-built wheels
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy the application source
COPY . .

# Create and switch to a non-root user for security
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Document the port the container listens on
EXPOSE ${PORT}

# Basic container healthcheck against the app's health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; path=os.environ.get('HEALTHCHECK_PATH','/v1/api/health/check'); sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','5005')+path, timeout=4).status==200 else sys.exit(1)" || exit 1

# Run the app with gunicorn (production WSGI server).
# run.py exposes the Flask app instance as `app`.
CMD ["sh", "-c", "gunicorn --bind ${HOST}:${PORT} --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - run:app"]
