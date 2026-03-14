FROM python:3.10-slim

# Install system dependencies, specifically FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Render assigns a dynamic port via $PORT env var - we must use a shell form CMD to read it
EXPOSE 10000

# Use shell form (not exec form) so $PORT is expanded at runtime
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-10000}
