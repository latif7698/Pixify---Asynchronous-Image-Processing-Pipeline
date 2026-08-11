# Menggunakan image base Linux yang ringan (slim) agar ukuran container tidak bengkak
FROM python:3.12-slim

# Mencegah Python menulis file .pyc ke disk dan membiarkan output stdout/stderr tampil langsung di log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies yang mungkin dibutuhkan oleh library seperti Pillow atau psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy hanya requirements terlebih dahulu untuk memanfaatkan Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy sisa kode aplikasi
COPY . .