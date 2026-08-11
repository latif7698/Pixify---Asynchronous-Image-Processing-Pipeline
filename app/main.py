from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.database import Base, engine

# (Opsional di production, tapi berguna untuk development) 
# Otomatis membuat tabel di DB jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pixify Async Image Processing API",
    description="API for processing images asynchronously using FastAPI, Celery, and MinIO.",
    version="1.0.0"
)

# Daftarkan router
app.include_router(api_router, prefix="/api/v1")