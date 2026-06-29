from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class SettingsModel(BaseModel):
    key: str = Field(..., min_length=1)
    value: Any
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
