# Use a base image
FROM alpine:3.17

# Install necessary dependencies
RUN apk add --no-cache \
    bash \
    curl \
    python3 \
    py3-pip \
    && pip install flask requests

# Set working directory
WORKDIR /app

# Copy the add-on files
COPY run.sh /app/run.sh

# Ensure the script is executable
RUN chmod +x /app/run.sh

# Set the default command
CMD ["/app/run.sh"]
