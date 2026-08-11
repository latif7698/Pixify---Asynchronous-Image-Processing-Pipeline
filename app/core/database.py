import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

# Mengambil URL dari environment variable. 
# Format: postgresql://<user>:<password>@<host>:<port>/<db_name>
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/pixify_db"
)

try:
    # 1. Engine: "Mesin" utama yang berkomunikasi langsung dengan PostgreSQL
    engine = create_engine(DATABASE_URL, echo=False)

    # 2. SessionLocal: Pabrik (factory) untuk membuat sesi database baru setiap kali ada request
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 3. Base: Kelas induk untuk semua model database kita (seperti ImageJob)
    Base = declarative_base()
    
except Exception as e:
    logger.error(f"Gagal menghubungkan ke database: {e}")
    raise e