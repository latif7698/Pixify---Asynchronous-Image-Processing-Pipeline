import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base # Asumsi kamu sudah punya setup Base declarative

class ImageJob(Base):
    __tablename__ = "image_jobs"

    # Menggunakan UUID yang di-generate otomatis
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Status job: PENDING, PROCESSING, COMPLETED, FAILED
    status = Column(String(20), default="PENDING", nullable=False, index=True)
    
    original_filename = Column(String(255), nullable=False)
    
    # URL hasil gambar, baru akan diisi oleh worker setelah selesai
    result_url = Column(String(500), nullable=True)
    
    # Menyimpan jejak error jika worker gagal memproses (sangat penting untuk debugging)
    error_message = Column(Text, nullable=True)
    
    # Timestamp untuk mengukur durasi atau membersihkan data lama
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)