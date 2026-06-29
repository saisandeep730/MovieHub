from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MovieRequest(BaseModel):
    movie_name: str = Field(..., min_length=1)
    user_id: int
    username: str = ""
    count: int = Field(default=1, ge=1)
    fulfilled: bool = False
    fulfilled_movie_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
