from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math

from app.database import get_db
from app.core.deps import get_tenant_id
from app.models.designation import Designation
from app.schemas.designation import DesignationCreate, DesignationUpdate, DesignationOut
from app.schemas.common import PaginatedResponse, MessageResponse

router = APIRouter(prefix="/designations", tags=["Designation Management"])


@router.post("", response_model=DesignationOut, status_code=201)
def create_designation(
    payload: DesignationCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    desig = Designation(**payload.model_dump(), tenant_id=tenant_id)
    db.add(desig)
    db.commit()
    db.refresh(desig)
    return desig


@router.get("", response_model=PaginatedResponse[DesignationOut])
def list_designations(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    q = db.query(Designation).filter(
        Designation.tenant_id == tenant_id,
        Designation.is_deleted == False,
    )
    if search:
        q = q.filter(or_(
            Designation.name.ilike(f"%{search}%"),
            Designation.code.ilike(f"%{search}%"),
        ))
    if status:
        q = q.filter(Designation.status == status)
    if grade:
        q = q.filter(Designation.grade == grade)

    total = q.count()
    items = q.order_by(Designation.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
        items=items,
    )


@router.get("/{desig_id}", response_model=DesignationOut)
def get_designation(
    desig_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    desig = db.query(Designation).filter(
        Designation.id == desig_id,
        Designation.tenant_id == tenant_id,
        Designation.is_deleted == False,
    ).first()
    if not desig:
        raise HTTPException(status_code=404, detail="Designation not found")
    return desig


@router.put("/{desig_id}", response_model=DesignationOut)
def update_designation(
    desig_id: str,
    payload: DesignationUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    desig = db.query(Designation).filter(
        Designation.id == desig_id,
        Designation.tenant_id == tenant_id,
        Designation.is_deleted == False,
    ).first()
    if not desig:
        raise HTTPException(status_code=404, detail="Designation not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(desig, field, value)
    db.commit()
    db.refresh(desig)
    return desig


@router.delete("/{desig_id}", response_model=MessageResponse)
def delete_designation(
    desig_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    desig = db.query(Designation).filter(
        Designation.id == desig_id,
        Designation.tenant_id == tenant_id,
        Designation.is_deleted == False,
    ).first()
    if not desig:
        raise HTTPException(status_code=404, detail="Designation not found")
    desig.is_deleted = True
    db.commit()
    return MessageResponse(message="Designation deleted successfully", id=desig_id)
