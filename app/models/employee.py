from sqlalchemy import Column, String, Date, Text
from app.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_code = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    gender = Column(String(10), nullable=True)       # MALE / FEMALE / OTHER
    date_of_birth = Column(Date, nullable=True)
    blood_group = Column(String(5), nullable=True)
    address = Column(Text, nullable=True)

    # Employment info
    category = Column(String(50), nullable=True)     # DOCTOR / NURSE / etc.
    department_id = Column(String(36), nullable=True)
    designation_id = Column(String(36), nullable=True)
    reporting_manager_id = Column(String(36), nullable=True)
    joining_date = Column(Date, nullable=True)
    employment_status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE / INACTIVE / RESIGNED

    # Professional info
    qualification = Column(String(200), nullable=True)
    experience_years = Column(String(10), nullable=True)
    specialty = Column(String(100), nullable=True)
    sub_specialty = Column(String(100), nullable=True)

    profile_photo_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
