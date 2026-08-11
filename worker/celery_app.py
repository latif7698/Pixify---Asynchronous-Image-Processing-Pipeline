from celery import Celery
import os

# Idealnya diambil dari environment variables (nanti kita setup di config.py)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Inisialisasi Celery
celery_app = Celery(
    "image_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['worker.tasks'] # Memberitahu Celery di mana mencari task-nya
)

# Konfigurasi tambahan agar worker lebih stabil
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Jika task tidak selesai dalam 5 menit, batalkan (mencegah zombie worker)
    task_time_limit=300, 
)