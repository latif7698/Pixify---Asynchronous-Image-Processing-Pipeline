import boto3
from botocore.exceptions import ClientError
import logging

# IMPORT DARI CONFIG.PY
from app.core.config import settings

logger = logging.getLogger(__name__)

# Inisialisasi S3 Client menggunakan object settings
s3_client = boto3.client(
    's3',
    endpoint_url=settings.MINIO_ENDPOINT,
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
    region_name='us-east-1' 
)

def upload_file_to_storage(file_obj, destination_path: str) -> str:
    """
    Mengunggah file ke MinIO/S3 dan mengembalikan public URL.
    file_obj bisa berupa file dari FastAPI (UploadFile.file) atau file dari disk lokal worker.
    """
    try:
        s3_client.upload_fileobj(
            file_obj,
            settings.BUCKET_NAME,
            destination_path,
            ExtraArgs={'ACL': 'public-read'} # Asumsi kita ingin hasilnya bisa diakses langsung via URL
        )
        
        # Format URL MinIO: http://<endpoint>/<bucket_name>/<file_path>
        file_url = f"{settings.MINIO_ENDPOINT}/{settings.BUCKET_NAME}/{destination_path}"
        return file_url
        
    except ClientError as e:
        logger.error(f"Failed to upload to MinIO: {e}")
        raise e