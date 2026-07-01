import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class RBACMiddleware(BaseHTTPMiddleware):
    """
    Role-Based Access Control (RBAC) Middleware.
    Enforces that only users with 'ADMIN' or 'HR' roles can perform write operations (POST, PUT, DELETE).
    Users with 'VIEWER' role can only perform read operations (GET).
    """
    async def dispatch(self, request: Request, call_next):
        # We only apply RBAC to the API routes, not static files or docs
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Skip RBAC for preflight CORS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Retrieve the user's role from headers (Defaulting to ADMIN for ease of use in UI if not provided)
        # In a real app, this would come from a verified JWT token.
        user_role = request.headers.get("X-User-Role", "ADMIN").upper()
        
        # Define allowed write roles
        write_roles = {"ADMIN", "HR"}
        
        # Check permissions
        if request.method in ["POST", "PUT", "DELETE"]:
            if user_role not in write_roles:
                logger.warning(f"Access Denied: User role '{user_role}' attempted a {request.method} operation.")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Forbidden: You do not have permission to perform this action. Role required: ADMIN or HR."}
                )

        # Process the request if authorized
        response = await call_next(request)
        return response
