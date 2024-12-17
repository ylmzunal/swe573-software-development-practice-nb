# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DOCKER_BUILD 0
ENV CLOUD_RUN 1
ENV SECRET_KEY="django-insecure-)ww=s(l-)=r&0z1pr$i9$h81-dr%83ok#1=wiww2ronzo$j)co"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn eureka_nexus.wsgi:application --bind 0.0.0.0:$PORT 