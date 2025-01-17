FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Expose the port for Flask
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
