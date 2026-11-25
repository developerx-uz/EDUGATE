from typing import Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User


def get_role_str(user: User) -> str:
    return str(user.role.value if hasattr(user.role, "value") else user.role)


async def record_audit(
    db: AsyncSession,
    user: Optional[User],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[str] = None,
    request: Optional[Request] = None,
    username_override: Optional[str] = None,
) -> None:
    """Persist an audit log entry without interrupting the main request if logging fails."""
    try:
        ip_addr = request.client.host if (request and request.client) else None
        entry = AuditLog(
            user_id=user.id if user else None,
            username=username_override or (user.username if user else "system"),
            role=get_role_str(user) if user else "SYSTEM",
            school_id=user.school_id if user else None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_addr,
        )
        db.add(entry)
    except Exception:
        pass
