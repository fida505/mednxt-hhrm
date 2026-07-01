from sqlalchemy import Column, String
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Designation(Base, TimestampMixin):
    __tablename__ = "designations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    grade = Column(String(50), nullable=True)
    department_id = Column(String(36), nullable=True)
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)
