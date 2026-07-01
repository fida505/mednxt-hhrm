from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_tenant_id
from app.models.department import Department
from app.models.designation import Designation
from app.models.employee import Employee
from app.models.base import generate_uuid
from datetime import date

router = APIRouter(prefix="/seed", tags=["Seed Data"])

DEPARTMENTS = [
    {"name": "OPD", "code": "OPD", "cost_center": "CC-001", "description": "Out Patient Department"},
    {"name": "IPD", "code": "IPD", "cost_center": "CC-002", "description": "In Patient Department"},
    {"name": "Emergency", "code": "EMRG", "cost_center": "CC-003", "description": "Emergency & Trauma Care"},
    {"name": "ICU", "code": "ICU", "cost_center": "CC-004", "description": "Intensive Care Unit"},
    {"name": "NICU", "code": "NICU", "cost_center": "CC-005", "description": "Neonatal Intensive Care Unit"},
    {"name": "Operation Theatre", "code": "OT", "cost_center": "CC-006", "description": "Surgical Operations"},
    {"name": "Laboratory", "code": "LAB", "cost_center": "CC-007", "description": "Pathology & Diagnostics"},
    {"name": "Radiology", "code": "RAD", "cost_center": "CC-008", "description": "Imaging & Radiology"},
    {"name": "Pharmacy", "code": "PHRM", "cost_center": "CC-009", "description": "Pharmacy & Dispensary"},
    {"name": "HR", "code": "HR", "cost_center": "CC-010", "description": "Human Resources"},
    {"name": "Finance", "code": "FIN", "cost_center": "CC-011", "description": "Finance & Accounts"},
    {"name": "Biomedical", "code": "BIO", "cost_center": "CC-012", "description": "Biomedical Engineering"},
    {"name": "Housekeeping", "code": "HK", "cost_center": "CC-013", "description": "Housekeeping & Sanitation"},
]

DESIGNATIONS = [
    {"name": "Senior Consultant", "code": "SC", "grade": "Grade A"},
    {"name": "Consultant", "code": "CONS", "grade": "Grade A"},
    {"name": "Resident Doctor", "code": "RD", "grade": "Grade B"},
    {"name": "Duty Medical Officer", "code": "DMO", "grade": "Grade B"},
    {"name": "Junior Resident", "code": "JR", "grade": "Grade C"},
    {"name": "Head Nurse", "code": "HN", "grade": "Grade B"},
    {"name": "Staff Nurse", "code": "SN", "grade": "Grade C"},
    {"name": "Pharmacist", "code": "PHAR", "grade": "Grade C"},
    {"name": "Laboratory Technician", "code": "LT", "grade": "Grade C"},
    {"name": "Radiographer", "code": "RADG", "grade": "Grade C"},
    {"name": "Reception Executive", "code": "RE", "grade": "Grade D"},
    {"name": "HR Executive", "code": "HRE", "grade": "Grade D"},
    {"name": "Finance Executive", "code": "FE", "grade": "Grade D"},
]

