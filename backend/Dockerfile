FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

# Create directory for Vosk model
RUN mkdir -p /vosk/model

EXPOSE 5000

CMD ["python", "main.py"] 