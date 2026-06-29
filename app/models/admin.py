from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.utils.enums import UserRole


class Admin(BaseModel):
    user_id: int
    username: str = ""
    added_by: int = 0
    role: UserRole = UserRole.ADMIN
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
