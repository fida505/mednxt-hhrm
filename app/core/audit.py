from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit(
    db: Session,
    tenant_id: str,
    table_name: str,
    record_id: str,
    action: str,
    changed_by: str = "System",
    details: dict = None
):
    """
    Helper function to log audit activities (CREATE, UPDATE, DELETE).
    """
    audit = AuditLog(
        tenant_id=tenant_id,
        table_name=table_name,
        record_id=record_id,
        action=action,
        changed_by=changed_by,
        details=details
    )
    db.add(audit)
    # We do not db.commit() here so it commits as part of the parent transaction
