from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math

from app.database import get_db
from app.core.deps import get_tenant_id
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentOut
from app.schemas.common import PaginatedResponse, MessageResponse
from app.core.audit import log_audit
from fastapi import Request

router = APIRouter(prefix="/departments", tags=["Department Management"])


@router.post("", response_model=DepartmentOut, status_code=201)
def create_department(
    payload: DepartmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    dept = Department(**payload.model_dump(), tenant_id=tenant_id)
    db.add(dept)
    db.flush() # flush to get dept.id
    log_audit(db, tenant_id, "departments", dept.id, "CREATE", user_role, payload.model_dump())
    db.commit()
    db.refresh(dept)
    return dept


@router.get("", response_model=PaginatedResponse[DepartmentOut])
def list_departments(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    q = db.query(Department).filter(
        Department.tenant_id == tenant_id,
        Department.is_deleted == False,
    )
    if search:
        q = q.filter(or_(
            Department.name.ilike(f"%{search}%"),
            Department.code.ilike(f"%{search}%"),
        ))
    if status:
        q = q.filter(Department.status == status)

    total = q.count()
    items = q.order_by(Department.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
        items=items,
    )


@router.get("/{dept_id}", response_model=DepartmentOut)
def get_department(
    dept_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    dept = db.query(Department).filter(
        Department.id == dept_id,
        Department.tenant_id == tenant_id,
        Department.is_deleted == False,
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: str,
    payload: DepartmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    dept = db.query(Department).filter(
        Department.id == dept_id,
        Department.tenant_id == tenant_id,
        Department.is_deleted == False,
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(dept, field, value)
    log_audit(db, tenant_id, "departments", dept.id, "UPDATE", user_role, payload.model_dump(exclude_none=True))
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}", response_model=MessageResponse)
def delete_department(
    dept_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    dept = db.query(Department).filter(
        Department.id == dept_id,
        Department.tenant_id == tenant_id,
        Department.is_deleted == False,
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    dept.is_deleted = True
    log_audit(db, tenant_id, "departments", dept.id, "DELETE", user_role, {"is_deleted": True})
    db.commit()
    return MessageResponse(message="Department deleted successfully", id=dept_id)
