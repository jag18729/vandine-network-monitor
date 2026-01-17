FROM python:3.14-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY src/django_app/requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY src/django_app/ /app/

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Create entrypoint script
RUN echo '#!/bin/sh\n\
\n\
echo "Waiting for postgres..."\n\
while ! nc -z postgres 5432; do\n\
  sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
\n\
echo "Waiting for redis..."\n\
while ! nc -z redis 6379; do\n\
  sleep 0.1\n\
done\n\
echo "Redis started"\n\
\n\
python manage.py collectstatic --noinput\n\
python manage.py migrate\n\
\n\
exec "$@"' > /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000