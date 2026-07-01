from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import generate_uuid

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    tenant_id = Column(String(36), index=True, nullable=False)
    
    table_name = Column(String(100), index=True, nullable=False)
    record_id = Column(String(36), index=True, nullable=False)
    action = Column(String(20), nullable=False) # CREATE, UPDATE, DELETE
    
    changed_by = Column(String(100), nullable=True) # e.g., the User Role or ID if we had auth
    
    # Store changes or full snapshot as JSON (using JSONB for Postgres)
    details = Column(JSONB, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
