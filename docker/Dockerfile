FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY src/ ./src/

# Collect static files (DEBUG=True generates a temporary ephemeral key for asset collection)
RUN DEBUG=True python src/manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "--chdir", "src", "jrbstore.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
