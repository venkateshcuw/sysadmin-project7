# Pinned base image -- never "latest"
FROM python:3.11.9-slim-bookworm

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install dependencies BEFORE copying source (better layer caching, smaller rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy source code
COPY app.py .

# Drop privileges
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Real healthcheck using stdlib only (no curl needed -> smaller image)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]
