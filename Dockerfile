# Use the official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port (will be overridden by Railway)
EXPOSE ${PORT:-8001}

# Command to run the Chainlit application
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "${PORT:-8001}"]
