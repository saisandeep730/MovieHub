from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.utils.enums import MovieStatus


class Movie(BaseModel):
    movie_id: str = Field(..., description="Permanent MovieHub ID, e.g. MH000001")
    title: str = Field(..., min_length=1)
    normalized_title: str = Field(..., min_length=1)
    year: int = Field(..., ge=1800, le=2100)
    poster_file_id: Optional[str] = None
    status: MovieStatus = MovieStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int = Field(..., description="Telegram user ID of the uploader")
