# Use the official Python image
FROM python:3.12.8-slim

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies, including git
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Copy the specific airflow.cfg file into the container
COPY airflow.cfg $AIRFLOW_HOME/airflow.cfg


# Set permissions for entrypoint script
RUN chmod +x entrypoint.sh

# Expose ports
# 8080 for Airflow, 8050 for the dashboard, 8000 for the docs
EXPOSE 8080 8050 8000

# Start the application using the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]