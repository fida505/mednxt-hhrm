from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math

from app.database import get_db
from app.core.deps import get_tenant_id
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut
from app.schemas.common import PaginatedResponse, MessageResponse
import random

router = APIRouter(prefix="/employees", tags=["Employee Management"])


def generate_employee_code(db: Session, tenant_id: str):
    # Simplistic generation: EMP- + random 4 digits (in reality, could use a sequence table)
    # Just checking uniqueness
    while True:
        code = f"EMP-{random.randint(1000, 9999)}"
        exists = db.query(Employee).filter(Employee.employee_code == code, Employee.tenant_id == tenant_id).first()
        if not exists:
            return code


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    emp_code = generate_employee_code(db, tenant_id)
    emp = Employee(**payload.model_dump(), employee_code=emp_code, tenant_id=tenant_id)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("", response_model=PaginatedResponse[EmployeeOut])
def list_employees(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    department_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    q = db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
    )
    if search:
        q = q.filter(or_(
            Employee.first_name.ilike(f"%{search}%"),
            Employee.last_name.ilike(f"%{search}%"),
            Employee.employee_code.ilike(f"%{search}%"),
            Employee.email.ilike(f"%{search}%"),
        ))
    if category:
        q = q.filter(Employee.category == category)
    if department_id:
        q = q.filter(Employee.department_id == department_id)
    if status:
        q = q.filter(Employee.employment_status == status)

    total = q.count()
    items = q.order_by(Employee.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
        items=items,
    )


@router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(
    emp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{emp_id}", response_model=MessageResponse)
def delete_employee(
    emp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_deleted = True
    db.commit()
    return MessageResponse(message="Employee soft deleted successfully", id=emp_id)
