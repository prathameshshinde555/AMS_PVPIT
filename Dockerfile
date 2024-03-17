# Use an official Python runtime as a parent image
FROM python:3.9-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
        build-base \
        libpq \
        postgresql-dev \
    && rm -rf /var/cache/apk/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project into the container
COPY . /app/

# Create a non-root user
RUN addgroup appgroup && adduser -S appuser -G appgroup

# Change to the non-root user
USER appuser

# Expose the port the Django app runs on
EXPOSE 8000

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
