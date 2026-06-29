from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class MovieFile(BaseModel):
    movie_id: str = Field(..., description="References Movie.movie_id")
    file_id: str = Field(..., description="Telegram file_id")
    file_unique_id: str = Field(..., description="Telegram file_unique_id")
    file_name: str = Field(..., min_length=1)
    file_size: int = Field(..., ge=0)
    quality: Optional[str] = None
    part: int = Field(default=0, ge=0)
    mime_type: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
