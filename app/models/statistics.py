from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    key: str = Field(..., min_length=1)
    value: Any
    date: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
