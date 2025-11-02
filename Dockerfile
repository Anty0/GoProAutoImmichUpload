# Minimal runtime image for GoPro Immich Uploader
# BlueZ is expected to run on the host; we only talk to it over the system D-Bus

FROM docker.io/library/python:3.13.7-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first for better build caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENTRYPOINT ["/usr/local/bin/python", "-m", "gopro_immich_uploader"]
CMD ["run"]
