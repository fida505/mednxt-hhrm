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
from app.core.audit import log_audit
from fastapi import Request
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
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    emp_code = generate_employee_code(db, tenant_id)
    emp = Employee(**payload.model_dump(), employee_code=emp_code, tenant_id=tenant_id)
    db.add(emp)
    db.flush()
    log_audit(db, tenant_id, "employees", emp.id, "CREATE", user_role, payload.model_dump())
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
    page_size: int = Query(10, ge=1, le=1000),
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
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(emp, field, value)
    log_audit(db, tenant_id, "employees", emp.id, "UPDATE", user_role, payload.model_dump(exclude_none=True))
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{emp_id}", response_model=MessageResponse)
def delete_employee(
    emp_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_deleted = True
    log_audit(db, tenant_id, "employees", emp.id, "DELETE", user_role, {"is_deleted": True})
    db.commit()
    return MessageResponse(message="Employee soft deleted successfully", id=emp_id)


from fastapi import UploadFile, File
from fastapi.responses import Response
from app.models.document import EmployeeDocument
from app.schemas.document import DocumentOut
import os
import shutil

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

@router.post("/{emp_id}/documents", response_model=DocumentOut, status_code=201)
async def upload_employee_document(
    emp_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    user_role = request.headers.get("X-User-Role", "System")
    
    # Verify employee exists
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Read file bytes into memory (store in DB to handle Railway ephemeral FS)
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB allowed.")

    # Save to DB (also keep file_path as reference string)
    import uuid
    safe_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    
    doc = EmployeeDocument(
        tenant_id=tenant_id,
        employee_id=emp_id,
        filename=file.filename,
        file_path=safe_filename,  # just a reference name, not an actual disk path
        content_type=file.content_type,
        file_size=len(file_bytes),
        file_data=file_bytes,  # stored in DB
    )
    db.add(doc)
    db.flush()
    log_audit(db, tenant_id, "employee_documents", doc.id, "CREATE", user_role, {"filename": file.filename, "size": len(file_bytes)})
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{emp_id}/documents", response_model=list[DocumentOut])
def list_employee_documents(
    emp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    emp = db.query(Employee).filter(
        Employee.id == emp_id,
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    docs = db.query(EmployeeDocument).filter(
        EmployeeDocument.employee_id == emp_id,
        EmployeeDocument.tenant_id == tenant_id,
        EmployeeDocument.is_deleted == False
    ).all()
    return docs


@router.get("/{emp_id}/documents/{doc_id}/download")
def download_employee_document(
    emp_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Download a document - streams bytes stored in DB."""
    doc = db.query(EmployeeDocument).filter(
        EmployeeDocument.id == doc_id,
        EmployeeDocument.employee_id == emp_id,
        EmployeeDocument.tenant_id == tenant_id,
        EmployeeDocument.is_deleted == False,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.file_data:
        raise HTTPException(status_code=404, detail="File data not available")

    return Response(
        content=doc.file_data,
        media_type=doc.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )

