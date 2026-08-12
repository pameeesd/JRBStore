FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source and entrypoint
COPY src/ ./src/
COPY docker/entrypoint.sh /entrypoint.sh

# Collect static files (DEBUG=True generates a temporary ephemeral key for asset collection)
RUN DEBUG=True python src/manage.py collectstatic --noinput

# Create non-root user and persistent directories with proper permissions
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    mkdir -p /app/data /app/src/media && \
    chown -R appuser:appgroup /app/data /app/src/media /entrypoint.sh && \
    chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--chdir", "src", "jrbstore.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
