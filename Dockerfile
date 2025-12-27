FROM python:3.11-slim

# Install system dependencies FIRST
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first (cache optimization)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy rest of code
COPY . .

EXPOSE 8080
CMD ["python3", "app.py"]
