from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DocumentOut(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    filename: str
    file_path: str
    content_type: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
