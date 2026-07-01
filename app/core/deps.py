from fastapi import Header
from app.core.config import settings


async def get_tenant_id(x_tenant_id: str = Header(default=None)) -> str:
    """Extract tenant_id from request header. Falls back to default tenant."""
    return x_tenant_id or settings.DEFAULT_TENANT_ID
