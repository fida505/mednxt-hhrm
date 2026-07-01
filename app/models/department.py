from sqlalchemy import Column, String, Numeric
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    description = Column(String(500), nullable=True)
    head_employee_id = Column(String(36), nullable=True)
    cost_center = Column(String(50), nullable=True)       # Added from spec
    budget_allocation = Column(Numeric(15, 2), nullable=True) # Added from spec
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE / INACTIVE
