from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class JobResponse(BaseModel):
    id: UUID
    status: str
    original_filename: str
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    # Mengizinkan Pydantic untuk membaca data langsung dari model SQLAlchemy
    model_config = ConfigDict(from_attributes=True)