from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    reporting_manager_id: Optional[str] = None
    joining_date: Optional[date] = None
    employment_status: Optional[str] = "ACTIVE"
    qualification: Optional[str] = None
    experience_years: Optional[str] = None
    specialty: Optional[str] = None
    sub_specialty: Optional[str] = None
    profile_photo_url: Optional[str] = None
    notes: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    reporting_manager_id: Optional[str] = None
    joining_date: Optional[date] = None
    employment_status: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[str] = None
    specialty: Optional[str] = None
    sub_specialty: Optional[str] = None
    profile_photo_url: Optional[str] = None
    notes: Optional[str] = None


class EmployeeOut(EmployeeBase):
    id: str
    employee_code: Optional[str] = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
