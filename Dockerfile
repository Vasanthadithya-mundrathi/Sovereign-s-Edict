# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies for some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY backend/ ./backend
COPY data/ ./data

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "backend/main.py"]