from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    head_employee_id: Optional[str] = None
    cost_center: Optional[str] = None
    budget_allocation: Optional[Decimal] = None
    status: Optional[str] = "ACTIVE"


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    head_employee_id: Optional[str] = None
    cost_center: Optional[str] = None
    budget_allocation: Optional[Decimal] = None
    status: Optional[str] = None


class DepartmentOut(DepartmentBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
