from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import uuid

# Import setup kita sebelumnya
from app.core.database import SessionLocal
from app.core.storage import upload_file_to_storage
from app.models.job import ImageJob
from worker.tasks import process_image_task
from app.schemas.job import JobResponse

router = APIRouter()

# Dependency: Membuat session DB yang aman (otomatis close setelah request selesai)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# ENDPOINT 1: UPLOAD GAMBAR & TRIGGER CELERY
# ---------------------------------------------------------
@router.post(
    "/images/process", 
    response_model=JobResponse, 
    status_code=status.HTTP_202_ACCEPTED
)
async def upload_image_for_processing(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Menerima file gambar, menyimpan file mentah ke MinIO, 
    membuat record di DB, dan men-trigger Celery worker.
    """
    # 1. Validasi tipe file (Security best practice)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # 2. Upload file mentah ke MinIO
    # Kita buat nama file unik (UUID) di MinIO untuk menghindari bentrok jika ada file bernama sama
    raw_object_name = f"raw/{uuid.uuid4()}_{file.filename}"
    upload_file_to_storage(file.file, raw_object_name)

    # 3. Buat record di Database dengan status PENDING
    new_job = ImageJob(
        original_filename=file.filename,
        status="PENDING"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job) # Untuk mendapatkan ID UUID yang di-generate oleh DB

    # 4. Trigger Celery Task (Asynchronous)
    # Ini yang membuat API kita sangat cepat. Kita tidak menunggu file di-resize.
    # Kita hanya mengirim pesan ke Redis: "Tolong proses job_id ini!"
    process_image_task.delay(str(new_job.id), raw_object_name)

    # 5. Kembalikan response 202 Accepted ke user
    return new_job


# ---------------------------------------------------------
# ENDPOINT 2: CEK STATUS (POLLING)
# ---------------------------------------------------------
@router.get(
    "/jobs/{job_id}", 
    response_model=JobResponse
)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Endpoint untuk klien mengecek apakah gambarnya sudah selesai diproses.
    """
    try:
        # Validasi format UUID
        valid_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Job ID format.")

    # Query ke database
    job = db.query(ImageJob).filter(ImageJob.id == valid_uuid).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return job