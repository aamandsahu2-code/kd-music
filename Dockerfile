FROM python:3.11-slim

# Install FFmpeg + system deps
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files
COPY . .

# Install Python deps
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port (Koyeb requirement)
EXPOSE 8080

# Start script
CMD ["bash", "start.sh"]

