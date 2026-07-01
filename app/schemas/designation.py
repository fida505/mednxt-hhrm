from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DesignationBase(BaseModel):
    name: str
    code: Optional[str] = None
    grade: Optional[str] = None
    department_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    grade: Optional[str] = None
    department_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DesignationOut(DesignationBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
