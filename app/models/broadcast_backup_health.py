from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.utils.enums import HealthStatus


class Broadcast(BaseModel):
    broadcast_id: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(text|photo|video|document|forward|copy)$")
    content: dict = Field(default_factory=dict)
    status: str = Field(default="pending")
    total_users: int = 0
    success_count: int = 0
    fail_count: int = 0
    created_by: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class Backup(BaseModel):
    backup_id: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(settings|full|scheduled)$")
    status: str = Field(default="pending")
    file_id: Optional[str] = None
    file_size: int = 0
    created_by: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class HealthCheck(BaseModel):
    check_id: str = Field(..., min_length=1)
    component: str = Field(..., pattern="^(bot|mongodb|telegram|database_channel|redirect_server)$")
    status: HealthStatus = HealthStatus.HEALTHY
    message: str = ""
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