EMPLOYEES = [
    {"first_name": "Dr. Arjun", "last_name": "Sharma", "email": "arjun.sharma@mednxt.com", "phone": "+91-9001234567", "gender": "MALE", "category": "DOCTOR", "qualification": "MBBS, MD", "specialty": "Cardiology", "experience_years": "12", "blood_group": "B+", "joining_date": "2020-01-15", "employment_status": "ACTIVE"},
    {"first_name": "Dr. Priya", "last_name": "Nair", "email": "priya.nair@mednxt.com", "phone": "+91-9001234568", "gender": "FEMALE", "category": "DOCTOR", "qualification": "MBBS, MS", "specialty": "Gynecology", "experience_years": "8", "blood_group": "A+", "joining_date": "2021-03-10", "employment_status": "ACTIVE"},
    {"first_name": "Rahul", "last_name": "Menon", "email": "rahul.menon@mednxt.com", "phone": "+91-9001234569", "gender": "MALE", "category": "NURSE", "qualification": "BSc Nursing", "specialty": "ICU Care", "experience_years": "5", "blood_group": "O+", "joining_date": "2022-06-01", "employment_status": "ACTIVE"},
    {"first_name": "Sneha", "last_name": "Kumar", "email": "sneha.kumar@mednxt.com", "phone": "+91-9001234570", "gender": "FEMALE", "category": "NURSE", "qualification": "GNM", "specialty": "Paediatrics", "experience_years": "3", "blood_group": "AB+", "joining_date": "2023-01-20", "employment_status": "ACTIVE"},
    {"first_name": "Anil", "last_name": "Verma", "email": "anil.verma@mednxt.com", "phone": "+91-9001234571", "gender": "MALE", "category": "PHARMACIST", "qualification": "B.Pharm", "specialty": "Clinical Pharmacy", "experience_years": "6", "blood_group": "O-", "joining_date": "2021-08-05", "employment_status": "ACTIVE"},
    {"first_name": "Divya", "last_name": "Pillai", "email": "divya.pillai@mednxt.com", "phone": "+91-9001234572", "gender": "FEMALE", "category": "LAB_STAFF", "qualification": "BMLT", "specialty": "Pathology", "experience_years": "4", "blood_group": "A-", "joining_date": "2022-09-12", "employment_status": "ACTIVE"},
    {"first_name": "Mohammed", "last_name": "Rizwan", "email": "m.rizwan@mednxt.com", "phone": "+91-9001234573", "gender": "MALE", "category": "DOCTOR", "qualification": "MBBS, DM", "specialty": "Neurology", "experience_years": "10", "blood_group": "B-", "joining_date": "2020-11-30", "employment_status": "ACTIVE"},
    {"first_name": "Anitha", "last_name": "George", "email": "anitha.george@mednxt.com", "phone": "+91-9001234574", "gender": "FEMALE", "category": "RECEPTIONIST", "qualification": "BBA", "specialty": "Patient Relations", "experience_years": "2", "blood_group": "AB-", "joining_date": "2023-07-01", "employment_status": "ACTIVE"},
    {"first_name": "Suresh", "last_name": "Babu", "email": "suresh.babu@mednxt.com", "phone": "+91-9001234575", "gender": "MALE", "category": "BIOMEDICAL_ENGINEER", "qualification": "BE Biomedical", "specialty": "Medical Equipment", "experience_years": "7", "blood_group": "O+", "joining_date": "2021-02-14", "employment_status": "ACTIVE"},
    {"first_name": "Fathima", "last_name": "Beevi", "email": "fathima.b@mednxt.com", "phone": "+91-9001234576", "gender": "FEMALE", "category": "HR_STAFF", "qualification": "MBA HR", "specialty": "Talent Acquisition", "experience_years": "5", "blood_group": "A+", "joining_date": "2022-04-01", "employment_status": "ACTIVE"},
]


@router.post("/demo-data")
def seed_demo_data(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Seed the database with sample departments, designations, and employees from the PDF spec."""

    # Check if already seeded
    existing = db.query(Department).filter(Department.tenant_id == tenant_id, Department.is_deleted == False).count()
    if existing > 0:
        return {"message": "Demo data already exists. Clear first or use fresh tenant.", "seeded": False}

    # Seed Departments
    dept_map = {}
    for d in DEPARTMENTS:
        dept = Department(**d, tenant_id=tenant_id, status="ACTIVE")
        db.add(dept)
        db.flush()
        dept_map[d["code"]] = dept.id

    # Seed Designations
    desig_map = {}
    for d in DESIGNATIONS:
        desig = Designation(**d, tenant_id=tenant_id, status="ACTIVE")
        db.add(desig)
        db.flush()
        desig_map[d["code"]] = desig.id

    # Seed Employees with department/designation links
    import random
    dept_ids = list(dept_map.values())
    desig_ids = list(desig_map.values())

    for i, e in enumerate(EMPLOYEES):
        e_copy = dict(e)
        e_copy["joining_date"] = date.fromisoformat(e["joining_date"])
        emp = Employee(
            **e_copy,
            department_id=dept_ids[i % len(dept_ids)],
            designation_id=desig_ids[i % len(desig_ids)],
            tenant_id=tenant_id,
        )
        db.add(emp)

    db.commit()
    return {
        "message": "Demo data seeded successfully!",
        "seeded": True,
        "departments": len(DEPARTMENTS),
        "designations": len(DESIGNATIONS),
        "employees": len(EMPLOYEES),
    }


@router.delete("/clear-data")
def clear_demo_data(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Soft-delete all records for this tenant (for resetting demo)."""
    db.query(Department).filter(Department.tenant_id == tenant_id).update({"is_deleted": True})
    db.query(Designation).filter(Designation.tenant_id == tenant_id).update({"is_deleted": True})
    db.query(Employee).filter(Employee.tenant_id == tenant_id).update({"is_deleted": True})
    db.commit()
    return {"message": "All demo data cleared!"}
