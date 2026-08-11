import io
import logging
from PIL import Image
from sqlalchemy.orm import Session
from celery.exceptions import MaxRetriesExceededError

from worker.celery_app import celery_app

# Import dari folder app/core dan app/models yang benar
from app.core.database import SessionLocal 
from app.core.storage import s3_client, upload_file_to_storage
from app.models.job import ImageJob
from app.core.config import settings

# ... (lanjutan kode fungsi process_image_task tetap sama) ...
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_image_task(self, job_id: str, raw_object_name: str):
    """
    Task untuk mengunduh gambar dari MinIO, meresize-nya, dan mengunggah kembali.
    Menggunakan bind=True agar kita bisa memanggil self.retry jika gagal.
    """
    db: Session = SessionLocal()
    
    # 1. Ambil data job dari database
    job = db.query(ImageJob).filter(ImageJob.id == job_id).first()
    if not job:
        logger.error(f"Job {job_id} not found in database.")
        db.close()
        return

    try:
        # 2. Update status menjadi PROCESSING
        job.status = "PROCESSING"
        db.commit()
        logger.info(f"Starting process for job {job_id}")

        # 3. Download gambar dari MinIO ke Memory (RAM)
        # Kita menggunakan io.BytesIO sebagai "file bohongan" di memori
        image_stream = io.BytesIO()
        s3_client.download_fileobj(settings.BUCKET_NAME, raw_object_name, image_stream)
        image_stream.seek(0) # Kembalikan kursor ke awal file setelah di-download

        # 4. Proses gambar menggunakan Pillow (CPU-bound task)
        with Image.open(image_stream) as img:
            # Contoh: Resize gambar ke maksimal lebar/tinggi 800px sambil menjaga aspect ratio
            img.thumbnail((800, 800))
            
            # Simpan hasil proses ke memory (BytesIO) lain
            processed_stream = io.BytesIO()
            # Convert ke RGB untuk menghindari error jika gambar aslinya berformat RGBA (PNG transparan)
            if img.mode in ("RGBA", "P"): 
                img = img.convert("RGB")
                
            img.save(processed_stream, format="JPEG", quality=85)
            processed_stream.seek(0)

        # 5. Upload hasil kembali ke MinIO
        processed_object_name = f"processed/{job_id}.jpg"
        result_url = upload_file_to_storage(processed_stream, processed_object_name)

        # 6. Update database status ke COMPLETED
        job.status = "COMPLETED"
        job.result_url = result_url
        db.commit()
        logger.info(f"Successfully processed job {job_id}")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        # Rollback DB jika ada transaksi yang menggantung
        db.rollback() 
        
        try:
            # Retry mekanisme dengan exponential backoff (coba lagi setelah 10, 20, 40 detik)
            countdown = 10 * (2 ** self.request.retries)
            logger.info(f"Retrying task in {countdown} seconds...")
            raise self.retry(exc=e, countdown=countdown)
        except MaxRetriesExceededError:
            # Jika sudah retry 3x (max_retries=3) dan masih gagal, tandai sebagai FAILED (Dead Letter Queue concept)
            job.status = "FAILED"
            job.error_message = str(e)
            db.commit()
            logger.error(f"Job {job_id} permanently failed after max retries.")

    finally:
        # 7. Pastikan koneksi DB ditutup agar tidak terjadi "connection pool exhaustion"
        db.close()