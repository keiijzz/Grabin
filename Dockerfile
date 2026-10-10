# Jalanin grabin via Docker (opsional, buat yang suka container).
FROM python:3.12-slim

# ffmpeg wajib buat merge video+audio yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

VOLUME ["/app/downloads"]
ENTRYPOINT ["python", "-m", "grabin"]
CMD ["--help"]
