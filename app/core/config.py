import os
from dotenv import load_dotenv

# Mencari dan memuat file .env yang ada di root folder proyek
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Pixify Async Image Processing API"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgrespassword@localhost:5432/pixify_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL")
    
    # MinIO / S3
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME")

    def __init__(self):
        if not self.MINIO_ACCESS_KEY or not self.MINIO_SECRET_KEY:
            raise RuntimeError("CRITICAL ERROR: MINIO_ACCESS_KEY / MINIO_SECRET_KEY wajib di-set di file .env")

# Inisiasi object settings agar bisa di-import oleh file lain
settings = Settings()