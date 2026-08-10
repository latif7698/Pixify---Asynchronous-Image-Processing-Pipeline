#!/bin/bash

# ==========================================================
# Setup Struktur Project: project-v2
# FastAPI + Celery + Redis + PostgreSQL + MinIO/S3
# ==========================================================

set -e  # Hentikan script jika ada perintah yang gagal

PROJECT_NAME="project-v2"

echo "Membuat struktur folder untuk ${PROJECT_NAME}..."

# Buat root folder project
mkdir -p "${PROJECT_NAME}"
cd "${PROJECT_NAME}"

# --- app/ ---
mkdir -p app/api
mkdir -p app/core
mkdir -p app/models
mkdir -p app/schemas

touch app/__init__.py
touch app/api/__init__.py
touch app/api/endpoints.py

touch app/core/__init__.py
touch app/core/config.py
touch app/core/database.py
touch app/core/storage.py

touch app/models/__init__.py
touch app/models/job.py

touch app/schemas/__init__.py
touch app/schemas/job.py

touch app/main.py

# --- worker/ ---
mkdir -p worker
touch worker/__init__.py
touch worker/celery_app.py
touch worker/tasks.py

# --- File di root ---
touch docker-compose.yml
touch requirements.txt
touch .env
touch .gitignore

# Isi default .gitignore
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
.env
.pytest_cache/
*.egg-info/
EOF

echo ""
echo "Struktur folder berhasil dibuat:"
echo ""

# Tampilkan struktur folder hasil akhir
find . -not -path '*/\.git*' | sort | sed 's|[^/]*/|  |g'

echo ""
echo "Selesai. Masuk ke folder dengan: cd ${PROJECT_NAME}"