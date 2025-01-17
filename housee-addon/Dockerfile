FROM python:3.10-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Expose the port for the app
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
