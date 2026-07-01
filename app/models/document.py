from sqlalchemy import Column, String, ForeignKey, LargeBinary, BigInteger
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid

class EmployeeDocument(Base, TimestampMixin):
    __tablename__ = "employee_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    employee_id = Column(String(36), ForeignKey("employees.id"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    # Store file bytes in DB to avoid ephemeral filesystem issues on Railway
    file_data = Column(LargeBinary, nullable=True)

