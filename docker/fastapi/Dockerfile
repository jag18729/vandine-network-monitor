FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    nmap \
    iperf3 \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY src/fastapi_app/requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY src/fastapi_app/ /app/

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Waiting for postgres..."\n\
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do\n\
  sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
\n\
echo "Waiting for redis..."\n\
while ! nc -z $REDIS_HOST $REDIS_PORT; do\n\
  sleep 0.1\n\
done\n\
echo "Redis started"\n\
\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Expose port
EXPOSE 8001

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]